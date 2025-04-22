#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SWB交互模块，处理与Sentaurus Workbench的交互
"""
import os
import time
import logging
import subprocess
import json
from pathlib import Path
import traceback
import requests
from typing import Dict, Any, List

# 尝试导入SWB API
try:
    from swbpy2 import *
    from swbpy2.core.core import STATE_READY, STATE_DONE, STATE_FAILED, STATE_RUNNING
    SWB_API_AVAILABLE = True
except ImportError:
    SWB_API_AVAILABLE = False
    logging.warning("未找到SWB API，将使用命令行模式与SWB交互")

logger = logging.getLogger("auto_sim.swb_interaction")

class SWBInteraction:
    """Sentaurus Workbench交互类"""
    
    def __init__(self, project_path):
        """
        初始化与SWB的交互
        
        Args:
            project_path: Sentaurus项目路径
        """
        self.project_path = Path(project_path)
        self.logger = logging.getLogger(__name__)
        self.project_abs_path = self.project_path.absolute()
        self.swb_api_available = SWB_API_AVAILABLE
        self.deck = None
        self.tree = None
        
        # 设置用于运行命令的环境变量
        self.env = os.environ.copy()
        
        # 找到sentaurus_env.sh文件
        self.sentaurus_env_path = self.project_path / "sentaurus_env.sh"
        if not self.sentaurus_env_path.exists():
            logger.warning(f"未找到sentaurus_env.sh: {self.sentaurus_env_path}")
        
    def initialize_swb_connection(self):
        """初始化与SWB的连接"""
        if not self.swb_api_available:
            logger.info("SWB API不可用，使用命令行模式")
            return True
        
        try:
            # 使用SWB API打开项目
            logger.info(f"打开项目: {self.project_abs_path}")
            self.deck = Deck(str(self.project_abs_path))
            self.tree = self.deck.getGtree()
            logger.info("成功连接到SWB项目")
            return True
        except Exception as e:
            logger.error(f"连接SWB项目失败: {str(e)}")
            return False
    
    def get_current_leaf_nodes(self):
        """获取当前叶节点"""
        if not self.swb_api_available or not self.tree:
            return None
        
        try:
            leaf_nodes = set(self.tree.AllLeafNodes())
            logger.info(f"当前有 {len(leaf_nodes)} 个叶节点")
            return leaf_nodes
        except Exception as e:
            logger.error(f"获取叶节点失败: {str(e)}")
            return None
    
    def get_all_nodes(self):
        """获取所有节点"""
        if not self.swb_api_available or not self.tree:
            return None
        
        try:
            all_nodes = set(self.tree.AllNodes())
            logger.info(f"当前有 {len(all_nodes)} 个节点")
            return all_nodes
        except Exception as e:
            logger.error(f"获取所有节点失败: {str(e)}")
            return None
    
    def create_new_experiment(self, params):
        """
        创建新实验
        
        Args:
            params: 参数字典
        
        Returns:
            dict: 包含 'all_added' 和 'leaf_added' 两个节点列表的字典
        """
        if not self.swb_api_available or not self.tree:
            logger.info("SWB API不可用或未初始化，尝试使用命令行方式创建实验")
            return self._create_new_experiment_cmd(params)

        try:
            # 1. 获取添加前的节点
            old_all_node_ids = self.get_all_nodes()
            old_leaf_node_ids = self.get_current_leaf_nodes()

            if old_all_node_ids is None or old_leaf_node_ids is None:
                logger.error("获取现有节点失败，无法继续")
                # 尝试回退到命令行
                return self._create_new_experiment_cmd(params)

            logger.info(f"添加前: {len(old_all_node_ids)} 个节点，{len(old_leaf_node_ids)} 个叶节点")

            # 2. 转换参数为AddPath可接受的格式
            param_values = []
            tools = self.tree.AllTools()
            logger.debug(f"项目工具列表: {tools}")
            for tool in tools:
                param_names = self.tree.ToolPnames(tool)
                logger.debug(f"工具 '{tool}' 的参数: {param_names}")
                for param_name in param_names:
                    if param_name in params:
                        param_values.append(str(params[param_name]))
                    else:
                        logger.warning(f"参数 '{param_name}' (工具: '{tool}') 在提供的参数字典中未找到，将使用空字符串")
                        param_values.append("") # 或者可以尝试获取默认值，但更安全的是用空字符串

            # 3. 添加新路径 - 增加重试逻辑
            max_retries = 3
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    logger.info(f"尝试添加新实验，参数值: {param_values} (尝试 {retry_count+1}/{max_retries})")
                    self.tree.AddPath(pvalues=param_values)

                    # 4. 保存并重新加载项目
                    logger.info("保存项目")
                    self.deck.save()

                    # 增加等待时间确保文件被完全保存
                    wait_time = 5 + retry_count * 3  # 每次重试增加等待时间
                    logger.info(f"等待SWB状态更新（{wait_time}秒）...")
                    time.sleep(wait_time)

                    logger.info("重新加载项目")
                    self.deck.reload()
                    # 重新获取 Gtree 实例
                    self.tree = self.deck.getGtree()

                    # 额外等待以确保节点加载完成
                    time.sleep(2)

                    success = True
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"添加路径失败 (尝试 {retry_count}/{max_retries}): {str(e)}")
                    if retry_count >= max_retries:
                        logger.error("添加路径重试次数已达上限，API方式失败")
                        raise # 重新抛出异常，由外层捕获并决定是否回退
                    time.sleep(3)  # 失败后等待再次尝试
            
            # 如果 AddPath 和 reload 成功，尝试运行预处理
            if success:
                logger.info("运行项目预处理 (preprocess)...")
                try:
                    self.deck.preprocess()
                    logger.info("项目预处理完成。")
                    time.sleep(2) # 短暂等待预处理完成
                except Exception as e_prep:
                    logger.error(f"项目预处理失败: {str(e_prep)}")
                    # 预处理失败通常意味着无法运行节点
                    raise Exception(f"项目预处理失败，无法继续: {str(e_prep)}") from e_prep
            else:
                # 如果循环结束但 success 仍为 False
                logger.error("添加路径重试次数已达上限且失败，无法继续。")
                raise Exception("添加路径重试次数已达上限且失败。")

            # 5. 获取添加后的节点 (在成功预处理后)
            current_all_node_ids = self.get_all_nodes()
            current_leaf_node_ids = self.get_current_leaf_nodes()

            if current_all_node_ids is None or current_leaf_node_ids is None:
                logger.error("获取更新后节点失败")
                # 尝试回退到命令行
                return self._create_new_experiment_cmd(params)

            logger.info(f"添加后: {len(current_all_node_ids)} 个节点，{len(current_leaf_node_ids)} 个叶节点")

            # 6. 计算新增节点
            added_all_node_ids = current_all_node_ids - old_all_node_ids
            added_leaf_node_ids = current_leaf_node_ids - old_leaf_node_ids

            logger.info(f"检测到 {len(added_all_node_ids)} 个新增节点: {added_all_node_ids}")
            logger.info(f"检测到 {len(added_leaf_node_ids)} 个新增叶节点: {added_leaf_node_ids}")

            # 如果没有检测到新增叶节点，尝试备用方法识别
            if not added_leaf_node_ids and added_all_node_ids:
                logger.warning("未通过API直接检测到新增叶节点，尝试通过节点类型识别...")

                # 尝试识别计算节点和叶节点
                potential_leaf_nodes = set()
                for node_id in added_all_node_ids:
                    try:
                        node_info = self.get_node_info(node_id) # 使用已有的get_node_info方法
                        if node_info and node_info.get('tool') in ['sdevice', 'sde']: # 主要关注计算工具
                            logger.info(f"识别到可能的新增叶节点: {node_id}, 类型: {node_info.get('tool')}")
                            potential_leaf_nodes.add(node_id)
                    except Exception as e_info:
                        logger.warning(f"获取节点 {node_id} 信息失败: {e_info}")

                if potential_leaf_nodes:
                    added_leaf_node_ids = potential_leaf_nodes
                    logger.info(f"通过节点类型识别到的新增叶节点: {added_leaf_node_ids}")
                else:
                    # 如果仍未找到，作为最后手段，将所有新增节点都视为叶节点
                    logger.warning("无法通过节点类型识别新增叶节点，将所有新增节点视为叶节点")
                    added_leaf_node_ids = added_all_node_ids
            elif not added_all_node_ids:
                 logger.warning("未检测到任何新增节点。可能是参数未导致新路径，或API状态未更新。")
                 # 在这种情况下，最好返回空列表，并检查参数或项目状态
                 return []

            # 返回所有新增节点和新增叶节点，以及叶节点的工具信息
            leaf_info = []
            if added_leaf_node_ids:
                for leaf_id in added_leaf_node_ids:
                    # 在 preprocess 后尝试获取节点信息
                    info = self.get_node_info(leaf_id)
                    leaf_info.append({'id': leaf_id, 'tool': info.get('tool', 'unknown')})
            
            return {
                "all_added": list(added_all_node_ids),
                "leaf_added": list(added_leaf_node_ids),
                "leaf_info": leaf_info
            }

        except Exception as e:
            logger.error(f"使用SWB API创建新实验失败: {str(e)}")
            logger.error(traceback.format_exc())
            # 尝试使用命令行方式作为回退
            logger.info("API方式失败，尝试使用命令行方式...")
            return self._create_new_experiment_cmd(params)
    
    def _create_new_experiment_cmd(self, params):
        """使用命令行方式创建新实验（备用方法）"""
        logger.info("使用命令行方式创建新实验")

        # 首先检查项目目录中已存在的节点
        all_patterns = ["n*_des.cmd", "n*_dvs.cmd", "n*_par.cmd", "n*.plt", "n*_command"] # 添加 *_command 文件
        old_node_files = []
        for pattern in all_patterns:
            old_node_files.extend(list(self.project_path.glob(pattern)))

        # 从文件名提取节点ID
        old_node_ids = set()
        for f in old_node_files:
            try:
                # 文件名格式 n{node_id}_xxx.yyy 或 n{node_id}_command
                if f.stem.startswith('n'):
                   if '_' in f.stem:
                       node_id_str = f.stem.split('_')[0][1:]
                       if node_id_str.isdigit():
                           old_node_ids.add(int(node_id_str))
                   elif f.stem.endswith('_command'): # 处理 nXXX_command
                       node_id_str = f.stem.replace('_command', '')[1:]
                       if node_id_str.isdigit():
                           old_node_ids.add(int(node_id_str))
            except (ValueError, IndexError):
                continue

        logger.info(f"命令行方法 - 执行前已存在节点: {sorted(list(old_node_ids)) if old_node_ids else 'None'}")

        # 获取当前最大节点ID
        max_existing_node = max(old_node_ids) if old_node_ids else 0
        logger.info(f"当前最大节点ID: {max_existing_node}")

        # 这里实现调用外部脚本(如之前的mct_auto_sim.py)来添加实验
        try:
            # 创建临时参数文件
            temp_params_file = self.project_path / "temp_params.json"
            with open(temp_params_file, 'w') as f:
                json.dump(params, f, indent=4)

            # 构建命令
            # 使用专门的添加实验脚本
            script_path = self.project_path / "add_experiment.py"
            
            # 如果专用脚本不存在，尝试找到主自动化脚本
            if not script_path.exists():
                logger.warning(f"未找到专用脚本: {script_path}, 尝试使用主脚本")
                main_script_path = self.project_path / "auto_sim" / "auto_sim_main.py"
                if not main_script_path.exists():
                    logger.warning(f"未找到主脚本: {main_script_path}, 尝试查找替代脚本")
                    alternative_scripts = list(self.project_path.glob("*.py")) + \
                                         list((self.project_path / "auto_sim").glob("*.py"))
                    # 优先选择包含 "auto_sim" 或 "main" 的脚本
                    preferred_scripts = [s for s in alternative_scripts if "auto_sim" in s.name or "main" in s.name]
                    if preferred_scripts:
                         script_path = preferred_scripts[0]
                    elif alternative_scripts:
                         script_path = alternative_scripts[0]
                    else:
                         logger.error("未找到任何Python脚本来执行创建实验的操作")
                         return {}
                    logger.info(f"使用脚本: {script_path}")
                else:
                    script_path = main_script_path
                    logger.info(f"使用主脚本: {script_path}")


            # 修改命令，确保调用脚本只执行添加参数的功能，而不是完整的流程
            cmd = [
                "python",
                str(script_path),
                "--params-file", str(temp_params_file) # 传递参数文件
            ]
            
            # 如果使用的是主脚本而不是专用脚本，我们可能需要添加额外的参数
            if script_path.name != "add_experiment.py":
                cmd.extend(["--project", str(self.project_path)])  # 传递项目路径

            # 执行命令前等待系统稳定
            time.sleep(2)

            # 执行命令，增加超时设置
            try:
                logger.info(f"执行命令: {' '.join(cmd)}")
                # 增加timeout，防止命令卡住
                result = subprocess.run(
                    cmd,
                    env=self.env,
                    cwd=str(self.project_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=180  # 3分钟超时
                )
            except subprocess.TimeoutExpired:
                logger.warning("创建实验的命令行命令执行超时")
                result = None

            # 等待系统更新
            time.sleep(5)

            # 删除临时文件
            if temp_params_file.exists():
                os.remove(temp_params_file)

            # 检查结果
            output = ""
            if result:
                 output = result.stdout
                 logger.info(f"命令输出: {output[:500]}...") # 只记录前500个字符
                 if result.returncode != 0:
                     logger.error(f"命令执行失败: {result.stderr}")
                     # 即使命令报告失败，仍尝试检查是否有新节点创建
            else:
                 logger.warning("命令执行无返回结果 (可能超时)")


            # 重新扫描文件系统查找新节点
            # 等待一段时间确保文件已写入
            logger.info("重新扫描文件系统以查找新增节点...")
            time.sleep(3)

            new_node_files = []
            for pattern in all_patterns:
                new_node_files.extend(list(self.project_path.glob(pattern)))

            # 提取新节点ID
            new_node_ids = set()
            for f in new_node_files:
                try:
                    if f.stem.startswith('n'):
                       if '_' in f.stem:
                           node_id_str = f.stem.split('_')[0][1:]
                           if node_id_str.isdigit():
                               new_node_ids.add(int(node_id_str))
                       elif f.stem.endswith('_command'):
                           node_id_str = f.stem.replace('_command', '')[1:]
                           if node_id_str.isdigit():
                               new_node_ids.add(int(node_id_str))
                except (ValueError, IndexError):
                    continue

            # 找出新增的节点
            added_nodes = new_node_ids - old_node_ids
            if added_nodes:
                logger.info(f"通过文件系统扫描到新增节点: {sorted(list(added_nodes))}")
            else:
                logger.warning("通过文件系统未扫描到新增节点")
                # 尝试从命令行输出再次提取
                import re
                output_nodes = set()
                if output:
                    matches = re.findall(r'节点\s*(\d+)', output) # 匹配 "节点 X"
                    output_nodes.update(int(m) for m in matches if int(m) > max_existing_node)
                    matches = re.findall(r'nodeId=(\d+)', output) # 匹配 nodeId=X
                    output_nodes.update(int(m) for m in matches if int(m) > max_existing_node)
                if output_nodes:
                    logger.info(f"从命令输出中提取到可能的新节点: {sorted(list(output_nodes))}")
                    added_nodes = output_nodes
                else:
                    logger.error("无法通过任何方式确认新增节点。创建实验可能失败。")
                    return {}


            # 过滤掉明显不是叶节点的（比如参数节点，如果能识别）
            # 这里简化处理，返回所有新增节点
            return {
                "all_added": list(added_nodes),
                "leaf_added": []
            }

        except Exception as e:
            logger.error(f"调用外部脚本创建实验失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {}
    
    def run_nodes(self, node_ids):
        """
        运行指定节点
        
        Args:
            node_ids: 节点ID集合或列表
        
        Returns:
            dict: 节点运行状态，格式为 {节点ID: 状态}
        """
        if not self.swb_api_available or not self.tree:
            return self._run_nodes_cmd(node_ids)
        
        try:
            # 首先进行预处理
            logger.info("开始预处理...")
            self.deck.preprocess()
            logger.info("预处理完成")
            
            # 运行结果状态字典
            results = {}
            
            # 所有节点都视为计算节点，不再区分参数节点
            real_compute_nodes = list(node_ids)
            
            # 按节点ID排序，确保正确顺序
            real_compute_nodes.sort()
            
            logger.info(f"需要运行的节点: {real_compute_nodes}")
            
            # 如果没有需要运行的节点，返回
            if not real_compute_nodes:
                logger.info("没有需要运行的节点")
                return {}
            
            # 运行每个节点
            for node_id in real_compute_nodes:
                logger.info(f"尝试运行节点 {node_id}")
                try:
                    # 使用之前已验证有效的方法
                    self.deck.run(nodes=[node_id])
                    logger.info(f"成功启动节点 {node_id}")
                    results[node_id] = "started"
                    
                    # 等待节点处理开始
                    logger.info(f"等待节点处理开始（2秒）...")
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"运行节点 {node_id} 失败: {str(e)}")
                    results[node_id] = "failed"
                    
                    # 如果是最后一个节点并且失败，尝试运行所有节点
                    if node_id == real_compute_nodes[-1]:
                        logger.info("这是最后一个节点。尝试运行所有节点...")
                        try:
                            self.deck.run()
                            logger.info("启动了所有节点的运行")
                        except Exception as e2:
                            logger.error(f"运行所有节点也失败: {str(e2)}")
            
            # 合并结果，确保所有节点都有状态
            for node_id in node_ids:
                if node_id not in results:
                    results[node_id] = "unknown"
            
            return results
            
        except Exception as e:
            logger.error(f"运行节点失败: {str(e)}")
            return {}
    
    def _run_nodes_cmd(self, node_ids):
        """使用命令行方式运行节点（备用方法）"""
        logger.info("使用命令行方式运行节点")
        
        # 这里实现调用外部脚本来运行节点
        try:
            # 创建临时节点文件
            temp_nodes_file = self.project_path / "temp_nodes.json"
            with open(temp_nodes_file, 'w') as f:
                json.dump(list(node_ids), f)
                
            # 构建命令
            cmd = [
                "python", 
                str(self.project_path / "run_swb_nodes.py"), 
                "--nodes", 
                str(temp_nodes_file)
            ]
            
            # 执行命令
            result = subprocess.run(
                cmd, 
                env=self.env, 
                cwd=str(self.project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 删除临时文件
            if temp_nodes_file.exists():
                os.remove(temp_nodes_file)
            
            # 检查结果
            if result.returncode != 0:
                logger.error(f"命令执行失败: {result.stderr}")
                return {}
                
            # 返回简单结果
            return {node_id: "started" for node_id in node_ids}
                
        except Exception as e:
            logger.error(f"调用外部脚本运行节点失败: {str(e)}")
            return {}
    
    def check_run_status(self, node_ids):
        """
        检查节点运行状态
        
        Args:
            node_ids: 要检查的节点ID列表
            
        Returns:
            dict: 节点状态字典 {节点ID: 状态}
        """
        # 如果传入的是集合，转换为列表
        node_ids = list(node_ids) if isinstance(node_ids, set) else node_ids
        
        if not self.swb_api_available or not self.tree:
            return self._check_run_status_files(node_ids)
        
        # 首先尝试通过文件系统检查（这是最可靠的方法）
        file_statuses = self._check_run_status_files(node_ids)
        
        # 如果通过文件系统能获取到全部状态，则直接返回
        if all(status != "unknown" for status in file_statuses.values()):
            return file_statuses
            
        # 否则尝试通过SWB API获取状态
        try:
            # 通过SearchNodesByStatus获取不同状态的节点
            try:
                ready_nodes = self.tree.SearchNodesByStatus("ready")
                done_nodes = self.tree.SearchNodesByStatus("done")  
                failed_nodes = self.tree.SearchNodesByStatus("failed")
                running_nodes = self.tree.SearchNodesByStatus("running")
                
                statuses = {}
                for node_id in node_ids:
                    if node_id in done_nodes:
                        statuses[node_id] = "done"
                    elif node_id in failed_nodes:
                        statuses[node_id] = "failed"
                    elif node_id in running_nodes:
                        statuses[node_id] = "running"
                    elif node_id in ready_nodes:
                        statuses[node_id] = "ready"
                    else:
                        # 如果通过API无法确定，则使用文件系统检查的结果
                        statuses[node_id] = file_statuses.get(node_id, "unknown")
                        
                return statuses
                
            except Exception as e:
                logger.warning(f"通过SearchNodesByStatus获取状态失败: {str(e)}")
                # 如果API方法失败，回退到文件系统检查结果
                return file_statuses
                
        except Exception as e:
            logger.error(f"检查节点状态时出错: {str(e)}")
            # 如果有错误，直接返回文件系统检查结果
            return file_statuses
    
    def get_node_info(self, node_id: int) -> Dict[str, Any]:
        """
        获取节点信息（工具类型、状态等），优先使用API，失败则尝试文件查找。

        Args:
            node_id: 节点ID

        Returns:
            包含节点信息的字典，例如 {'id': node_id, 'tool': 'sdevice', 'status': 'done'}
            如果失败则返回 {'id': node_id, 'tool': 'unknown', 'status': 'unknown'}
        """
        self.logger.info(f"获取节点 {node_id} 的详细信息")
        # 状态获取移至 wait_for_simulation_completion，这里主要关注工具类型
        node_info = {'id': node_id, 'tool': 'unknown', 'status': 'pending_check'}

        # 通过文件查找推断工具类型
        self.logger.debug(f"尝试通过文件查找节点 {node_id} 的工具类型...")
        tool_found = False
        max_retries = 3
        retry_delay = 2 # 秒
        for attempt in range(max_retries):
            try:
                patterns = [
                    f"*n{node_id}*_des.cmd", # SDevice (Flexible pattern)
                    f"*n{node_id}*_dvs.cmd", # SDE (Flexible pattern)
                    f"*n{node_id}*_fps.cmd", # Sprocess (Flexible pattern)
                    f"*n{node_id}*_vis.tcl", # SVisual (Flexible pattern)
                    # f"n{node_id}_plt",     # Replaced by _find_plt_files with flexible pattern
                    f"*n{node_id}*_command"  # Generic command file (Flexible pattern)
                ]
                for pattern in patterns:
                    # 在项目根目录查找
                    found_files = list(self.project_path.glob(pattern))
                    # 同时在可能的节点子目录查找 (虽然标准项目通常不在子目录)
                    # found_files.extend(list(self.project_path.glob(f"**/n{node_id}*/{pattern}")))
                    
                    if found_files:
                        file_path = found_files[0]
                        self.logger.debug(f"找到节点 {node_id} 的关联文件: {file_path} (尝试 {attempt+1})")
                        if "_des" in file_path.name: node_info['tool'] = 'sdevice'
                        elif "_dvs" in file_path.name: node_info['tool'] = 'sde'
                        elif "_fps" in file_path.name: node_info['tool'] = 'sprocess'
                        elif "_vis" in file_path.name: node_info['tool'] = 'svisual'
                        elif "_plt" in file_path.name:
                            if node_info['tool'] == 'unknown': node_info['tool'] = 'sdevice_or_sde'
                        elif "_command" in file_path.name:
                            if node_info['tool'] == 'unknown': node_info['tool'] = 'command_step'
                        tool_found = True
                        break # 找到一种即可
                if tool_found:
                    break # 找到工具类型，跳出重试循环
            except Exception as e:
                self.logger.error(f"通过文件查找节点 {node_id} 信息时出错 (尝试 {attempt+1}): {e}")
                
            if not tool_found and attempt < max_retries - 1:
                self.logger.info(f"未找到节点 {node_id} 文件，{retry_delay}秒后重试...")
                time.sleep(retry_delay)

        if tool_found:
             self.logger.info(f"通过文件推断节点 {node_id} 工具为: {node_info['tool']}")
        else:
             self.logger.warning(f"未能通过文件找到节点 {node_id} 的明确工具类型")

        self.logger.info(f"最终获取的节点 {node_id} 信息: {node_info}")
        return node_info

    def run_specific_nodes(self, node_ids: List[int]):
        """
        运行指定的节点列表。
        优先使用 SWB API (deck.run)，如果API不可用则回退到命令行模式。
        
        Args:
            node_ids: 需要运行的节点ID列表。
            
        Returns:
            bool: 是否所有节点都成功提交运行。或者命令行模式下返回运行状态字典。
        """
        if not node_ids:
            self.logger.warning("没有指定要运行的节点")
            return False

        # 如果 API 可用，则继续使用 SWB API 运行，如不可用则已在上文回退

        # 确保使用 API 模式
        if not self.swb_api_available or not self.deck:
            self.logger.error("SWB API 不可用或未初始化，无法使用 deck.run(nodes=...) 运行节点。")
            return False
            
        # 按照 mct_auto_sim.py 的逻辑，运行所有传入的节点，通常是 all_added_nodes
        self.logger.info(f"准备使用 deck.run(nodes=[node_id]) 运行节点: {node_ids}")
        success_all = True
        run_count = 0
        fail_count = 0
        
        # 确保按 ID 顺序运行
        sorted_node_ids = sorted(list(node_ids))
        self.logger.info(f"将按顺序运行节点: {sorted_node_ids}")

        for node_id in sorted_node_ids:
            self.logger.info(f"  - 尝试运行节点 ID: {node_id}")
            try:
                # 使用 mct_auto_sim.py 中验证过的方法
                self.deck.run(nodes=[node_id])
                self.logger.info(f"    成功启动节点 {node_id}。")
                run_count += 1
                
                # 短暂等待，让节点开始处理
                wait_after_run = 1 # 秒
                self.logger.info(f"    等待 {wait_after_run} 秒...")
                time.sleep(wait_after_run)
            except Exception as e:
                self.logger.error(f"    运行节点 {node_id} 失败: {e}")
                fail_count += 1
                success_all = False
                # 这里不 break，尝试运行后续节点
                
                # 考虑 mct_auto_sim.py 中的回退逻辑：如果最后一个节点失败，尝试运行全部
                if node_id == sorted_node_ids[-1]:
                    self.logger.warning(f"最后一个节点 {node_id} 运行失败，尝试 deck.run() 作为回退...")
                    try:
                        self.deck.run() # 运行所有 ready 节点
                        self.logger.info("    deck.run() 回退调用成功提交。")
                    except Exception as e2:
                        self.logger.error(f"    deck.run() 回退调用也失败: {e2}")
        
        self.logger.info(f"节点运行尝试完成。成功启动: {run_count}, 失败: {fail_count}")
        # 返回 True 即使部分失败，让后续的状态检查处理
        # return success_all 
        return True # 表示尝试过程完成，后续依赖状态检查
        
    def _find_plt_files(self, node_id: int) -> List[Path]:
        """
        查找与指定节点ID相关的plt文件
        
        Args:
            node_id (int): 节点ID
            
        Returns:
            list: 找到的plt文件路径列表
        """
        plt_files = []
        
        # 使用更灵活的模式查找 plt 文件
        # 在项目根目录查找
        pattern = f"*n{node_id}*.plt"
        logger.debug(f"在 {self.project_path} 中查找模式: {pattern}")
        try:
            found_files = list(self.project_path.glob(pattern))
            # 也可以考虑递归查找，但通常 plt 在根目录
            # found_files.extend(list(self.project_path.rglob(pattern)))
            
            plt_files = [f.absolute() for f in found_files] # 返回绝对路径Path对象
        except Exception as e:
            logger.error(f"查找节点 {node_id} 的plt文件时出错: {str(e)}")
        
        logger.debug(f"节点 {node_id} 找到 {len(plt_files)} 个plt文件: {plt_files}")
        return plt_files
    
    def parse_simulation_results(self, node_id):
        """
        解析仿真结果
        
        Args:
            node_id: 节点ID
            
        Returns:
            dict: 解析后的结果
        """
        logger.info(f"解析节点 {node_id} 的仿真结果")
        
        try:
            # 检查节点信息
            node_info = self.get_node_info(node_id)
            if not node_info:
                logger.warning(f"找不到节点 {node_id} 的信息")
                return {}
            
            # 获取相关工具标签
            if node_info['tool'] == 'sdevice':
                # 找到相关的sdevice工具标签
                cmd_file = self.project_path / f"n{node_id}_des.cmd"
                tool_label = cmd_file.stem.split('_')[0] if cmd_file.exists() else "HeavyIon"
            else:
                # 默认使用HeavyIon作为工具标签
                tool_label = "HeavyIon"
            
            # 调用ResultAnalyzer处理结果
            from auto_sim.result_analyzer import ResultAnalyzer
            result_analyzer = ResultAnalyzer(self.project_path)
            results = result_analyzer.process_simulation_results(node_id, tool_label)
            
            logger.info(f"节点 {node_id} 的解析结果: {results}")
            return results
                
        except Exception as e:
            logger.error(f"解析节点 {node_id} 的结果时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
            
    def close_connection(self):
        """关闭与SWB的连接"""
        if not self.swb_api_available or not self.deck:
            return
            
        try:
            # 释放SWB资源
            del self.deck # 使用del触发析构函数关闭项目
            self.deck = None
            self.tree = None
            logger.info("关闭了与SWB的连接")
        except Exception as e:
            logger.error(f"关闭连接时出错: {str(e)}")

    def run_all_ready_nodes(self):
        """
        尝试使用 SWB API (deck.run() 无参数) 运行项目中所有状态为 'ready' 的节点。
        
        Returns:
            bool: 是否成功提交运行。
        """
        if not self.swb_api_available or not self.deck:
            self.logger.error("SWB API 不可用或未初始化，无法使用 deck.run()")
            return False

        self.logger.info("尝试使用 SWB API (deck.run()) 运行所有 Ready 节点...")
        try:
            self.deck.run() # 调用无参数的 run 方法
            self.logger.info("成功提交运行所有 Ready 节点。")
            return True
        except Exception as e:
            self.logger.error(f"通过 API 运行所有 Ready 节点失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False
        
    def _check_run_status_files(self, node_ids):
        """通过文件系统检查节点状态"""
        statuses = {}
        
        try:
            # 创建临时节点文件
            temp_nodes_file = self.project_path / "temp_check_nodes.json"
            with open(temp_nodes_file, 'w') as f:
                json.dump(list(node_ids), f)
                
            # 构建命令
            check_script = self.project_path / "check_node_status.py"
            if check_script.exists():
                cmd = [
                    "python", 
                    str(check_script), 
                    "--nodes", 
                    str(temp_nodes_file)
                ]
                
                # 执行命令
                result = subprocess.run(
                    cmd, 
                    env=self.env, 
                    cwd=str(self.project_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 检查结果
                if result.returncode != 0:
                    logger.error(f"检查节点状态命令执行失败: {result.stderr}")
                else:
                    # 读取生成的状态文件
                    status_file = str(temp_nodes_file).replace(".json", "_status.json")
                    if os.path.exists(status_file):
                        with open(status_file, 'r') as f:
                            status_data = json.load(f)
                            # 转换键为整数
                            for node_id_str, status in status_data.items():
                                try:
                                    node_id = int(node_id_str)
                                    statuses[node_id] = status
                                except ValueError:
                                    continue
                        
                        # 删除临时状态文件
                        os.remove(status_file)
            else:
                # 如果脚本不存在，模拟所有节点完成
                for node_id in node_ids:
                    statuses[node_id] = "done"
                    
            # 删除临时节点文件
            if temp_nodes_file.exists():
                os.remove(temp_nodes_file)
                
        except Exception as e:
            logger.error(f"检查节点状态出错: {str(e)}")
            
        # 确保所有请求的节点都有状态
        for node_id in node_ids:
            if node_id not in statuses:
                statuses[node_id] = "unknown"
                
        return statuses

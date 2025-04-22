#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
Sentaurus Workbench自动化仿真系统 - 整合版
结合了mct_auto_sim.py的简单工作流和auto_sim目录中的高级模块
"""
import os
import sys
import time
import datetime
import argparse
import logging
import json
from pathlib import Path

# 导入auto_sim模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from auto_sim.parameter_manager import ParameterManager
    from auto_sim.swb_interaction import SWBInteraction
    from auto_sim.result_analyzer import ResultAnalyzer
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    print("警告: 未找到auto_sim模块，将使用基本功能")

# 尝试导入swbpy2
try:
    from swbpy2 import *
    from swbpy2.core.core import STATE_READY, STATE_NONE, STATE_DONE, STATE_FAILED, STATE_VIRTUAL, STATE_RUNNING, STATE_QUEUED, STATE_PENDING
    SWBPY2_AVAILABLE = True
except ImportError:
    SWBPY2_AVAILABLE = False
    print("错误: swbpy2模块未找到，请确保已正确安装")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("swb_integrated.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("swb_integrated")

# ======================================
# 默认配置
# ======================================
DEFAULT_CONFIG = {
    "PROJECT_PATH": os.path.abspath(os.path.dirname(__file__)),
    "AUTO_RUN": True,
    "REPORT_PATH": "iteration_report.md",
    "sde_params": {
        "Wtot": 50,
        "Wg": 10,
        "Wcp": 15,
        "Wcs": 4,
        "Tdrift": 320,
        "TPc": 0.2,
        "TNb": 1.5,
        "TNa": 1.5,
        "TPb": 5,
        "TPa": 0.6,
        "Tox": -0.2,
        "Tpoly": -2,
        "Tcathode": -4,
        "Zeropoint": 0,
        "Pc": 1e19,
        "Nb": 1.2e18,
        "Na": 1e15,
        "Ndrift": 5e13,
        "Npoly": 1e21,
        "Pb": 1e17,
        "Pa": 5e16,
        "x": 8.6,
        "Length": 35
    },
    "sdevice_params": ["-", 90, 800]
}

class SWBIntegrated:
    """整合版Sentaurus Workbench自动化仿真类"""

    def __init__(self, config=None):
        """
        初始化整合版自动化仿真系统
        
        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        # 加载配置
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
            
        # 确保项目路径是绝对路径
        self.config["PROJECT_PATH"] = os.path.abspath(self.config["PROJECT_PATH"])
        if not os.path.exists(self.config["PROJECT_PATH"]):
            logger.error(f"项目路径不存在: {self.config['PROJECT_PATH']}")
            sys.exit(1)
            
        # 确保报告路径是绝对路径
        if not os.path.isabs(self.config["REPORT_PATH"]):
            self.config["REPORT_PATH"] = os.path.join(self.config["PROJECT_PATH"], self.config["REPORT_PATH"])
            
        # 初始化模块
        self.swb = None
        self.param_manager = None
        self.result_analyzer = None
        
        # 如果高级模块可用，初始化它们
        if MODULES_AVAILABLE:
            logger.info("使用高级模块")
            self.swb = SWBInteraction(self.config["PROJECT_PATH"])
            self.param_manager = ParameterManager(self.config["PROJECT_PATH"])
            self.result_analyzer = ResultAnalyzer(self.config["PROJECT_PATH"])
        
        logger.info(f"初始化完成，项目路径: {self.config['PROJECT_PATH']}")
        
    def load_config_from_file(self, config_file):
        """
        从文件加载配置
        
        Args:
            config_file: 配置文件路径
        """
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
                logger.info(f"从文件加载配置: {config_file}")
                
            # 更新初始化的模块配置
            if self.swb:
                self.swb.project_path = Path(self.config["PROJECT_PATH"])
                self.swb.project_abs_path = self.swb.project_path.absolute()
                
            if self.param_manager:
                self.param_manager.project_path = Path(self.config["PROJECT_PATH"])
                
            if self.result_analyzer:
                self.result_analyzer.set_results_directory(self.config["PROJECT_PATH"])
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
    
    def get_combined_parameters(self):
        """
        获取组合的参数列表
        
        Returns:
            组合参数列表，按照SWB工具参数顺序
        """
        # 与mct_auto_sim.py中保持一致的参数顺序
        sde_order = ["Wtot", "Wg", "Wcp", "Wcs", "Tdrift", "TPc", "TNb", "TNa", "TPb", "TPa",
                     "Tox", "Tpoly", "Tcathode", "Zeropoint", "Pc", "Nb", "Na", "Ndrift",
                     "Npoly", "Pb", "Pa", "x", "Length"]
        
        sde_params = self.config["sde_params"]
        sde_list = [sde_params.get(key, 0) for key in sde_order]
        
        return sde_list + self.config["sdevice_params"]
    
    def generate_report(self, combined_params, iteration, run_status):
        """
        生成迭代报告
        
        Args:
            combined_params: 组合参数
            iteration: 迭代编号
            run_status: 运行状态
        """
        report_lines = []
        report_lines.append("# 仿真迭代报告")
        report_lines.append(f"**迭代编号：** {iteration}")
        report_lines.append(f"**日期：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        report_lines.append("## sde 参数")
        for key in ["Wtot", "Wg", "Wcp", "Wcs", "Tdrift", "TPc", "TNb", "TNa", "TPb", "TPa",
                    "Tox", "Tpoly", "Tcathode", "Zeropoint", "Pc", "Nb", "Na", "Ndrift",
                    "Npoly", "Pb", "Pa", "x", "Length"]:
            report_lines.append(f"- **{key}**: {self.config['sde_params'].get(key, 'N/A')}")
        
        report_lines.append("\n## sdevice 参数 (固定)")
        sdevice_order = ["eLifetime", "angle", "Vanode"]
        for key, value in zip(sdevice_order, self.config["sdevice_params"]):
            report_lines.append(f"- **{key}**: {value}")
        
        report_lines.append("\n## 操作记录")
        if run_status:
            report_lines.append(f"新增实验参数已更新，并触发了 {run_status['run_count']} 个新增节点的运行。")
            if run_status.get('fail_count', 0) > 0:
                report_lines.append(f"**警告：** {run_status['fail_count']} 个节点运行失败。")
        else:
            report_lines.append("新增实验参数已更新，设置为手动运行。")
        report_lines.append("\n---\n")
        
        report_content = "\n".join(report_lines)
        with open(self.config["REPORT_PATH"], "a") as f:
            f.write(report_content)
        
        logger.info(f"生成报告: {self.config['REPORT_PATH']}")
    
    def run_experiment(self):
        """
        运行实验：添加新实验节点并根据AUTO_RUN决定是否运行
        
        Returns:
            成功标志
        """
        # 使用两种方式实现: 高级模块或直接SWB API
        combined_params = self.get_combined_parameters()
        run_status_report = None
        
        # 打开项目
        logger.info(f"打开项目: {self.config['PROJECT_PATH']}")
        
        # 首先尝试使用高级模块
        if MODULES_AVAILABLE and self.swb:
            try:
                # 初始化连接
                if not self.swb.initialize_swb_connection():
                    logger.error("初始化SWB连接失败")
                    return False
                
                # 获取添加前的节点
                old_all_node_ids = self.swb.get_all_nodes()
                old_leaf_node_ids = self.swb.get_current_leaf_nodes()
                
                if not old_all_node_ids or not old_leaf_node_ids:
                    logger.error("获取现有节点失败")
                    return False
                
                logger.info(f"添加前: {len(old_all_node_ids)} 个节点，{len(old_leaf_node_ids)} 个叶节点")
                
                # 创建参数字典
                sde_order = ["Wtot", "Wg", "Wcp", "Wcs", "Tdrift", "TPc", "TNb", "TNa", "TPb", "TPa",
                             "Tox", "Tpoly", "Tcathode", "Zeropoint", "Pc", "Nb", "Na", "Ndrift",
                             "Npoly", "Pb", "Pa", "x", "Length"]
                
                sdevice_order = ["eLifetime", "angle", "Vanode"]
                
                params_dict = {}
                for key, value in zip(sde_order, combined_params[:len(sde_order)]):
                    params_dict[key] = value
                    
                for key, value in zip(sdevice_order, combined_params[len(sde_order):]):
                    params_dict[key] = value
                
                # 添加新实验
                success, added_nodes = self.swb.create_new_experiment(params_dict)
                
                if not success:
                    logger.error("创建新实验失败")
                    return False
                
                logger.info(f"成功添加新实验，新增节点: {added_nodes}")
                
                # 如果设置了AUTO_RUN，运行新节点
                run_count = 0
                fail_count = 0
                
                if self.config["AUTO_RUN"] and added_nodes:
                    logger.info("AUTO_RUN=True，开始运行新节点...")
                    node_status = self.swb.run_nodes(added_nodes)
                    
                    for node_id, status in node_status.items():
                        if status == "started":
                            run_count += 1
                        elif status == "failed":
                            fail_count += 1
                    
                    logger.info(f"运行了 {run_count} 个节点，{fail_count} 个失败")
                    
                    # 等待并检查运行状态
                    if run_count > 0:
                        logger.info("等待节点运行完成...")
                        final_status = self.swb.check_run_status(added_nodes)
                        
                        for node_id, status in final_status.items():
                            logger.info(f"节点 {node_id} 状态: {status}")
                    
                run_status_report = {
                    "run_count": run_count,
                    "fail_count": fail_count
                }
                
            except Exception as e:
                logger.error(f"使用高级模块时出错: {str(e)}")
                # 回退到使用直接API
                logger.info("回退到使用直接SWB API...")
                return self._run_experiment_direct_api(combined_params)
            
        else:
            # 使用直接API
            return self._run_experiment_direct_api(combined_params)
        
        # 生成报告
        self.generate_report(combined_params, 1, run_status_report)
        
        return True
    
    def _run_experiment_direct_api(self, combined_params):
        """
        使用直接SWB API运行实验
        
        Args:
            combined_params: 组合参数列表
        
        Returns:
            成功标志
        """
        run_status_report = None
        
        try:
            # 打开项目
            logger.info(f"使用直接API打开项目: {self.config['PROJECT_PATH']}")
            deck = Deck(self.config["PROJECT_PATH"], True)
            tree = deck.getGtree()
            logger.info("项目打开成功")
            
            # 获取添加前的叶节点和所有节点 IDs
            old_leaf_node_ids = set(tree.AllLeafNodes())
            old_all_node_ids = set(tree.AllNodes())
            logger.info(f"添加前: {len(old_all_node_ids)} 个节点存在 ({len(old_leaf_node_ids)} 个叶节点)")
            
            # 添加新实验并保存
            logger.info("添加新实验...")
            tree.AddPath(pvalues=combined_params)
            logger.info("新实验结构添加完成")
            deck.save()
            logger.info("项目已保存")
            
            # 重新加载以确保树对象反映保存的更改
            deck.reload()
            # 添加短暂延迟，允许SWB可能更新其状态
            logger.info("等待SWB状态更新 (2秒)...")
            time.sleep(2)
            tree = deck.getGtree()  # 刷新树对象实例
            logger.info("项目已重新加载")
            
            # 获取添加后的叶节点和所有节点 IDs
            current_all_node_ids = set(tree.AllNodes())
            current_leaf_node_ids = set(tree.AllLeafNodes())
            logger.info(f"添加后: {len(current_all_node_ids)} 个节点存在 ({len(current_leaf_node_ids)} 个叶节点)")
            
            # 计算新添加的节点 IDs
            added_leaf_node_ids = current_leaf_node_ids - old_leaf_node_ids
            added_all_node_ids = current_all_node_ids - old_all_node_ids
            
            if not added_leaf_node_ids:
                logger.warning("警告: 添加实验后未检测到新的叶节点。检查参数或项目状态。")
            else:
                logger.info(f"检测到 {len(added_leaf_node_ids)} 个新增叶节点: {added_leaf_node_ids}")
                logger.info(f"检测到 {len(added_all_node_ids)} 个总共新增节点: {added_all_node_ids}")
                
                # 按ID排序，以便按正确顺序运行
                all_new_nodes_to_run = sorted(list(added_all_node_ids))
                logger.info(f"将按此顺序仅运行新节点: {all_new_nodes_to_run}")
            
            # 如果设置了AUTO_RUN，预处理并仅运行新节点
            run_count = 0
            fail_count = 0
            
            if self.config["AUTO_RUN"]:
                if not added_leaf_node_ids:
                    logger.info("未检测到新节点，跳过运行阶段")
                else:
                    logger.info("AUTO_RUN=True，开始预处理...")
                    try:
                        deck.preprocess()
                        logger.info("预处理完成")
                    except Exception as e:
                        logger.error(f"预处理失败: {str(e)}")
                        return False
                    
                    logger.info("查找新节点中可运行的节点...")
                    
                    # 遍历每个新节点并尝试运行
                    for node_id in all_new_nodes_to_run:
                        logger.info(f"尝试运行节点ID: {node_id}")
                        try:
                            deck.run(nodes=[node_id])
                            logger.info(f"成功启动节点 {node_id}")
                            run_count += 1
                            
                            # 添加延迟，让节点开始处理
                            logger.info(f"等待1秒让节点开始处理...")
                            time.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"运行节点 {node_id} 失败: {str(e)}")
                            fail_count += 1
                    
                    # 等待节点完成
                    if run_count > 0:
                        logger.info("等待节点完成...")
                        time.sleep(5)  # 简单等待
                        
                        # 检查状态
                        try:
                            # 获取不同状态的节点列表
                            for state_name, state_val in [("ready", STATE_READY), ("none", STATE_NONE), 
                                                        ("done", STATE_DONE), ("running", STATE_RUNNING),
                                                        ("failed", STATE_FAILED)]:
                                try:
                                    nodes = tree.SearchNodesByStatus(state_val)
                                    logger.info(f"'{state_name}' 状态的节点: {len(nodes)}")
                                except TypeError:
                                    try:
                                        nodes = tree.SearchNodesByStatus(state_name)
                                        logger.info(f"'{state_name}' 状态的节点 (字符串参数): {len(nodes)}")
                                    except Exception as e:
                                        logger.error(f"无法检查 '{state_name}' 状态: {str(e)}")
                        except Exception as e:
                            logger.error(f"检查节点状态时出错: {str(e)}")
            
            run_status_report = {
                "run_count": run_count,
                "fail_count": fail_count
            }
            
            # 生成报告
            self.generate_report(combined_params, 1, run_status_report)
            
            return True
            
        except Exception as e:
            logger.error(f"使用直接API运行实验失败: {str(e)}")
            return False
    
    def analyze_results(self, node_id=None):
        """
        分析特定节点的结果
        
        Args:
            node_id: 节点ID，如果为None则分析所有叶节点
            
        Returns:
            分析结果
        """
        if not MODULES_AVAILABLE or not self.result_analyzer:
            logger.error("高级模块不可用，无法进行结果分析")
            return None
        
        try:
            # 确定要分析的节点
            nodes_to_analyze = []
            
            if node_id:
                nodes_to_analyze.append(node_id)
            else:
                # 获取所有叶节点
                if self.swb:
                    leaf_nodes = self.swb.get_current_leaf_nodes()
                    if leaf_nodes:
                        nodes_to_analyze = list(leaf_nodes)
                        
            results = {}
            for node in nodes_to_analyze:
                logger.info(f"分析节点 {node} 的结果...")
                node_results = {}
                
                # 尝试提取IV特性
                try:
                    node_results["iv"] = self.result_analyzer.analyze_iv_characteristics(
                        self.result_analyzer.load_data_file(f"{self.config['PROJECT_PATH']}/n{node}_iv.dat")
                    )
                except Exception as e:
                    logger.error(f"分析IV特性时出错: {str(e)}")
                
                # 尝试提取SEE结果
                try:
                    node_results["see"] = self.result_analyzer.analyze_see_results(
                        self.result_analyzer.load_data_file(f"{self.config['PROJECT_PATH']}/n{node}_see.dat")
                    )
                except Exception as e:
                    logger.error(f"分析SEE结果时出错: {str(e)}")
                
                results[node] = node_results
            
            return results
            
        except Exception as e:
            logger.error(f"分析结果时出错: {str(e)}")
            return None
    
    def close(self):
        """关闭连接和清理资源"""
        if MODULES_AVAILABLE and self.swb:
            self.swb.close_connection()
        
        logger.info("资源已释放")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Sentaurus Workbench自动化仿真系统 - 整合版")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--project", type=str, help="项目路径")
    parser.add_argument("--no-run", action="store_true", help="添加实验但不自动运行")
    parser.add_argument("--analyze", type=int, help="分析指定节点ID的结果")
    parser.add_argument("--analyze-all", action="store_true", help="分析所有叶节点的结果")
    
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 创建配置
    config = DEFAULT_CONFIG.copy()
    
    # 更新配置
    if args.config:
        try:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
    
    if args.project:
        config["PROJECT_PATH"] = args.project
    
    if args.no_run:
        config["AUTO_RUN"] = False
    
    # 创建整合版实例
    swb_integrated = SWBIntegrated(config)
    
    try:
        # 根据命令行参数执行操作
        if args.analyze:
            results = swb_integrated.analyze_results(args.analyze)
            print(json.dumps(results, indent=2))
        elif args.analyze_all:
            results = swb_integrated.analyze_results()
            print(json.dumps(results, indent=2))
        else:
            # 默认操作：运行实验
            swb_integrated.run_experiment()
    except Exception as e:
        logger.error(f"执行操作时出错: {str(e)}")
    finally:
        # 清理资源
        swb_integrated.close()

if __name__ == "__main__":
    main() 
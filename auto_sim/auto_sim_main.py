#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化仿真主控脚本
"""
import os
import sys
import time
import json
import logging
import argparse
import traceback
import subprocess
from pathlib import Path
from typing import List
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入所有模块
from auto_sim.parameter_manager import ParameterManager
from auto_sim.swb_interaction import SWBInteraction
from auto_sim.result_analyzer import ResultAnalyzer
from auto_sim.deepseek_interaction import DeepSeekInteraction
from auto_sim.report_generator import ReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_sim.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("auto_sim")

class AutoSimulation:
    """自动化仿真主控类"""
    
    def __init__(self, project_path, max_iterations=10, api_key=None, use_fake_results=False):
        """
        初始化自动化仿真系统
        
        Args:
            project_path: Sentaurus项目路径
            max_iterations: 最大迭代次数
            api_key: DeepSeek API密钥
            use_fake_results: 是否使用假的仿真结果（测试用）
        """
        # 设置项目路径
        self.project_path = Path(project_path).resolve()
        
        # 初始化日志
        self.logger = logging.getLogger("auto_sim")
        
        # 创建目录结构
        self._create_directory_structure()
        
        # 读取配置
        self.config = {}
        self.config_file = self.project_path / "auto_sim" / "config.json"
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info("成功加载配置文件")
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {str(e)}")
        else:
            self.logger.warning(f"配置文件不存在: {self.config_file}")
            
        # 设置参数
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.use_fake_results = use_fake_results
        
        # 保存最佳结果
        self.iteration_history = []
        self.best_result = None
        
        # 初始化参数管理器
        self.logger.info("初始化参数管理器...")
        self.param_manager = ParameterManager(self.project_path)
        
        # 初始化SWB交互模块
        self.logger.info("初始化SWB交互模块...")
        self.swb_interaction = SWBInteraction(self.project_path)
        
        # 初始化结果分析模块
        self.logger.info("初始化结果分析模块...")
        self.result_analyzer = ResultAnalyzer(self.project_path)
        
        # 初始化DeepSeek API模块
        self.logger.info("初始化DeepSeek API模块...")
        self.deepseek_interaction = DeepSeekInteraction(
            api_key=api_key,
            simulation_mode=use_fake_results
        )
        
        # 初始化报告生成模块
        self.logger.info("初始化报告生成模块...")
        self.report_generator = ReportGenerator(self.project_path)
        
        # 扫描项目结构，识别 SDE 与 SDevice 工具标签
        self.logger.info("扫描项目结构以确定工具标签...")
        if not self.scan_project_structure():
            self.logger.error("项目结构扫描失败，无法确定工具脚本文件")
        
        # SDevice工具标签
        self.sdevice_tool_label = self.config.get('sdevice_tool_label', 'sdevice')
        
        # 将可能用到的字符串转换为Path对象
        if isinstance(project_path, str):
            self.project_path = Path(project_path)
            
        # 初始化跳过节点检查标志
        self.skip_node_check = False
        
        # 初始化SWB连接
        if not self.use_fake_results:
            if not self.swb_interaction.initialize_swb_connection():
                logger.error("初始化SWB连接失败")
        
    def _create_directory_structure(self):
        """创建必要的目录结构"""
        dirs = [
            self.project_path / "Parameter" / "Initial_Parameter",
            self.project_path / "Parameter" / "Generated_Parameter",
            self.project_path / "Results" / "Extracted",
            self.project_path / "Results" / "Raw",
            self.project_path / "Results" / "Figures",
            self.project_path / "Reports" / "iteration_reports",
            self.project_path / "DeepSeek" / "Prompts",
            self.project_path / "DeepSeek" / "Responses",
            self.project_path / "DeepSeek" / "Condensed",
            self.project_path / "auto_sim" / "templates",
            self.project_path / "auto_sim" / "utils",
        ]
        
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"确保目录存在: {directory}")
    
    def read_sde_code(self):
        """读取SDE代码"""
        try:
            sde_file = self.project_path / f"{self.sde_tool_label}_dvs.cmd"
            if not sde_file.exists():
                logger.error(f"未找到SDE文件: {sde_file}")
                return ""
                
            with open(sde_file, 'r', encoding='utf-8') as f:
                sde_code = f.read()
                
            logger.info(f"已读取SDE代码文件: {sde_file}")
            return sde_code
        except Exception as e:
            logger.error(f"读取SDE代码出错: {str(e)}")
            return ""
    
    def read_sdevice_code(self):
        """读取SDevice代码"""
        try:
            sdevice_file = self.project_path / f"{self.sdevice_tool_label}_des.cmd"
            if not sdevice_file.exists():
                logger.error(f"未找到SDevice文件: {sdevice_file}")
                return ""
                
            with open(sdevice_file, 'r', encoding='utf-8') as f:
                sdevice_code = f.read()
                
            logger.info(f"已读取SDevice代码文件: {sdevice_file}")
            return sdevice_code
        except Exception as e:
            logger.error(f"读取SDevice代码出错: {str(e)}")
            return ""
    
    def verify_initial_parameters(self):
        """验证初始参数组"""
        if not self.param_manager.initial_params_exist():
            logger.warning("未找到初始参数文件。创建示例参数文件...")
            self.param_manager.create_example_params()
            
            print("\n请检查并修改初始参数文件:")
            print(f"{self.project_path}/Parameter/Initial_Parameter/initial_params.json")
            print("然后重新运行此脚本。")
            sys.exit(0)
        
        # 显示初始参数并请求确认
        initial_params = self.param_manager.get_initial_params()
        print("\n当前初始参数组:")
        for key, value in initial_params.items():
            print(f"    {key}: {value}")
        
        confirmation = input("\n这些参数是否正确？ (y/n): ")
        if confirmation.lower() != 'y':
            print("请修改初始参数文件后重新运行此脚本。")
            sys.exit(0)
            
        logger.info("初始参数已确认")
        return True
    
    def scan_project_structure(self):
        """扫描项目结构，识别SDE和SDevice模块"""
        logger.info("扫描项目结构...")
        
        # 遍历项目目录，查找SDE和SDevice文件
        sde_files = []
        sdevice_files = []
        
        for file in self.project_path.glob("*_dvs.cmd"):
            sde_files.append(file)
            
        for file in self.project_path.glob("*_des.cmd"):
            sdevice_files.append(file)
        
        if not sde_files:
            logger.error("未找到SDE文件（*_dvs.cmd）")
            return False
            
        if not sdevice_files:
            logger.error("未找到SDevice文件（*_des.cmd）")
            return False
        
        # 使用第一个找到的文件
        self.sde_tool_label = sde_files[0].stem.replace("_dvs", "")
        self.sdevice_tool_label = sdevice_files[0].stem.replace("_des", "")
        
        logger.info(f"找到SDE工具: {self.sde_tool_label}")
        logger.info(f"找到SDevice工具: {self.sdevice_tool_label}")
        
        # 验证文件存在
        sde_file = self.project_path / f"{self.sde_tool_label}_dvs.cmd"
        sdevice_file = self.project_path / f"{self.sdevice_tool_label}_des.cmd"
        
        if not sde_file.exists():
            logger.error(f"未找到SDE工具文件: {sde_file}")
            return False
            
        if not sdevice_file.exists():
            logger.error(f"未找到SDevice工具文件: {sdevice_file}")
            return False
            
        logger.info("项目结构扫描完成")
        return True
    
    def wait_for_simulation_completion(self, node_ids: List[int], timeout: int = 3600):
        """
        等待指定的叶节点仿真完成。
        通过循环检查对应的 *.plt 文件是否存在来判断。
        
        Args:
            node_ids (List[int]): 需要等待完成的叶节点ID列表。
            timeout (int): 最长等待时间（秒）。
        """
        if not node_ids:
            self.logger.warning("没有指定需要等待的节点")
            return
            
        self.logger.info(f"等待节点完成仿真: {node_ids}")
        start_time = time.time()
        nodes_to_wait = set(node_ids)
        completed_nodes = set()
        poll_interval = 10 # 秒

        while nodes_to_wait and (time.time() - start_time) < timeout:
            finished_in_this_poll = set()
            for node_id in list(nodes_to_wait): # Iterate over a copy
                # 检查此节点对应的 .plt 文件是否存在
                # 使用与 _find_plt_files 类似的灵活模式
                pattern = f"*n{node_id}*.plt"
                found_plt = list(self.project_path.glob(pattern))
                
                if found_plt:
                    self.logger.info(f"检测到节点 {node_id} 的输出文件: {found_plt[0]} - 标记为完成。")
                    completed_nodes.add(node_id)
                    finished_in_this_poll.add(node_id)
                # 还可以考虑检查 .log 文件中的完成标记或 .job 文件状态，但 plt 是最直接的
            
            # 从等待集合中移除已完成的
            nodes_to_wait -= finished_in_this_poll
            
            if nodes_to_wait:
                self.logger.info(f"仍在等待节点: {sorted(list(nodes_to_wait))}... ({int(time.time() - start_time)}s / {timeout}s)")
                time.sleep(poll_interval)
            else:
                self.logger.info("所有指定的节点都已检测到输出文件。")
                break

        if nodes_to_wait: # 超时
            self.logger.error(f"等待节点 {sorted(list(nodes_to_wait))} 完成超时 ({timeout}秒)！")
            # 即使超时，也要记录哪些节点被视为完成（可能部分完成）
            # 返回或记录状态可能需要调整
            # for node_id in nodes_to_wait:
            #     self.update_best_result(self.current_iteration, {}, {"error": "timeout"}, node_id)

        # 旧的调用方式，不再使用
        # try:
        #     node_statuses = self.swb_interaction.wait_for_nodes(node_ids, timeout=timeout)
        #     self.logger.info(f"所有节点完成状态: {node_statuses}")
        #     # 检查是否有节点失败或超时
        #     failed_nodes = [nid for nid, status in node_statuses.items() if status == 'failed']
        #     timed_out_nodes = [nid for nid, status in node_statuses.items() if status == 'timeout']
        #     
        # except Exception as e:
        #     self.logger.error(f"等待节点完成时出错: {str(e)}")

    def get_best_result_so_far(self):
        """
        获取目前最好的结果
        
        Returns:
            dict: 最佳结果信息
        """
        if not self.best_result:
            return None
            
        return self.best_result
    
    def update_best_result(self, iteration, params, simulation_result, node_id):
        """
        更新最佳结果
        
        Args:
            iteration: 迭代次数
            params: 参数组
            simulation_result: 仿真结果
            node_id: 节点ID
        """
        if not simulation_result:
            return
            
        # 检查是否达到性能目标（未闩锁）
        is_latchup = simulation_result.get('is_latchup', True)
        vanode = params.get('Vanode', 0)
        
        # 如果当前结果未闩锁，且阳极电压更高，则更新最佳结果
        if not is_latchup:
            if not self.best_result or vanode > self.best_result.get('vanode', 0):
                figure_path = self.project_path / "Results" / "Figures" / f"iteration_{iteration}_node_{node_id}_result.png"
                
                self.best_result = {
                    'iteration': iteration,
                    'params': params,
                    'vanode': vanode,
                    'is_latchup': is_latchup,
                    'vst_status': simulation_result.get('vst_status', '未知'),
                    'figure_path': str(figure_path) if figure_path.exists() else None
                }
                
                logger.info(f"更新最佳结果: 迭代{iteration}, 阳极电压={vanode}V, 未闩锁")
    
    def run_simulation_cycle(self, params):
        """
        运行单个仿真周期
        
        Args:
            params (dict): 仿真参数
            
        Returns:
            tuple: (params, results) 仿真参数和结果
        """
        self.logger.info(f"运行仿真周期，参数: {params}")
        
        # 创建实验节点
        try:
            experiment_info = self.swb_interaction.create_new_experiment(params)
            if not experiment_info or not experiment_info.get("all_added"):
                error_msg = "未能创建新的实验节点或未检测到新增节点"
                self.logger.error(error_msg)
                return params, {"error": error_msg}
                
            all_new_nodes = experiment_info["all_added"]
            leaf_nodes_to_watch = experiment_info["leaf_added"]
            leaf_info = experiment_info.get("leaf_info", []) # 获取叶节点信息
            self.logger.info(f"创建的所有新节点: {all_new_nodes}")
            self.logger.info(f"需要关注的新增叶节点: {leaf_nodes_to_watch}")
            
            if not leaf_nodes_to_watch:
                self.logger.warning("未检测到新增的叶节点，流程可能无法正常进行结果分析。")
                # 可以选择继续运行所有节点，或在此处返回错误
                # return params, {"error": "未检测到新增叶节点"}

        except Exception as e:
            self.logger.error(f"创建实验节点失败: {str(e)}")
            return params, {"error": f"创建实验节点异常: {str(e)}"}
        
        # 增加延时，给SWB时间准备运行环境
        delay_before_run = 5 # 秒
        self.logger.info(f"等待 {delay_before_run} 秒，让SWB准备运行节点...")
        time.sleep(delay_before_run)
        
        # 运行所有新增的节点 (模仿 mct_auto_sim.py 的行为)
        if not all_new_nodes:
            self.logger.warning("没有要运行的新增节点")
            # 如果没有新增节点，但流程到了这里，可能是个问题
            return params, {"error": "未找到任何新增节点来运行"} 
        
        run_success = self.swb_interaction.run_specific_nodes(all_new_nodes)
        if not run_success:
            error_msg = f"提交运行所有新增节点 {all_new_nodes} 失败"
            self.logger.error(f"{error_msg}，无法继续")
            return params, {"error": error_msg}
        
        # 等待关键的叶节点仿真完成 (通过检查文件)
        if not leaf_nodes_to_watch:
             self.logger.warning("没有叶节点需要等待，将直接尝试解析（可能失败）")
             # 如果没有叶节点，解析结果会失败，这里可以提前返回或记录
             results = {"warning": "没有叶节点完成可供解析"}
        else:
            self.wait_for_simulation_completion(leaf_nodes_to_watch)
            # 调用结果分析（使用正确的参数签名）
            results = self.result_analyzer.process_simulation_results(
                leaf_nodes_to_watch[0],  # 节点ID
                self.sdevice_tool_label    # 工具标签
            )
            # 注意：如果 leaf_nodes_to_watch 可能为空，这里需要处理 IndexError
            # 注意：ResultAnalyzer 目前的 process_simulation_results 只接受单个 node_id ，
            # 如果需要处理多个叶节点的结果（例如比较），需要修改 ResultAnalyzer。
            # 目前简化为只处理第一个叶节点。
            if not leaf_nodes_to_watch:
                 results = {"error": "没有叶节点可供解析"}
                 self.logger.error(results["error"])

        # 如果解析结果是空的，或者只包含错误信息，则标记为失败
        if not results or (len(results) == 1 and "error" in results):
            return params, {"error": "解析结果为空或只包含错误信息"}
        
        # 更新存储迭代数据，包含叶节点信息
        self._store_iteration_data(
            iteration=self.current_iteration, 
            params=params, 
            results=results,
            optimized_params=None, # 传递上一轮的建议（如果存在）
            node_id=leaf_nodes_to_watch[0] if leaf_nodes_to_watch else 'unknown' # 简化：仍用第一个叶节点ID
        )
        
        # 更新最佳结果 (目前已移至 _store_iteration_data 内注释掉)
        # self.update_best_result(self.current_iteration, params, results, leaf_nodes_to_watch[0])
        
        return params, results
    
    def parse_simulation_results(self, sdevice_nodes):
        """
        解析仿真结果
        
        Args:
            sdevice_nodes (list): sdevice节点ID列表
            
        Returns:
            dict: 解析后的结果
        """
        self.logger.info(f"解析仿真结果，节点: {sdevice_nodes}")
        
        if not sdevice_nodes:
            self.logger.warning("没有可解析的节点")
            return {}
            
        # 选择第一个节点进行解析（可以扩展为合并多个节点的结果）
        node_id = sdevice_nodes[0]
        
        try:
            results = self.swb_interaction.parse_simulation_results(node_id)
            self.logger.info(f"节点 {node_id} 的解析结果: {results}")
            return results
        except Exception as e:
            self.logger.error(f"解析节点 {node_id} 的结果时出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {}
    
    def check_performance_target(self):
        """
        检查是否达到性能目标
        
        Returns:
            bool: 是否达到目标
        """
        if not self.iteration_history:
            return False
        
        last_result = self.iteration_history[-1].get('results', {})
        
        # 获取新目标指标
        breakdown_voltage = last_result.get('breakdown_voltage', 0) # 从结果中获取击穿电压
        threshold_voltage = last_result.get('threshold_voltage', float('inf')) # 从结果中获取阈值电压

        # 获取目标值 (可以从 config.json 或硬编码)
        target_bv = self.config.get("target_breakdown_voltage", 1450) 
        target_vth_max = self.config.get("target_threshold_voltage_max", 10)

        self.logger.info(f"检查性能目标: 当前 BV={breakdown_voltage}V (目标 > {target_bv}V), Vth={threshold_voltage}V (目标 < {target_vth_max}V)")
        
        # 检查是否达到目标
        if breakdown_voltage >= target_bv and threshold_voltage < target_vth_max:
            self.logger.info(f"性能目标已达到！BV ≥ {target_bv}V 且 Vth < {target_vth_max}V")
            return True
        else:
            self.logger.info("性能目标未达到。")
            return False
    
    def _store_iteration_data(self, iteration, params, results, optimized_params=None, node_id='unknown'):
        """存储单次迭代的数据到历史记录中"""
        if not results:
            logger.warning(f"迭代 {iteration} 没有有效结果，无法存储历史。")
            return

        history_entry = {
            'iteration': iteration,
            'params': params.copy() if params else {},
            'results': results.copy(),
            'optimized_params': optimized_params.copy() if optimized_params else {},
            'node_id': node_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.iteration_history.append(history_entry)
        logger.info(f"迭代 {iteration} 的数据已存储到历史记录。")
        
        # 同时更新 best_result (如果需要)
        # 注意：这里可以保留寻找"最佳"的逻辑，或者完全依赖最终报告
        # 保持简单：暂时只存储历史
        # self.update_best_result(iteration, params, results, node_id)

    def run_complete_flow(self, initial_params):
        """
        运行完整的仿真流程
        """
        logger.info("开始完整仿真流程...")
        
        try:
            # ---- 主要仿真逻辑开始 ----
            current_params = initial_params
            self.iteration_history = []
            
            # 运行初始仿真获取基准结果
            iteration_number = 1
            logger.info(f"执行第{iteration_number}次仿真")
            self.current_iteration = iteration_number # 更新当前迭代号
            
            # 初始参数运行仿真
            current_params, simulation_results = self.run_simulation_cycle(current_params)
            # self._update_best_results(simulation_results, current_params) # 旧方法
            # 存储迭代数据
            self._store_iteration_data(
                iteration=iteration_number, 
                params=current_params, 
                results=simulation_results,
                node_id=simulation_results.get('leaf_node_id', 'unknown') # 假设 run_simulation_cycle 返回叶节点ID
            )

            # 生成第一次迭代报告 (无优化建议, 无思考过程)
            self.report_generator.generate_iteration_report(
                iteration=iteration_number,
                params=current_params,
                results=simulation_results,
                deepseek_thought="首次运行，无 DeepSeek 思考过程。" # 添加默认值
            )
            
            # 运行优化迭代
            max_iterations = self.config.get('max_iterations', 10)
            for iteration_number in range(2, max_iterations + 1):
                # 检查上一轮结果是否有错误
                if simulation_results.get("error"):
                    logger.error(f"上一轮仿真出错: {simulation_results['error']}，终止优化流程")
                    break
                
                logger.info(f"执行第{iteration_number}次仿真迭代")
                
                # 获取优化参数并运行下一轮仿真
                # !! 注意：需要修改 get_optimization_suggestions 返回原始响应 !!
                optimized_params, deepseek_raw_response = self.deepseek_interaction.get_optimization_suggestions(
                    current_params=current_params,
                    simulation_results=simulation_results,
                    iteration_number=iteration_number-1
                )
                
                # 检查是否获取到有效参数
                if not optimized_params:
                    logger.error("未能从DeepSeek获取有效的参数建议，终止优化流程")
                    break
                
                # 应用优化参数并运行仿真
                # 合并参数：确保即使DeepSeek只返回部分参数，也能保持参数集的完整性
                merged_params = current_params.copy() # 从上一轮完整参数开始
                if optimized_params: # 检查 DeepSeek 是否返回了参数
                    merged_params.update(optimized_params) # 用 DeepSeek 的建议更新
                    logger.info(f"DeepSeek建议的参数已合并: {optimized_params}")
                else:
                    logger.warning("DeepSeek未返回有效参数，将使用上一轮参数运行")
                
                current_params = merged_params # 使用合并后的参数进行下一轮
                current_params, simulation_results = self.run_simulation_cycle(current_params)
                # self._update_best_results(simulation_results, current_params) # 旧方法
                # 存储迭代数据
                self._store_iteration_data(
                    iteration=iteration_number, 
                    params=current_params, 
                    results=simulation_results,
                    optimized_params=optimized_params,
                    node_id=simulation_results.get('leaf_node_id', 'unknown')
                )

                # 生成本次迭代报告
                self.report_generator.generate_iteration_report(
                    iteration=iteration_number,
                    params=current_params,
                    results=simulation_results,
                    optimized_params=optimized_params, # 传递 DeepSeek 的建议（可能为空）
                    deepseek_thought=deepseek_raw_response # 传递 DeepSeek 原始响应
                )

                # 每 3 次迭代生成一次 DeepSeek 总结报告
                if iteration_number >= 3 and iteration_number % 3 == 0:
                    self.generate_intermediate_summary(start_iter=iteration_number - 2, end_iter=iteration_number)

                # 检查性能目标是否已达到
                if self.check_performance_target():
                    logger.info("性能目标已达到，停止优化")
                    break
            
            logger.info(f"完整仿真流程已完成，共执行了{iteration_number}次迭代")
            logger.info(f"总历史记录条数: {len(self.iteration_history)}")

            # 生成最终总结报告 (使用完整的历史记录)
            self.report_generator.generate_summary_report(self.iteration_history)

            return self.iteration_history # 返回完整的历史记录
            # ---- 主要仿真逻辑结束 ----
            
        except KeyboardInterrupt:
            logger.warning("接收到中断信号 (KeyboardInterrupt)，正在停止仿真流程...")
            # 这里可以添加额外的特定于中断的清理逻辑（如果需要）
            # 例如，保存当前状态或生成一个中断报告
            return None # 或者返回部分历史记录 self.iteration_history
        
        except Exception as e:
            logger.error(f"完整仿真流程失败: {str(e)}")
            logger.error(traceback.format_exc())
            # 可以在这里生成错误报告
            return None
        finally:
            # 无论如何，最后尝试执行清理
            logger.info("执行清理操作...")
            self.cleanup() # 确保调用清理方法
    
    def cleanup(self):
        """清理资源"""
        if not self.use_fake_results:
            self.swb_interaction.close_connection()
            
        logger.info("资源已清理")

    def generate_intermediate_summary(self, start_iter: int, end_iter: int):
        """调用 DeepSeek 生成中间总结报告"""
        if not self.iteration_history or len(self.iteration_history) < (end_iter - start_iter + 1):
            self.logger.warning(f"历史数据不足，无法生成 {start_iter}-{end_iter} 轮的中间总结报告。")
            return
            
        # 获取最近 N 轮的数据
        relevant_history = self.iteration_history[-(end_iter - start_iter + 1):]
        if not relevant_history or relevant_history[0]['iteration'] != start_iter:
             self.logger.warning(f"获取的迭代历史范围 ({relevant_history[0]['iteration']}?) 与请求的 {start_iter}-{end_iter} 不匹配。")
             # 可以尝试更精确的切片或查找，但这里简化处理
             relevant_history = self.iteration_history[-3:] # 简单取最后三个
             if len(relevant_history) < 3:
                  self.logger.warning(f"无法获取足够的历史数据进行总结。")
                  return
             start_iter = relevant_history[0]['iteration']
             end_iter = relevant_history[-1]['iteration']
             self.logger.warning(f"将尝试总结实际获取到的最后三轮: {start_iter}-{end_iter}")

        self.logger.info(f"准备为第 {start_iter}-{end_iter} 轮生成 DeepSeek 中间总结报告...")
        try:
            summary_content = self.deepseek_interaction.get_intermediate_summary(relevant_history)
            if summary_content:
                self.report_generator.save_intermediate_summary(summary_content, start_iter, end_iter)
            else:
                self.logger.error("DeepSeek未能生成有效的中间总结内容。")
        except Exception as e:
            self.logger.error(f"生成中间总结报告时出错: {e}")
            self.logger.error(traceback.format_exc())

    def update_params_history(self, iteration, params, results):
        """
        更新参数历史记录
        
        Args:
            iteration (int): 迭代次数
            params (dict): 参数字典
            results (dict): 结果字典
        """
        history_entry = {
            'iteration': iteration,
            'params': params.copy() if params else {},
            'results': results.copy() if results else {},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 确保history目录存在
        history_dir = self.project_path / "Results" / "History"
        history_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存当前迭代结果
        history_file = history_dir / f"iteration_{iteration}.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(history_entry, f, indent=2)
            self.logger.info(f"保存了迭代{iteration}的历史记录到 {history_file}")
        except Exception as e:
            self.logger.error(f"保存历史记录失败: {str(e)}")
    
    def generate_final_report(self):
        """生成最终报告，包括所有迭代的结果和最佳配置"""
        try:
            report_dir = self.project_path / "Results" / "Reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_file = report_dir / "final_report.md"
            
            best_result = self.get_best_result_so_far()
            
            with open(report_file, 'w') as f:
                f.write("# Sentaurus自动化仿真最终报告\n\n")
                f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 总结
                f.write("## 总体结果\n\n")
                if best_result:
                    f.write(f"* 最佳结果来自第 {best_result.get('iteration', 'unknown')} 次迭代\n")
                    f.write(f"* 阳极电压: {best_result.get('vanode', 'N/A')} V\n")
                    f.write(f"* 闩锁状态: {'是' if best_result.get('is_latchup', True) else '否'}\n")
                    
                    # 参数表格
                    f.write("\n## 最佳参数配置\n\n")
                    f.write("| 参数 | 值 |\n")
                    f.write("|------|------|\n")
                    for param, value in best_result.get('params', {}).items():
                        f.write(f"| {param} | {value} |\n")
                    
                    # 如果有图表
                    figure_path = best_result.get('figure_path')
                    if figure_path and os.path.exists(figure_path):
                        rel_path = os.path.relpath(figure_path, os.path.dirname(report_file))
                        f.write(f"\n## 仿真结果图表\n\n")
                        f.write(f"![仿真结果]({rel_path})\n")
                else:
                    f.write("没有找到满足条件的有效结果。\n")
                
                # 迭代历史
                f.write("\n## 迭代历史\n\n")
                history_dir = self.project_path / "Results" / "History"
                history_files = sorted(list(history_dir.glob("iteration_*.json")))
                
                for history_file in history_files:
                    try:
                        with open(history_file, 'r') as hf:
                            history = json.load(hf)
                            
                            iteration = history.get('iteration', 'unknown')
                            timestamp = history.get('timestamp', 'unknown')
                            params = history.get('params', {})
                            results = history.get('results', {})
                            
                            f.write(f"### 迭代 {iteration} ({timestamp})\n\n")
                            
                            # 参数
                            f.write("#### 参数配置\n\n")
                            f.write("| 参数 | 值 |\n")
                            f.write("|------|------|\n")
                            for param, value in params.items():
                                f.write(f"| {param} | {value} |\n")
                            
                            # 结果
                            f.write("\n#### 仿真结果\n\n")
                            f.write("| 指标 | 值 |\n")
                            f.write("|------|------|\n")
                            for metric, value in results.items():
                                f.write(f"| {metric} | {value} |\n")
                            
                            f.write("\n")
                    except Exception as e:
                        self.logger.error(f"读取历史文件 {history_file} 失败: {str(e)}")
                        f.write(f"读取迭代历史失败: {str(e)}\n\n")
            
            self.logger.info(f"生成了最终报告: {report_file}")
            
        except Exception as e:
            self.logger.error(f"生成最终报告失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def get_initial_params(self):
        """
        获取初始参数
        
        Returns:
            dict: 初始参数字典
        """
        try:
            # 修改查找路径，优先读取指定的 initial_params.json 文件
            params_file = self.project_path / "Parameter" / "Initial_Parameter" / "initial_params.json"
            initial_params = {}
            
            if params_file.exists():
                try:
                    with open(params_file, 'r') as f:
                        initial_params = json.load(f)
                    self.logger.info(f"成功从文件加载初始参数: {params_file}")
                except Exception as e:
                    self.logger.error(f"加载初始参数文件 {params_file} 失败: {str(e)}")
                    # 如果文件存在但加载失败，返回空字典，避免使用默认值
                    return {}
            else:
                 self.logger.warning(f"指定的初始参数文件不存在: {params_file}")
                 # 如果指定文件不存在，尝试从 config.json 获取
                 initial_params = self.config.get('initial_params', {})
                 if initial_params:
                     self.logger.info("从 config.json 加载初始参数")
                 else:
                    # 最后才使用硬编码的默认值 (更新为 IGBT 相关默认值)
                    initial_params = {
                        "Xmax": 6,
                        "Wgate": 1.8,
                        "Wnplus": 0.5,
                        "Wpplus": 1.5,
                        "Wemitter": 1.8,
                        "Ymax": 100,
                        "Ygate": 5,
                        "Ypplus": 0.5,
                        "Ynplus": 0.5,
                        "Ypbase": 3,
                        "Hnbuffer": 4,
                        "Hcollector": 0.5,
                        "Ndrift": 5e13,
                        "Pbase": 2.5e17,
                        "Pplus": 1e19,
                        "Nplus": 1e19,
                        "Nbuffer": 5e15,
                        "Pcollector": 1e17,
                        "Tox_sidewall": 0.1,
                        "Tox_bottom": 0.12
                    }
                    self.logger.warning("未找到任何初始参数文件，使用硬编码的 IGBT 默认参数")
            
            self.logger.info(f"最终使用的初始参数: {initial_params}")
            return initial_params
            
        except Exception as e:
            self.logger.error(f"获取初始参数失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {}

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Sentaurus自动化仿真系统")
    parser.add_argument("--project", "--project-path", type=str, help="Sentaurus项目路径")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--max-iterations", type=int, default=10, help="最大迭代次数")
    parser.add_argument("--api-key", type=str, help="DeepSeek API密钥")
    parser.add_argument("--fake-results", action="store_true", help="使用假的仿真结果（测试用）")
    args = parser.parse_args()
    
    # 获取配置
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
                logger.info(f"已从文件加载配置: {args.config}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return 1
    
    # 命令行参数优先级高于配置文件
    project_path = args.project or config.get("project_path", ".")
    max_iterations = args.max_iterations or config.get("max_iterations", 10)
    api_key = args.api_key or config.get("api_key")
    use_fake_results = args.fake_results or config.get("use_fake_results", False)
    
    try:
        auto_sim = AutoSimulation(
            project_path, 
            max_iterations, 
            api_key, 
            use_fake_results
        )
        
        # 如果配置中指定跳过确认，覆盖verify_initial_parameters方法
        if config.get("skip_confirmation", False):
            auto_sim.verify_initial_parameters = lambda: True
            logger.info("已配置跳过参数确认")
        
        # 如果配置中有性能目标，覆盖默认值
        if "performance_target" in config:
            auto_sim.performance_target = config["performance_target"]
            logger.info(f"已设置性能目标: {auto_sim.performance_target}")
        
        # 如果配置中有参数变化设置
        if "parameter_variation" in config and config["parameter_variation"].get("enabled", False):
            # 这里可以添加参数变化的设置代码
            pass
        
        success = auto_sim.run_complete_flow(auto_sim.get_initial_params())
        
        if success:
            print("\n自动化仿真流程成功完成！")
            best_result = auto_sim.get_best_result_so_far()
            if best_result:
                print(f"最佳结果: 迭代{best_result['iteration']}, 阳极电压={best_result.get('vanode', 'N/A')}V")
                print(f"请查看最终报告获取详细信息: {project_path}/Reports/final_report.md")
            else:
                print("未找到满足性能目标的结果")
        else:
            print("\n自动化仿真流程失败！")
            print(f"请查看错误报告: {project_path}/Reports/error_report.md")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        logger.error(f"主函数错误: {str(e)}")
        logger.error(traceback.format_exc())
        return 1
    finally:
        if 'auto_sim' in locals():
            auto_sim.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
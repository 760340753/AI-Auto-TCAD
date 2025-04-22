#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化仿真运行器模块，负责集成参数优化和结果分析功能，
自动执行Sentaurus Workbench仿真任务并应用参数优化
"""

import os
import sys
import time
import json
import logging
import argparse
from pathlib import Path

from auto_sim.parameter_optimizer import ParameterOptimizer
from auto_sim.result_analyzer import ResultAnalyzer
from auto_sim.swb_automation import SWBAutomation

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_sim_runner.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("auto_sim.runner")

class AutomatedSimulationRunner:
    """自动化仿真运行器，负责协调运行优化流程"""
    
    def __init__(self, project_path, config_file=None):
        """
        初始化自动化仿真运行器
        
        Args:
            project_path: SWB项目路径
            config_file: 配置文件路径
        """
        self.project_path = Path(project_path)
        
        # 确保目录存在
        os.makedirs(self.project_path, exist_ok=True)
        
        # 加载配置
        self.config = self.load_config(config_file)
        
        # 初始化SWB自动化
        self.swb = SWBAutomation(self.project_path)
        
        # 初始化结果分析器
        self.result_analyzer = ResultAnalyzer(self.project_path)
        
        # 初始化参数优化器
        self.parameter_optimizer = ParameterOptimizer(
            self.project_path,
            initial_params=self.config.get("initial_params", {}),
            param_constraints=self.config.get("param_constraints", {})
        )
        
        # 记录运行状态
        self.state = {
            "current_iteration": 0,
            "max_iterations": self.config.get("max_iterations", 5),
            "started_at": None,
            "last_update": None,
            "status": "initialized"
        }
        
    def load_config(self, config_file=None):
        """
        加载配置文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            dict: 配置数据
        """
        default_config = {
            "project_name": "MCT-SEE",
            "max_iterations": 5,
            "auto_run": True,
            "wait_time": 10,  # 等待时间(秒)
            "initial_params": {
                # 默认参数
                "Wtot": 4.0,     # 有源区总宽度 (μm)
                "Wg": 0.4,       # P+阱宽度 (μm)
                "L": 1.5,        # 沟道长度 (μm)
                "Nemitter": 1.0e20,  # N+区掺杂浓度 (cm^-3)
                "Nbase": 5.0e17,     # P基区掺杂浓度 (cm^-3)
                "Ndrift": 2.0e14,    # N漂移区掺杂浓度 (cm^-3)
                "Xjn": 0.5,      # N+区结深 (μm)
                "Xjsw": 1.0,     # P基区结深 (μm)
                "Tdrift": 50.0,   # N漂移区厚度 (μm)
                "LET": 60.0,     # 线性能量传输率 (MeV·cm²/mg)
                "Voltage": 30.0   # 工作电压 (V)
            },
            "param_constraints": {
                # 参数约束
                "Wtot": {"min": 1.0, "max": 10.0},
                "Wg": {"min": 0.1, "max": 2.0},
                "L": {"min": 0.5, "max": 5.0},
                "Nemitter": {"min": 1.0e19, "max": 1.0e21},
                "Nbase": {"min": 1.0e16, "max": 1.0e18},
                "Ndrift": {"min": 1.0e13, "max": 1.0e15},
                "Xjn": {"min": 0.1, "max": 1.0},
                "Xjsw": {"min": 0.5, "max": 2.0},
                "Tdrift": {"min": 20.0, "max": 100.0},
                "LET": {"min": 10.0, "max": 100.0},
                "Voltage": {"min": 10.0, "max": 50.0}
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"已从 {config_file} 加载配置")
                
                # 合并默认配置和加载的配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                
                return config
            except Exception as e:
                logger.error(f"加载配置文件时出错: {str(e)}")
                
        logger.info("使用默认配置")
        return default_config
    
    def save_state(self):
        """保存当前运行状态到文件"""
        state_file = self.project_path / "auto_sim_state.json"
        self.state["last_update"] = time.time()
        
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.debug("已保存运行状态")
        except Exception as e:
            logger.error(f"保存运行状态时出错: {str(e)}")
    
    def load_state(self):
        """从文件加载运行状态"""
        state_file = self.project_path / "auto_sim_state.json"
        
        if not state_file.exists():
            logger.info("没有找到状态文件，将使用初始状态")
            return
            
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                saved_state = json.load(f)
                
            for key, value in saved_state.items():
                self.state[key] = value
                
            logger.info(f"已加载运行状态，当前迭代: {self.state['current_iteration']}")
        except Exception as e:
            logger.error(f"加载运行状态时出错: {str(e)}")
    
    def update_parameters(self, params):
        """
        更新SWB项目参数
        
        Args:
            params: 要更新的参数字典
            
        Returns:
            bool: 是否成功更新
        """
        try:
            # 打开项目
            self.swb.open_project()
            
            # 更新参数
            for param_name, param_value in params.items():
                self.swb.set_parameter(param_name, param_value)
                
            # 保存项目
            self.swb.save_project()
            logger.info("已更新SWB项目参数")
            return True
        except Exception as e:
            logger.error(f"更新SWB项目参数时出错: {str(e)}")
            return False
    
    def run_iteration(self):
        """
        运行一次优化迭代
        
        Returns:
            bool: 是否成功完成迭代
        """
        try:
            # 更新状态
            self.state["current_iteration"] += 1
            self.state["status"] = "running"
            self.save_state()
            
            current_iter = self.state["current_iteration"]
            logger.info(f"开始第 {current_iter} 次迭代")
            
            # 获取当前参数
            current_params = self.parameter_optimizer.current_params
            
            # 更新SWB项目参数
            if not self.update_parameters(current_params):
                logger.error("更新参数失败，中止本次迭代")
                return False
                
            # 添加新实验
            experiment_name = f"Iter_{current_iter}"
            logger.info(f"添加新实验: {experiment_name}")
            
            # 添加实验并获取节点ID
            experiment_node_id = self.swb.add_experiment(experiment_name)
            if not experiment_node_id:
                logger.error("添加实验失败，中止本次迭代")
                return False
                
            # 运行实验
            logger.info(f"运行实验 {experiment_name}，节点ID: {experiment_node_id}")
            self.swb.run_experiment(experiment_node_id)
            
            # 等待实验完成
            max_wait_time = self.config.get("max_wait_time", 7200)  # 默认最长等待2小时
            wait_interval = self.config.get("wait_interval", 30)    # 默认每30秒检查一次
            
            total_wait_time = 0
            while total_wait_time < max_wait_time:
                status = self.swb.get_experiment_status(experiment_node_id)
                logger.info(f"实验状态: {status}")
                
                if status == "done":
                    logger.info(f"实验 {experiment_name} 已完成")
                    break
                elif status in ["failed", "error", "killed"]:
                    logger.error(f"实验 {experiment_name} 失败，状态: {status}")
                    self.state["status"] = "failed"
                    self.save_state()
                    return False
                    
                logger.info(f"等待实验完成，已等待 {total_wait_time} 秒...")
                time.sleep(wait_interval)
                total_wait_time += wait_interval
                
            if total_wait_time >= max_wait_time:
                logger.error(f"等待实验完成超时 (>{max_wait_time}秒)")
                self.state["status"] = "timeout"
                self.save_state()
                return False
                
            # 分析实验结果
            logger.info("分析实验结果")
            result = self.result_analyzer.analyze_simulation_result(experiment_node_id)
            
            if not result:
                logger.error("无法获取实验结果")
                self.state["status"] = "failed"
                self.save_state()
                return False
                
            # 优化参数
            logger.info("根据结果优化参数")
            optimized_params = self.parameter_optimizer.optimize_parameters(
                experiment_node_id, 
                current_iter,
                max_iterations=self.state["max_iterations"]
            )
            
            # 保存参数优化器状态
            self.parameter_optimizer.save_optimization_history()
            
            # 更新状态
            self.state["status"] = "completed_iteration"
            self.save_state()
            
            logger.info(f"完成第 {current_iter} 次迭代")
            return True
            
        except Exception as e:
            logger.error(f"运行迭代时出错: {str(e)}")
            self.state["status"] = "error"
            self.save_state()
            return False
            
    def run_optimization_loop(self):
        """
        运行完整的优化循环
        """
        try:
            # 设置开始时间
            self.state["started_at"] = time.time()
            self.state["status"] = "starting"
            self.save_state()
            
            logger.info("开始优化循环")
            
            while self.state["current_iteration"] < self.state["max_iterations"]:
                success = self.run_iteration()
                
                if not success:
                    logger.error("迭代失败，中止优化循环")
                    break
                    
                # 保存优化历史
                self.parameter_optimizer.save_optimization_history()
                
            # 循环完成
            if self.state["current_iteration"] >= self.state["max_iterations"]:
                logger.info(f"已完成所有 {self.state['max_iterations']} 次迭代")
                self.state["status"] = "completed"
            
            self.save_state()
            
            # 生成优化报告
            self.generate_optimization_report()
            
        except Exception as e:
            logger.error(f"运行优化循环时出错: {str(e)}")
            self.state["status"] = "error"
            self.save_state()
            
    def generate_optimization_report(self):
        """
        生成优化报告
        """
        try:
            report_file = self.project_path / "optimization_report.txt"
            history = self.parameter_optimizer.optimization_history
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("===== 参数优化报告 =====\n\n")
                f.write(f"项目路径: {self.project_path}\n")
                f.write(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"迭代次数: {self.state['current_iteration']}\n\n")
                
                f.write("初始参数:\n")
                for param, value in self.parameter_optimizer.initial_params.items():
                    f.write(f"  {param}: {value}\n")
                    
                f.write("\n最终参数:\n")
                for param, value in self.parameter_optimizer.current_params.items():
                    f.write(f"  {param}: {value}\n")
                
                f.write("\n参数变化:\n")
                param_diff = self.parameter_optimizer.compare_parameters(
                    self.parameter_optimizer.initial_params,
                    self.parameter_optimizer.current_params
                )
                
                for param, diff in param_diff.items():
                    change = ""
                    if "percent_change" in diff:
                        change = f" (变化: {diff['percent_change']}%)"
                    f.write(f"  {param}: {diff['before']} -> {diff['after']}{change}\n")
                
                f.write("\n优化历史:\n")
                for i, record in enumerate(history):
                    f.write(f"\n  迭代 {i+1}:\n")
                    f.write(f"    仿真ID: {record['sim_id']}\n")
                    
                    if "result" in record:
                        f.write("    仿真结果:\n")
                        for key, value in record["result"].items():
                            f.write(f"      {key}: {value}\n")
                            
                    if "ai_response" in record:
                        f.write(f"    AI分析: {record['ai_response'][:100]}...\n")
                    
            logger.info(f"已生成优化报告: {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"生成优化报告时出错: {str(e)}")
            return False
            
    def run_single_simulation(self, params=None, experiment_name=None):
        """
        运行单次仿真
        
        Args:
            params: 要使用的参数字典，None表示使用当前参数
            experiment_name: 实验名称
            
        Returns:
            dict: 仿真结果
        """
        try:
            # 使用提供的参数或当前参数
            if params is None:
                params = self.parameter_optimizer.current_params
                
            # 生成实验名称
            if experiment_name is None:
                experiment_name = f"Single_Sim_{int(time.time())}"
                
            logger.info(f"运行单次仿真: {experiment_name}")
            
            # 更新SWB项目参数
            if not self.update_parameters(params):
                logger.error("更新参数失败，中止仿真")
                return None
                
            # 添加实验并获取节点ID
            experiment_node_id = self.swb.add_experiment(experiment_name)
            if not experiment_node_id:
                logger.error("添加实验失败，中止仿真")
                return None
                
            # 运行实验
            logger.info(f"运行实验 {experiment_name}，节点ID: {experiment_node_id}")
            self.swb.run_experiment(experiment_node_id)
            
            # 等待实验完成
            max_wait_time = self.config.get("max_wait_time", 7200)  # 默认最长等待2小时
            wait_interval = self.config.get("wait_interval", 30)    # 默认每30秒检查一次
            
            total_wait_time = 0
            while total_wait_time < max_wait_time:
                status = self.swb.get_experiment_status(experiment_node_id)
                logger.info(f"实验状态: {status}")
                
                if status == "done":
                    logger.info(f"实验 {experiment_name} 已完成")
                    break
                elif status in ["failed", "error", "killed"]:
                    logger.error(f"实验 {experiment_name} 失败，状态: {status}")
                    return None
                    
                logger.info(f"等待实验完成，已等待 {total_wait_time} 秒...")
                time.sleep(wait_interval)
                total_wait_time += wait_interval
                
            if total_wait_time >= max_wait_time:
                logger.error(f"等待实验完成超时 (>{max_wait_time}秒)")
                return None
                
            # 分析实验结果
            logger.info("分析实验结果")
            result = self.result_analyzer.analyze_simulation_result(experiment_node_id)
            
            if not result:
                logger.error("无法获取实验结果")
                return None
                
            return {
                "node_id": experiment_node_id,
                "experiment_name": experiment_name,
                "parameters": params,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"运行单次仿真时出错: {str(e)}")
            return None
            
    def run_parameter_sweep(self, param_name, values, fixed_params=None):
        """
        运行参数扫描，测试某个参数不同值的效果
        
        Args:
            param_name: 要扫描的参数名
            values: 参数值列表
            fixed_params: 固定参数字典，不提供则使用当前参数
            
        Returns:
            list: 仿真结果列表
        """
        try:
            logger.info(f"开始参数扫描: {param_name}, 值: {values}")
            
            # 生成实验矩阵
            experiment_matrix = self.parameter_optimizer.suggest_experiment_matrix(
                param_name, values, fixed_params
            )
            
            # 运行每个实验
            results = []
            for i, params in enumerate(experiment_matrix):
                experiment_name = f"Sweep_{param_name}_{i+1}"
                result = self.run_single_simulation(params, experiment_name)
                
                if result:
                    results.append(result)
                    
            # 保存扫描结果
            sweep_results_file = self.project_path / f"sweep_{param_name}_{int(time.time())}.json"
            
            try:
                with open(sweep_results_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                logger.info(f"已保存参数扫描结果: {sweep_results_file}")
            except Exception as e:
                logger.error(f"保存参数扫描结果时出错: {str(e)}")
                
            return results
            
        except Exception as e:
            logger.error(f"运行参数扫描时出错: {str(e)}")
            return []
            
def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化仿真运行器")
    parser.add_argument("--project", "-p", required=True, help="SWB项目路径")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--mode", "-m", default="optimize", 
                      choices=["optimize", "single", "sweep"],
                      help="运行模式: optimize(参数优化), single(单次运行), sweep(参数扫描)")
    parser.add_argument("--param", help="参数扫描时的参数名")
    parser.add_argument("--values", help="参数扫描时的参数值列表，以逗号分隔")
    
    args = parser.parse_args()
    
    # 创建自动化运行器
    runner = AutomatedSimulationRunner(args.project, args.config)
    
    # 根据模式运行
    if args.mode == "optimize":
        runner.load_state()
        runner.run_optimization_loop()
    elif args.mode == "single":
        result = runner.run_single_simulation()
        if result:
            print(f"仿真结果: {json.dumps(result['result'], indent=2)}")
    elif args.mode == "sweep":
        if not args.param:
            parser.error("参数扫描模式需要指定参数名 (--param)")
            
        if not args.values:
            parser.error("参数扫描模式需要指定参数值列表 (--values)")
            
        # 解析参数值
        try:
            values = [float(x) for x in args.values.split(",")]
        except ValueError:
            parser.error("参数值必须是逗号分隔的数值列表")
            
        results = runner.run_parameter_sweep(args.param, values)
        
        if results:
            print(f"参数扫描完成，共 {len(results)} 个实验")
            
if __name__ == "__main__":
    main() 
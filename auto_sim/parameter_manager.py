#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数管理模块，用于处理仿真参数的读取、验证和更新
"""
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("auto_sim.parameter_manager")

class ParameterManager:
    """参数管理类"""
    
    def __init__(self, project_path):
        """
        初始化参数管理器
        
        Args:
            project_path: Sentaurus项目路径
        """
        self.project_path = Path(project_path)
        self.initial_params_path = self.project_path / "Parameter" / "Initial_Parameter" / "initial_params.json"
        self.generated_params_dir = self.project_path / "Parameter" / "Generated_Parameter"
        
        # 确保目录存在
        os.makedirs(self.generated_params_dir, exist_ok=True)
    
    def initial_params_exist(self):
        """检查初始参数文件是否存在"""
        return self.initial_params_path.exists()
    
    def create_example_params(self):
        """创建示例参数文件"""
        example_params = {
            "Wtot": 50,
            "Wg": 10,
            "Wcp": 10,
            "Wcs": 4,
            "Tdrift": 350,
            "TPc": 0.2,
            "TNb": 1.5,
            "TNa": 1.5,
            "TPb": 4,
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
            "Length": 9,
            "Vanode": 300,  # 添加SDevice参数
            "angle": 90     # 添加SDevice参数
        }
        
        try:
            with open(self.initial_params_path, 'w') as f:
                json.dump(example_params, f, indent=4)
            
            logger.info(f"已创建示例参数文件: {self.initial_params_path}")
            return True
        except Exception as e:
            logger.error(f"创建示例参数文件时出错: {str(e)}")
            return False
    
    def get_initial_params(self):
        """获取初始参数"""
        if not self.initial_params_exist():
            logger.error("初始参数文件不存在")
            return None
        
        try:
            with open(self.initial_params_path, 'r') as f:
                params = json.load(f)
                logger.info("成功读取初始参数")
                return params
        except Exception as e:
            logger.error(f"读取初始参数时出错: {str(e)}")
            return None
    
    def save_iteration_params(self, iteration, params):
        """保存迭代参数"""
        file_path = self.generated_params_dir / f"iteration_{iteration}_params.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(params, f, indent=4)
                
            logger.info(f"已保存第 {iteration} 次迭代参数")
            return True
        except Exception as e:
            logger.error(f"保存迭代参数时出错: {str(e)}")
            return False
    
    def get_iteration_params(self, iteration):
        """获取特定迭代的参数"""
        file_path = self.generated_params_dir / f"iteration_{iteration}_params.json"
        
        if not file_path.exists():
            logger.error(f"第 {iteration} 次迭代参数文件不存在")
            return None
        
        try:
            with open(file_path, 'r') as f:
                params = json.load(f)
                logger.info(f"成功读取第 {iteration} 次迭代参数")
                return params
        except Exception as e:
            logger.error(f"读取迭代参数时出错: {str(e)}")
            return None
    
    def validate_params(self, params):
        """验证参数有效性"""
        # IGBT 参数必需键列表
        required_keys = [
            "Xmax", "Wgate", "Wnplus", "Wpplus", "Wemitter",
            "Ymax", "Ygate", "Ypplus", "Ynplus", "Ypbase",
            "Hnbuffer", "Hcollector", 
            "Ndrift", "Pbase", "Pplus", "Nplus", "Nbuffer", "Pcollector",
            "Tox_sidewall", "Tox_bottom"
        ]
        
        for key in required_keys:
            if key not in params:
                logger.error(f"参数缺失: {key}")
                return False
        
        logger.info("参数验证通过")
        return True
    
    def update_params_from_deepseek(self, iteration, deepseek_response):
        """从DeepSeek响应更新参数"""
        try:
            # 假设DeepSeek响应中包含一个parameters字段
            new_params = deepseek_response.get("parameters", {})
            
            # 获取上一次的参数作为基础
            if iteration == 1:
                base_params = self.get_initial_params()
            else:
                base_params = self.get_iteration_params(iteration - 1)
            
            if not base_params:
                logger.error("无法获取基础参数")
                return False
            
            # 更新参数
            updated_params = base_params.copy()
            updated_params.update(new_params)
            
            # 验证更新后的参数
            if not self.validate_params(updated_params):
                logger.error("更新后的参数验证失败")
                return False
            
            # 保存更新后的参数
            return self.save_iteration_params(iteration, updated_params)
            
        except Exception as e:
            logger.error(f"从DeepSeek更新参数时出错: {str(e)}")
            return False
    
    def get_current_params(self):
        """
        获取当前迭代参数，如果当前迭代参数不存在，则使用初始参数
        
        Returns:
            dict: 当前参数
        """
        # 尝试从最近的迭代获取参数
        for i in range(100, 0, -1):  # 从高迭代次数向低迭代次数查找
            params_file = self.generated_params_dir / f"iteration_{i}_params.json"
            if params_file.exists():
                try:
                    with open(params_file, 'r') as f:
                        params = json.load(f)
                    logger.info(f"使用第 {i} 次迭代的参数")
                    return params
                except Exception as e:
                    logger.error(f"读取第 {i} 次迭代参数失败: {str(e)}")
        
        # 如果找不到现有迭代参数，使用初始参数
        initial_params = self.get_initial_params()
        if initial_params:
            logger.info("使用初始参数")
            return initial_params
        
        # 如果还是找不到，创建并使用示例参数
        logger.warning("未找到任何参数，创建示例参数")
        self.create_example_params()
        return self.get_initial_params()
    
    def set_current_params(self, params):
        """
        设置当前参数
        
        Args:
            params: 当前参数字典
        """
        # 找到当前迭代号
        current_iteration = 1
        for i in range(1, 100):
            params_file = self.generated_params_dir / f"params_iteration_{i}.json"
            if not params_file.exists():
                current_iteration = i
                break
        
        # 保存到当前迭代文件
        params_file = self.generated_params_dir / f"params_iteration_{current_iteration}.json"
        try:
            with open(params_file, 'w') as f:
                json.dump(params, f, indent=4)
            logger.info(f"已保存当前参数到: {params_file}")
        except Exception as e:
            logger.error(f"保存当前参数失败: {str(e)}") 
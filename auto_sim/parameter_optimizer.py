#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
参数优化器模块 - 用于优化TCAD仿真参数
"""

import os
import time
import json
import logging
import numpy as np
import pandas as pd
from scipy import optimize
from typing import Dict, List, Tuple, Callable, Union, Any, Optional

class ParameterOptimizer:
    """
    参数优化器类
    用于优化TCAD仿真参数，以找到满足目标函数的最佳参数组合
    """
    
    def __init__(self, analyzer=None):
        """
        初始化参数优化器
        
        Args:
            analyzer: 结果分析器实例(可选)
        """
        self.logger = logging.getLogger('ParameterOptimizer')
        self.analyzer = analyzer
        self.parameters = {}
        self.optimization_history = []
        self.best_result = None
        
        # 初始化日志配置
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
        self.logger.info("初始化参数优化器")
    
    def set_analyzer(self, analyzer):
        """
        设置结果分析器
        
        Args:
            analyzer: 结果分析器实例
        """
        self.analyzer = analyzer
        self.logger.info("设置结果分析器")
        
    def add_parameter(self, name: str, min_value: float, max_value: float, 
                    step: float = None, units: str = None, description: str = None):
        """
        添加要优化的参数
        
        Args:
            name: 参数名称
            min_value: 最小值
            max_value: 最大值
            step: 步长(可选)
            units: 单位(可选)
            description: 参数描述(可选)
        """
        self.parameters[name] = {
            'min': min_value,
            'max': max_value,
            'step': step,
            'units': units,
            'description': description
        }
        self.logger.info(f"添加参数: {name}, 范围: [{min_value}, {max_value}] {units if units else ''}")
        
    def add_parameters(self, parameters: Dict):
        """
        批量添加多个参数
        
        Args:
            parameters: 参数配置字典，格式如下：
            {
                "param1": {"min": 1.0, "max": 10.0, "step": 0.1, "units": "nm", "description": "..."},
                "param2": {"min": 1e15, "max": 1e19, "step": None, "units": "cm^-3", "description": "..."}
            }
        """
        for name, config in parameters.items():
            self.add_parameter(
                name, 
                config.get('min'), 
                config.get('max'), 
                config.get('step'),
                config.get('units'),
                config.get('description')
            )
            
    def remove_parameter(self, name: str):
        """
        移除参数
        
        Args:
            name: 参数名称
        """
        if name in self.parameters:
            del self.parameters[name]
            self.logger.info(f"移除参数: {name}")
        else:
            self.logger.warning(f"参数不存在: {name}")
            
    def clear_parameters(self):
        """清除所有参数"""
        self.parameters = {}
        self.logger.info("清除所有参数")
        
    def _validate_objective_function(self, objective_function: Callable):
        """
        验证目标函数是否有效
        
        Args:
            objective_function: 目标函数
            
        Returns:
            bool: 目标函数是否有效
        """
        if not callable(objective_function):
            self.logger.error("目标函数必须是可调用对象")
            return False
            
        # 检查目标函数是否接受参数字典
        try:
            # 创建一个包含所有参数中点值的测试字典
            test_params = {}
            for name, config in self.parameters.items():
                test_params[name] = (config['min'] + config['max']) / 2
                
            # 尝试调用目标函数
            objective_function(test_params)
            return True
        except Exception as e:
            self.logger.error(f"目标函数验证失败: {str(e)}")
            return False
            
    def _objective_wrapper(self, params_array: np.ndarray, param_names: List[str], 
                        objective_function: Callable) -> float:
        """
        包装目标函数以接受数组形式的参数
        
        Args:
            params_array: 参数数组
            param_names: 参数名称列表
            objective_function: 原始目标函数
            
        Returns:
            float: 目标函数的评估结果
        """
        # 将数组转换为字典
        params_dict = {name: value for name, value in zip(param_names, params_array)}
        
        # 记录本次评估到历史记录
        entry = params_dict.copy()
        
        try:
            # 调用目标函数
            result = objective_function(params_dict)
            
            # 记录结果
            entry['objective_value'] = result
            entry['timestamp'] = time.time()
            
            # 更新最佳结果
            if self.best_result is None or result < self.best_result['objective_value']:
                self.best_result = entry.copy()
                
            self.logger.info(f"参数评估: {params_dict}, 结果: {result}")
            
            self.optimization_history.append(entry)
            return result
        except Exception as e:
            self.logger.error(f"目标函数评估失败: {str(e)}")
            # 对于优化算法，返回一个大值表示失败
            result = 1e10
            entry['objective_value'] = result
            entry['error'] = str(e)
            entry['timestamp'] = time.time()
            self.optimization_history.append(entry)
            return result
    
    def optimize(self, objective_function: Callable, method: str = 'differential_evolution', 
                max_iterations: int = 100, tolerance: float = 1e-3, **kwargs) -> Dict:
        """
        执行参数优化
        
        Args:
            objective_function: 目标函数，接受参数字典并返回一个要最小化的标量值
            method: 优化方法，支持 'grid_search', 'differential_evolution', 'nelder_mead', 'powell', 'bfgs'
            max_iterations: 最大迭代次数
            tolerance: 收敛容差
            **kwargs: 传递给优化器的其他参数
            
        Returns:
            Dict: 包含最佳参数和优化结果的字典
        """
        if not self.parameters:
            self.logger.error("没有参数可供优化")
            return {'success': False, 'message': '没有参数可供优化'}
            
        if not self._validate_objective_function(objective_function):
            return {'success': False, 'message': '目标函数无效'}
            
        # 重置优化历史和最佳结果
        self.optimization_history = []
        self.best_result = None
        
        # 获取参数名称和边界
        param_names = list(self.parameters.keys())
        bounds = [(self.parameters[name]['min'], self.parameters[name]['max']) 
                 for name in param_names]
                 
        # 创建包装的目标函数
        wrapped_objective = lambda x: self._objective_wrapper(x, param_names, objective_function)
        
        # 记录优化开始时间
        start_time = time.time()
        
        # 根据方法选择不同的优化算法
        if method == 'grid_search':
            # 网格搜索
            return self._grid_search(param_names, bounds, wrapped_objective, max_iterations)
        elif method == 'differential_evolution':
            # 差分进化算法
            result = optimize.differential_evolution(
                wrapped_objective, 
                bounds, 
                maxiter=max_iterations,
                tol=tolerance,
                **kwargs
            )
        elif method == 'nelder_mead':
            # Nelder-Mead单纯形法
            initial_guess = [(b[0] + b[1]) / 2 for b in bounds]  # 使用边界的中点作为初始猜测
            result = optimize.minimize(
                wrapped_objective, 
                initial_guess, 
                method='Nelder-Mead',
                options={'maxiter': max_iterations, 'xatol': tolerance, 'fatol': tolerance},
                **kwargs
            )
        elif method == 'powell':
            # Powell方向集法
            initial_guess = [(b[0] + b[1]) / 2 for b in bounds]
            result = optimize.minimize(
                wrapped_objective, 
                initial_guess, 
                method='Powell',
                options={'maxiter': max_iterations, 'xtol': tolerance, 'ftol': tolerance},
                **kwargs
            )
        elif method == 'bfgs':
            # BFGS拟牛顿法
            initial_guess = [(b[0] + b[1]) / 2 for b in bounds]
            result = optimize.minimize(
                wrapped_objective, 
                initial_guess, 
                method='BFGS',
                options={'maxiter': max_iterations, 'gtol': tolerance},
                **kwargs
            )
        else:
            self.logger.error(f"不支持的优化方法: {method}")
            return {'success': False, 'message': f'不支持的优化方法: {method}'}
            
        # 计算运行时间
        run_time = time.time() - start_time
        
        # 构建结果字典
        best_params = {name: value for name, value in zip(param_names, result.x)}
        
        # 日志输出最佳结果
        self.logger.info(f"优化完成，方法: {method}")
        self.logger.info(f"最佳参数: {best_params}")
        self.logger.info(f"目标函数值: {result.fun}")
        self.logger.info(f"是否成功: {result.success}")
        self.logger.info(f"迭代次数: {result.nit if hasattr(result, 'nit') else result.nfev}")
        self.logger.info(f"运行时间: {run_time:.2f} 秒")
        
        # 返回优化结果
        return {
            'method': method,
            'best_parameters': best_params,
            'objective_value': float(result.fun),
            'success': bool(result.success),
            'iterations': int(result.nit if hasattr(result, 'nit') else result.nfev),
            'message': str(result.message) if hasattr(result, 'message') else '',
            'run_time': float(run_time),
            'history_size': len(self.optimization_history)
        }
    
    def _grid_search(self, param_names: List[str], bounds: List[Tuple[float, float]], 
                   objective_function: Callable, max_samples: int) -> Dict:
        """
        执行网格搜索优化
        
        Args:
            param_names: 参数名称列表
            bounds: 参数边界列表
            objective_function: 包装的目标函数
            max_samples: 最大样本数
            
        Returns:
            Dict: 优化结果
        """
        self.logger.info(f"开始网格搜索，最大样本数: {max_samples}")
        
        # 计算每个维度的采样点数
        n_params = len(param_names)
        
        # 确定每个维度上的采样点数
        # 使总点数接近但不超过max_samples
        samples_per_dim = int(np.floor(max_samples ** (1.0 / n_params)))
        
        # 至少每个维度采样2个点
        samples_per_dim = max(2, samples_per_dim)
        
        self.logger.info(f"每个维度的采样点数: {samples_per_dim}")
        
        # 为每个参数创建采样点
        grid_points = []
        for i, (lower, upper) in enumerate(bounds):
            # 检查参数是否有步长
            step = self.parameters[param_names[i]].get('step')
            
            if step is not None:
                # 使用指定步长在范围内生成点
                points = np.arange(lower, upper + step/2, step)
                # 如果点数过多，进行裁剪
                if len(points) > samples_per_dim:
                    indices = np.linspace(0, len(points) - 1, samples_per_dim, dtype=int)
                    points = points[indices]
            else:
                # 线性分布采样点
                points = np.linspace(lower, upper, samples_per_dim)
                
            grid_points.append(points)
            
        # 生成网格
        mesh = np.meshgrid(*grid_points)
        
        # 计算网格中的总点数
        total_points = np.prod([len(points) for points in grid_points])
        self.logger.info(f"网格搜索总点数: {total_points}")
        
        # 展平网格点
        params_list = []
        for i in range(total_points):
            idx = np.unravel_index(i, [len(points) for points in grid_points])
            point = [mesh[j][idx] for j in range(n_params)]
            params_list.append(point)
            
        # 评估所有点
        start_time = time.time()
        results = []
        
        for params in params_list:
            objective_value = objective_function(np.array(params))
            results.append(objective_value)
            
        # 找到最佳点
        best_idx = np.argmin(results)
        best_params = params_list[best_idx]
        best_value = results[best_idx]
        
        # 计算运行时间
        run_time = time.time() - start_time
        
        # 构建结果对象
        result = {
            'method': 'grid_search',
            'best_parameters': {name: value for name, value in zip(param_names, best_params)},
            'objective_value': float(best_value),
            'success': True,
            'iterations': total_points,
            'message': '网格搜索完成',
            'run_time': float(run_time),
            'history_size': len(self.optimization_history)
        }
        
        return result
    
    def suggest_next_experiments(self, n: int = 3, method: str = 'best_neighbors') -> List[Dict]:
        """
        根据当前优化结果，建议下一组实验参数
        
        Args:
            n: 建议的实验数量
            method: 建议方法 ('best_neighbors', 'random', 'exploration')
            
        Returns:
            List[Dict]: 建议的参数设置列表
        """
        if not self.optimization_history:
            self.logger.warning("没有优化历史，无法建议新实验")
            return []
            
        if self.best_result is None:
            self.logger.warning("没有找到最佳结果，无法建议新实验")
            return []
            
        suggestions = []
        
        if method == 'best_neighbors':
            # 基于最佳点的邻域探索
            best_params = {k: v for k, v in self.best_result.items() 
                          if k in self.parameters}
                          
            # 创建在最佳点附近的变化
            param_names = list(self.parameters.keys())
            
            for _ in range(n):
                # 为每个参数加入微小变化
                new_params = best_params.copy()
                
                # 随机选择一个参数进行较大变化
                param_to_change = np.random.choice(param_names)
                config = self.parameters[param_to_change]
                
                # 计算变化幅度（参数范围的10-30%）
                range_width = config['max'] - config['min']
                change_amount = range_width * np.random.uniform(0.1, 0.3)
                
                # 随机决定是增加还是减少
                if np.random.random() > 0.5:
                    new_value = best_params[param_to_change] + change_amount
                    # 确保在范围内
                    new_value = min(new_value, config['max'])
                else:
                    new_value = best_params[param_to_change] - change_amount
                    # 确保在范围内
                    new_value = max(new_value, config['min'])
                    
                new_params[param_to_change] = new_value
                
                # 为其他参数加入小变化
                for param in param_names:
                    if param != param_to_change:
                        config = self.parameters[param]
                        range_width = config['max'] - config['min']
                        
                        # 小变化（范围的1-5%）
                        change_amount = range_width * np.random.uniform(0.01, 0.05)
                        
                        # 随机决定是增加还是减少
                        if np.random.random() > 0.5:
                            new_value = best_params[param] + change_amount
                            # 确保在范围内
                            new_value = min(new_value, config['max'])
                        else:
                            new_value = best_params[param] - change_amount
                            # 确保在范围内
                            new_value = max(new_value, config['min'])
                            
                        new_params[param] = new_value
                
                suggestions.append(new_params)
                
        elif method == 'random':
            # 完全随机采样
            for _ in range(n):
                new_params = {}
                for name, config in self.parameters.items():
                    new_params[name] = np.random.uniform(config['min'], config['max'])
                suggestions.append(new_params)
                
        elif method == 'exploration':
            # 探索未访问的区域
            # 获取所有已评估的参数点
            evaluated_points = []
            for entry in self.optimization_history:
                point = [entry.get(name, 0) for name in self.parameters]
                evaluated_points.append(point)
                
            evaluated_points = np.array(evaluated_points)
            
            # 生成大量随机点
            num_candidates = min(1000, n * 50)
            candidates = []
            
            for _ in range(num_candidates):
                new_params = {}
                for name, config in self.parameters.items():
                    new_params[name] = np.random.uniform(config['min'], config['max'])
                candidates.append(new_params)
                
            # 计算每个候选点到已评估点的最小距离
            best_distances = []
            param_names = list(self.parameters.keys())
            
            for candidate in candidates:
                candidate_point = np.array([candidate[name] for name in param_names])
                
                # 计算与已评估点的距离
                distances = np.linalg.norm(evaluated_points - candidate_point, axis=1)
                min_distance = np.min(distances)
                best_distances.append((min_distance, candidate))
                
            # 选择距离最大的点
            best_distances.sort(reverse=True)
            suggestions = [candidate for _, candidate in best_distances[:n]]
            
        else:
            self.logger.error(f"不支持的建议方法: {method}")
            
        return suggestions
    
    def get_optimization_history_df(self) -> pd.DataFrame:
        """
        获取优化历史记录DataFrame
        
        Returns:
            pd.DataFrame: 优化历史记录
        """
        if not self.optimization_history:
            return pd.DataFrame()
            
        return pd.DataFrame(self.optimization_history)
        
    def save_optimization_history(self, file_path: str):
        """
        保存优化历史记录到文件
        
        Args:
            file_path: 输出文件路径
        """
        if not self.optimization_history:
            self.logger.warning("没有优化历史记录可保存")
            return
            
        try:
            df = self.get_optimization_history_df()
            
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == '.csv':
                df.to_csv(file_path, index=False)
            elif file_ext == '.json':
                df.to_json(file_path, orient='records', indent=2)
            elif file_ext == '.xlsx':
                df.to_excel(file_path, index=False)
            else:
                # 默认为CSV
                df.to_csv(file_path, index=False)
                
            self.logger.info(f"已保存优化历史记录到: {file_path}")
            
        except Exception as e:
            self.logger.error(f"保存优化历史记录时出错: {str(e)}")
            
    def load_optimization_history(self, file_path: str):
        """
        从文件加载优化历史记录
        
        Args:
            file_path: 输入文件路径
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            elif file_ext == '.xlsx':
                df = pd.read_excel(file_path)
            else:
                # 默认为CSV
                df = pd.read_csv(file_path)
                
            # 转换为字典列表
            self.optimization_history = df.to_dict('records')
            
            # 更新最佳结果
            if self.optimization_history:
                obj_values = [entry.get('objective_value', float('inf')) 
                             for entry in self.optimization_history]
                best_idx = np.argmin(obj_values)
                self.best_result = self.optimization_history[best_idx]
                
            self.logger.info(f"已加载优化历史记录，共 {len(self.optimization_history)} 条")
            
        except Exception as e:
            self.logger.error(f"加载优化历史记录时出错: {str(e)}")
            
    def plot_optimization_progress(self, output_file: str = None):
        """
        绘制优化进度曲线
        
        Args:
            output_file: 输出文件路径(可选)
        """
        if not self.optimization_history:
            self.logger.warning("没有优化历史记录可绘制")
            return
            
        try:
            import matplotlib.pyplot as plt
            
            # 获取优化历史
            df = self.get_optimization_history_df()
            
            if 'objective_value' not in df.columns:
                self.logger.warning("优化历史记录中没有目标函数值")
                return
                
            # 创建图表
            plt.figure(figsize=(12, 8))
            
            # 绘制目标函数值变化
            plt.subplot(2, 1, 1)
            plt.plot(df.index, df['objective_value'], 'b-', marker='o')
            plt.xlabel('迭代次数')
            plt.ylabel('目标函数值')
            plt.title('优化进度 - 目标函数值变化')
            plt.grid(True)
            
            # 计算移动平均
            window_size = min(10, len(df) // 2)
            if window_size > 1:
                moving_avg = df['objective_value'].rolling(window=window_size).mean()
                plt.plot(df.index, moving_avg, 'r-', linewidth=2, label=f'移动平均 (窗口={window_size})')
                plt.legend()
            
            # 绘制参数变化
            plt.subplot(2, 1, 2)
            
            param_names = [col for col in df.columns 
                         if col not in ['objective_value', 'timestamp', 'error']]
                         
            for param in param_names:
                plt.plot(df.index, df[param], marker='.', label=param)
                
            plt.xlabel('迭代次数')
            plt.ylabel('参数值')
            plt.title('优化进度 - 参数值变化')
            plt.legend()
            plt.grid(True)
            
            plt.tight_layout()
            
            # 保存或显示图表
            if output_file:
                plt.savefig(output_file, dpi=300)
                self.logger.info(f"已保存优化进度图表到: {output_file}")
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制优化进度时出错: {str(e)}")
            
    def plot_parameter_heatmap(self, param_x: str, param_y: str, output_file: str = None):
        """
        绘制两个参数的热力图
        
        Args:
            param_x: X轴参数名称
            param_y: Y轴参数名称
            output_file: 输出文件路径(可选)
        """
        if not self.optimization_history:
            self.logger.warning("没有优化历史记录可绘制")
            return
            
        if param_x not in self.parameters or param_y not in self.parameters:
            self.logger.warning(f"参数 {param_x} 或 {param_y} 不存在")
            return
            
        try:
            import matplotlib.pyplot as plt
            from matplotlib.colors import LogNorm
            from scipy.interpolate import griddata
            
            # 获取优化历史
            df = self.get_optimization_history_df()
            
            if 'objective_value' not in df.columns:
                self.logger.warning("优化历史记录中没有目标函数值")
                return
                
            # 提取需要的数据
            x = df[param_x].values
            y = df[param_y].values
            z = df['objective_value'].values
            
            # 创建网格
            xi = np.linspace(min(x), max(x), 100)
            yi = np.linspace(min(y), max(y), 100)
            X, Y = np.meshgrid(xi, yi)
            
            # 插值
            Z = griddata((x, y), z, (X, Y), method='cubic', fill_value=np.median(z))
            
            # 创建图表
            plt.figure(figsize=(10, 8))
            
            # 绘制热力图
            plt.pcolormesh(X, Y, Z, shading='auto', cmap='viridis')
            plt.colorbar(label='目标函数值')
            
            # 绘制采样点
            plt.scatter(x, y, c='red', s=20, marker='o', label='采样点')
            
            # 标记最佳点
            best_idx = np.argmin(z)
            plt.scatter(x[best_idx], y[best_idx], c='white', s=100, marker='*', label='最佳点')
            
            # 设置标题和标签
            plt.title(f'参数热力图: {param_x} vs {param_y}')
            plt.xlabel(f'{param_x} {self.parameters[param_x].get("units", "")}')
            plt.ylabel(f'{param_y} {self.parameters[param_y].get("units", "")}')
            plt.legend()
            
            # 保存或显示图表
            if output_file:
                plt.savefig(output_file, dpi=300)
                self.logger.info(f"已保存参数热力图到: {output_file}")
            else:
                plt.show()
                
        except Exception as e:
            self.logger.error(f"绘制参数热力图时出错: {str(e)}")
    
    def export_best_parameters(self, file_path: str):
        """
        导出最佳参数到文件
        
        Args:
            file_path: 输出文件路径
        """
        if self.best_result is None:
            self.logger.warning("没有最佳结果可导出")
            return
            
        try:
            # 提取参数
            best_params = {k: v for k, v in self.best_result.items() 
                          if k in self.parameters}
                         
            # 添加目标函数值
            best_params['objective_value'] = self.best_result.get('objective_value')
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.json':
                with open(file_path, 'w') as f:
                    json.dump(best_params, f, indent=2)
            elif file_ext == '.csv':
                pd.DataFrame([best_params]).to_csv(file_path, index=False)
            else:
                # 默认为文本格式
                with open(file_path, 'w') as f:
                    for key, value in best_params.items():
                        f.write(f"{key} = {value}\n")
                        
            self.logger.info(f"已导出最佳参数到: {file_path}")
            
        except Exception as e:
            self.logger.error(f"导出最佳参数时出错: {str(e)}")
    
    def create_parameter_scan_experiment(self, param_name: str, values: List[float], 
                                      base_params: Dict = None):
        """
        创建参数扫描实验
        
        Args:
            param_name: 要扫描的参数名称
            values: 参数值列表
            base_params: 基准参数字典(可选)
            
        Returns:
            List[Dict]: 实验参数列表
        """
        if param_name not in self.parameters:
            self.logger.warning(f"参数 {param_name} 不存在")
            return []
            
        # 使用基准参数或最佳参数(如果有)或参数中点值
        if base_params is None:
            if self.best_result is not None:
                base_params = {k: v for k, v in self.best_result.items() 
                              if k in self.parameters}
            else:
                base_params = {}
                for name, config in self.parameters.items():
                    base_params[name] = (config['min'] + config['max']) / 2
                    
        # 创建实验列表
        experiments = []
        
        for value in values:
            params = base_params.copy()
            params[param_name] = value
            experiments.append(params)
            
        self.logger.info(f"创建参数扫描实验，参数: {param_name}，值: {values}")
        return experiments 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器模块，用于生成迭代报告
"""

import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("auto_sim.report_generator")

class ReportGenerator:
    """报告生成器"""

    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.reports_dir = self.project_path / "Reports"
        os.makedirs(self.reports_dir, exist_ok=True)
        logger.info(f"报告生成器初始化，报告将保存在: {self.reports_dir}")

    def _get_timestamp(self):
        """获取当前时间戳字符串"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')

    def _format_param_value(self, value):
        """格式化参数值，对大数字使用科学计数法"""
        if isinstance(value, (int, float)) and abs(value) >= 1e6:
            return f"{value:.2e}"
        return str(value)

    def generate_iteration_report(
        self,
        iteration: int,
        params: dict,
        results: dict,
        optimized_params: dict = None,
        deepseek_thought: str = None
    ):
        """生成单次迭代的报告"""
        timestamp = self._get_timestamp()
        filename = self.reports_dir / f"report_iteration_{iteration}_{timestamp}.md"
        logger.info(f"生成第 {iteration} 次迭代报告: {filename}")

        content = []
        content.append(f"# 自动化仿真迭代报告 - 第 {iteration} 轮")
        content.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("--- ")

        content.append("## 本轮输入参数")
        for key, value in params.items():
            content.append(f"- **{key}:** {self._format_param_value(value)}")
        content.append("")

        content.append("## 本轮仿真结果")
        if results.get("error"):
            content.append(f"**错误:** {results['error']}")
        else:
            for key, value in results.items():
                 content.append(f"- **{key}:** {self._format_param_value(value)}")
        content.append("")

        # 新增 DeepSeek 思考过程部分
        if deepseek_thought:
            content.append("## DeepSeek 思考过程")
            content.append("```markdown")
            content.append(deepseek_thought)
            content.append("```")
            content.append("")
        else:
            content.append("## DeepSeek 思考过程")
            content.append("未提供 DeepSeek 思考过程信息。")
            content.append("")

        if optimized_params:
            content.append("## DeepSeek 优化建议 (用于下一轮)")
            content.append("```json")
            content.append(json.dumps(optimized_params, indent=4))
            content.append("```")
        else:
             content.append("## DeepSeek 优化建议")
             content.append("未获取到有效的优化建议 (可能因错误终止或达到目标)。")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            logger.info(f"迭代报告已保存: {filename}")
        except Exception as e:
            logger.error(f"保存迭代报告失败: {e}")

    def generate_summary_report(self, all_results: list):
        """生成最终的总结报告"""
        timestamp = self._get_timestamp()
        filename = self.reports_dir / f"report_summary_{timestamp}.md"
        logger.info(f"生成最终总结报告: {filename}")

        content = []
        content.append("# 自动化仿真优化总结报告")
        content.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"**总迭代次数:** {len(all_results)}")
        content.append("---")

        if not all_results:
            content.append("没有有效的仿真结果可供总结。")
        else:
            content.append("## 各轮最佳结果回顾")
            content.append("")
            for i, entry in enumerate(all_results):
                iteration = entry.get('iteration', i + 1)
                params = entry.get('params', {})
                results = entry.get('results', {})
                node_id = entry.get('node_id', 'N/A')
                tool_label = entry.get('parsed_tool_label', 'unknown')
                
                content.append(f"### 第 {iteration} 轮 (节点 {node_id}, 工具 {tool_label})")
                content.append("**参数:**")
                param_str = ", ".join([f"{k}={self._format_param_value(v)}" for k, v in params.items()])
                content.append(f"> {param_str}")
                content.append("**结果:**")
                result_str = ", ".join([f"{k}={self._format_param_value(v)}" for k, v in results.items()])
                content.append(f"> {result_str}")
                content.append("")
            
            content.append("---")
            content.append("## 最终最佳结果")
            best_entry = all_results[-1] # 假设列表是按顺序存储的，最后一个是最终的
            best_params = best_entry.get('params', {})
            best_results = best_entry.get('results', {})
            content.append("**参数:**")
            best_param_str = "\n".join([f"- **{k}:** {self._format_param_value(v)}" for k, v in best_params.items()])
            content.append(best_param_str)
            content.append("")
            content.append("**结果:**")
            bv = best_results.get('breakdown_voltage', 'N/A')
            vth = best_results.get('threshold_voltage', 'N/A')
            content.append(f"- **Breakdown Voltage (BV):** {self._format_param_value(bv)}")
            content.append(f"- **Threshold Voltage (Vth):** {self._format_param_value(vth)}")
            other_results_str = "\n".join([f"- **{k}:** {self._format_param_value(v)}" for k, v in best_results.items() if k not in ['breakdown_voltage', 'threshold_voltage', 'parsed_node_id', 'parsed_tool_label']])
            if other_results_str:
                content.append(other_results_str)

            # 新增：附加最后三次迭代报告内容
            content.append("\n---")
            content.append("## 最近三次迭代详情")
            
            num_results = len(all_results)
            start_index = max(0, num_results - 3)
            
            if num_results == 0:
                content.append("无迭代记录可供附加。")
            else:
                for i in range(start_index, num_results):
                    entry = all_results[i]
                    iteration_num = entry.get('iteration', i + 1)
                    # 尝试找到对应的迭代报告文件
                    # 注意：这里假设迭代报告文件名包含迭代次数，但时间戳未知，需要查找匹配的文件
                    # 可能需要更鲁棒的文件查找逻辑，例如存储每次迭代报告的文件名
                    # 暂时使用 glob 查找，可能会匹配到多个文件，取最新的一个
                    report_pattern = f"report_iteration_{iteration_num}_*.md"
                    iteration_reports = sorted(self.reports_dir.glob(report_pattern), key=os.path.getmtime, reverse=True)
                    
                    if iteration_reports:
                        latest_report_path = iteration_reports[0]
                        content.append(f"\n### 第 {iteration_num} 轮报告 ({latest_report_path.name})")
                        content.append("```markdown")
                        try:
                            with open(latest_report_path, 'r', encoding='utf-8') as iter_f:
                                content.append(iter_f.read())
                        except Exception as read_e:
                            content.append(f"读取报告文件失败: {read_e}")
                        content.append("```")
                    else:
                        content.append(f"\n### 第 {iteration_num} 轮报告")
                        content.append("未找到对应的迭代报告文件。")
                    content.append("")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            logger.info(f"总结报告已保存: {filename}")
        except Exception as e:
            logger.error(f"保存总结报告失败: {e}")

    def save_intermediate_summary(self, markdown_content: str, start_iter: int, end_iter: int):
        """将 DeepSeek 生成的中间总结 Markdown 内容保存到文件。"""
        if not markdown_content:
            logger.error("没有提供 Markdown 内容，无法保存中间总结报告。")
            return

        timestamp = self._get_timestamp()
        filename = self.reports_dir / f"report_summary_iter_{start_iter}-{end_iter}_{timestamp}.md"
        logger.info(f"保存 DeepSeek 生成的中间总结报告: {filename}")

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info(f"中间总结报告已保存: {filename}")
        except Exception as e:
            logger.error(f"保存中间总结报告失败: {e}")

    def generate_final_report(self, iterations, best_result):
        """
        生成最终报告
        
        Args:
            iterations: 迭代次数或迭代次数列表
            best_result: 最佳结果
            
        Returns:
            str: 报告文件路径
        """
        logger.info("生成最终报告")
        
        # 创建报告文件名
        report_file = self.reports_dir / "final_report.md"
        
        # 生成报告内容
        content = []
        content.append("# 仿真最终报告")
        content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 添加迭代摘要
        content.append("## 仿真迭代摘要")
        # 检查iterations是否为整数
        if isinstance(iterations, int):
            content.append(f"- 总迭代次数: {iterations}")
            content.append(f"- 首次迭代: 1")
            content.append(f"- 末次迭代: {iterations}")
        else:
            # 原有的列表处理逻辑
            content.append(f"- 总迭代次数: {len(iterations)}")
            content.append(f"- 首次迭代: {min(iterations) if iterations else 'N/A'}")
            content.append(f"- 末次迭代: {max(iterations) if iterations else 'N/A'}")
        content.append("")
        
        # 添加最佳结果
        content.append("## 最佳仿真结果")
        if best_result:
            content.append(f"- 迭代号: {best_result.get('iteration', 'N/A')}")
            params = best_result.get('params', {})
            if params:
                content.append("### 参数")
                for key, value in sorted(params.items()):
                    content.append(f"- **{key}**: {value}")
                content.append("")
                
            results = best_result.get('results', {})
            if results:
                content.append("### 结果")
                for key, value in sorted(results.items()):
                    if isinstance(value, dict):
                        content.append(f"#### {key}")
                        for k, v in sorted(value.items()):
                            content.append(f"- **{k}**: {v}")
                    else:
                        content.append(f"- **{key}**: {value}")
                content.append("")
        else:
            content.append("*无最佳结果数据*")
            
        # 写入文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
            
        logger.info(f"已生成最终报告文件: {report_file}")
        
        return str(report_file)
    
    def generate_error_report(self, iteration, params, error_message):
        """
        生成错误报告
        
        Args:
            iteration: 迭代次数
            params: 参数字典
            error_message: 错误信息
            
        Returns:
            str: 报告文件路径
        """
        logger.info(f"生成第 {iteration} 次迭代错误报告")
        
        # 创建报告文件名
        report_file = self.reports_dir / "error_report.md"
        
        # 生成报告内容
        content = []
        content.append("# 仿真错误报告")
        content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        content.append(f"## 错误发生于迭代 {iteration}")
        content.append("")
        
        # 添加参数部分（处理params可能是字符串或字典的情况）
        content.append("## 仿真参数")
        
        if isinstance(params, dict):
            # 如果params是字典，正常处理
            for key, value in sorted(params.items()):
                content.append(f"- **{key}**: {value}")
        elif isinstance(params, str):
            # 如果params是字符串，直接添加
            content.append(f"- {params}")
        else:
            # 其他类型，尝试转换为字符串
            content.append(f"- {str(params)}")
            
        content.append("")
        
        # 添加错误信息（处理error_message可能是字符串或其他类型的情况）
        content.append("## 错误信息")
        content.append("```")
        if isinstance(error_message, str):
            content.append(error_message)
        else:
            # 当参数顺序被错误调换时，error_message可能是其他类型
            content.append(str(error_message))
        content.append("```")
        content.append("")
        
        # 写入文件
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
            
        logger.info(f"已生成错误报告文件: {report_file}")
        
        return str(report_file) 
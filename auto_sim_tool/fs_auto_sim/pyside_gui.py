#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import threading
import time
import traceback
import json
import glob
import subprocess
import signal

# 添加项目根目录和 auto_sim_tool 目录到模块搜索路径
tool_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /home/.../FS_IGBT/auto_sim_tool
project_root = os.path.dirname(tool_dir)  # /home/.../FS_IGBT
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if tool_dir not in sys.path:
    sys.path.insert(0, tool_dir)

# 检测Sentaurus安装环境脚本（使用STROOT和STRELEASE环境变量）
system_env_script = None
stroot = os.environ.get("STROOT")
strelease = os.environ.get("STRELEASE")
if stroot and strelease:
    candidate = os.path.join(stroot, 'tcad', strelease, 'bin', 'sentaurus_env.sh')
    if os.path.exists(candidate):
        system_env_script = candidate

# 检测项目根目录的sentaurus_env.sh脚本
project_env_script = None
project_root = project_root if 'project_root' in locals() else os.path.dirname(os.path.dirname(os.path.dirname(tool_dir)))
candidate_proj = os.path.join(project_root, 'sentaurus_env.sh')
if os.path.exists(candidate_proj):
    project_env_script = candidate_proj

# 如果项目根目录存在 sentaurus_env.sh，则在后续命令中 source 它
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sentaurus_env = os.path.join(project_root, 'sentaurus_env.sh')
if os.path.exists(sentaurus_env):
    self_env_script = sentaurus_env
else:
    self_env_script = None

# 禁用 GTK3 平台主题插件，强制使用 xcb 平台插件，避免 libqgtk3.so 加载失败
os.environ.setdefault("QT_QPA_PLATFORMTHEME", "")
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTextEdit, QProgressBar, QFileDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox,
                             QDialog, QCheckBox)
from PySide2.QtCore import Qt, Signal, Slot, QTimer, QProcess, QProcessEnvironment
from PySide2.QtGui import QFont, QTextCursor

# 全局变量追踪导入状态和错误
IMPORT_ERRORS = []

# 导入实际功能模块 (来自 project_root/auto_sim)
try:
    from auto_sim.parameter_manager import ParameterManager
    from auto_sim.swb_interaction import SWBInteraction
    from auto_sim.result_analyzer import ResultAnalyzer
    HAS_SWB_MODULES = True
    print("成功导入 auto_sim 模块")
except ImportError as e:
    HAS_SWB_MODULES = False
    error_msg = f"无法导入 auto_sim 模块: {str(e)}"
    IMPORT_ERRORS.append(error_msg)
    print(error_msg)

# 尝试从项目目录导入
def import_project_modules(project_path=None):
    """尝试从项目路径导入模块"""
    global HAS_SWB_MODULES, IMPORT_ERRORS
    import_errors = []
    
    # 常规导入尝试
    try:
        # 先尝试从已安装包导入
        from auto_sim.parameter_manager import ParameterManager
        from auto_sim.swb_interaction import SWBInteraction
        from auto_sim.result_analyzer import ResultAnalyzer
        print("成功从auto_sim导入模块")
        return (ParameterManager, SWBInteraction, ResultAnalyzer, True)
    except ImportError as e:
        error_msg = f"从auto_sim导入失败: {str(e)}"
        import_errors.append(error_msg)
        IMPORT_ERRORS.append(error_msg)
        print(error_msg)
    
    # 尝试从FS_IGBT项目导入
    if project_path and os.path.exists(project_path):
        try:
            # 将项目路径添加到系统路径
            if project_path not in sys.path:
                sys.path.insert(0, project_path)
            
            # 检查auto_sim目录是否存在
            auto_sim_dir = os.path.join(project_path, "auto_sim")
            if os.path.exists(auto_sim_dir) and auto_sim_dir not in sys.path:
                sys.path.insert(0, auto_sim_dir)
                print(f"已添加目录到sys.path: {auto_sim_dir}")
            
            # 直接导入模块
            from auto_sim.parameter_manager import ParameterManager
            from auto_sim.swb_interaction import SWBInteraction
            from auto_sim.result_analyzer import ResultAnalyzer
            print(f"成功从路径导入模块: {project_path}")
            return (ParameterManager, SWBInteraction, ResultAnalyzer, True)
        except ImportError as e:
            error_msg = f"从项目路径导入失败: {str(e)}"
            import_errors.append(error_msg)
            IMPORT_ERRORS.append(error_msg)
            print(error_msg)
            
            # 尝试直接从目录导入
            try:
                module_path = os.path.join(project_path, "auto_sim")
                sys.path.insert(0, module_path)
                print(f"尝试从直接路径导入: {module_path}")
                
                import parameter_manager
                import swb_interaction
                import result_analyzer
                
                print(f"成功从直接路径导入模块: {module_path}")
                return (parameter_manager.ParameterManager, 
                        swb_interaction.SWBInteraction, 
                        result_analyzer.ResultAnalyzer, True)
            except ImportError as e:
                error_msg = f"从直接路径导入失败: {str(e)}"
                import_errors.append(error_msg)
                IMPORT_ERRORS.append(error_msg)
                print(error_msg)
    
    # 如果尝试都失败了，返回None和错误信息
    print(f"所有导入尝试都失败: {import_errors}")
    return (None, None, None, False)

# 初始导入尝试
ParameterManager, SWBInteraction, ResultAnalyzer, HAS_SWB_MODULES = import_project_modules()

class ConsoleOutput(QTextEdit):
    """日志输出区域，类似于命令行输出"""
    # 定义跨线程文本信号
    text_signal = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("background-color: black; color: white;")
        font = QFont("Courier New", 10)
        self.setFont(font)
        # 连接信号到槽函数，保证线程安全
        self.text_signal.connect(self._append_text)
        
    def print(self, text, end='\n'):
        """添加文本到日志区域，线程安全版本"""
        # 发射信号在主线程更新UI
        self.text_signal.emit(str(text))
    
    @Slot(str)
    def _append_text(self, text):
        """实际执行添加文本的槽函数"""
        self.append(text)
        self.moveCursor(QTextCursor.End)

class AutoSimGUI(QMainWindow):
    """基于PySide2的自动仿真工具GUI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Auto-TCAD 全自动仿真工具 (PySide2版)")
        self.setMinimumSize(800, 600)
        self.swb_interaction = None
        self.parameter_manager = None
        self.result_analyzer = None
        self.is_simulation_running = False
        self.setup_ui()
        # 初始化模拟步数计数器
        self.fake_step = 0
        # 初始化外部进程，用于真实全自动仿真
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self._read_process_output)
        # 记录进程状态和输出
        self.process.stateChanged.connect(self._process_state_changed)
        self.process.finished.connect(self._process_finished)
        self.process.errorOccurred.connect(self._process_error)
        
    def setup_ui(self):
        """设置界面布局"""
        # 中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 项目目录
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Sentaurus 工程目录:"))
        self.project_path = QLineEdit()
        self.project_path.setText("/home/tcad/STDB/MyProjects/AI_Lab/FS_IGBT")
        project_layout.addWidget(self.project_path)
        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_folder)
        project_layout.addWidget(self.browse_button)
        main_layout.addLayout(project_layout)
        
        # 强制真实模式选项
        force_real_layout = QHBoxLayout()
        force_real_layout.addWidget(QLabel("强制使用真实模式(不管是否导入成功):"))
        self.force_real_mode = QCheckBox()
        self.force_real_mode.setChecked(True)  # 默认选中
        force_real_layout.addWidget(self.force_real_mode)
        force_real_layout.addStretch()
        main_layout.addLayout(force_real_layout)
        
        # API Key
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("DeepSeek API Key (可选):"))
        self.api_key = QLineEdit()
        self.api_key.setText("sk-buspthftjrkhcudljfardlbubjlmpfoxehgstdipajrxpccc")  # 设置默认API key
        api_layout.addWidget(self.api_key)
        main_layout.addLayout(api_layout)
        
        # 性能目标
        target_layout = QVBoxLayout()
        target_layout.addWidget(QLabel("性能目标描述:"))
        self.target_text = QTextEdit()
        self.target_text.setPlainText("提升耐压至1450V，但是保持阈值电压在10V以内")
        self.target_text.setMaximumHeight(80)
        target_layout.addWidget(self.target_text)
        main_layout.addLayout(target_layout)
        
        # 迭代次数
        iter_layout = QHBoxLayout()
        iter_layout.addWidget(QLabel("最大迭代次数:"))
        self.max_iter = QSpinBox()
        self.max_iter.setRange(1, 50)
        self.max_iter.setValue(10)
        iter_layout.addWidget(self.max_iter)
        iter_layout.addStretch()
        main_layout.addLayout(iter_layout)
        
        # 加载参数按钮
        load_button = QPushButton("加载初始参数")
        load_button.clicked.connect(self.load_parameters)
        main_layout.addWidget(load_button)
        
        # 参数表格
        self.param_table = QTableWidget(0, 2)
        self.param_table.setHorizontalHeaderLabels(["参数", "值"])
        self.param_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.param_table.setMinimumHeight(200)
        main_layout.addWidget(self.param_table)
        
        # 进度条
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("进度:"))
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        progress_layout.addWidget(self.progress)
        main_layout.addLayout(progress_layout)
        
        # 日志区域
        self.log_output = ConsoleOutput()
        main_layout.addWidget(self.log_output)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.check_button = QPushButton("初始化SWB项目")
        self.check_button.clicked.connect(self.init_swb_project)
        button_layout.addWidget(self.check_button)
        
        self.run_button = QPushButton("开始全自动仿真")
        self.run_button.clicked.connect(self.start_simulation)
        button_layout.addWidget(self.run_button)
        
        self.stop_button = QPushButton("停止仿真")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # 报告按钮
        report_layout = QHBoxLayout()
        interim_report_button = QPushButton("查看最新的中间总结报告")
        interim_report_button.clicked.connect(self.view_interim_report)
        report_layout.addWidget(interim_report_button)
        
        final_report_button = QPushButton("查看最终报告")
        final_report_button.clicked.connect(self.view_final_report)
        report_layout.addWidget(final_report_button)
        
        # 新增按钮：查看最新迭代报告
        latest_iter_report_button = QPushButton("查看最新迭代报告")
        latest_iter_report_button.clicked.connect(self.view_latest_iteration_report)
        report_layout.addWidget(latest_iter_report_button)

        main_layout.addLayout(report_layout)
        
        # 打印导入信息和错误
        if HAS_SWB_MODULES:
            self.log_output.print("✅ SWB模块导入成功")
        else:
            self.log_output.print("⚠️ SWB模块导入失败，将使用模拟模式或命令行模式")
            for error in IMPORT_ERRORS:
                self.log_output.print(f"  - {error}")
            self.log_output.print("如果需要真实模式，请检查模块安装或选中'强制真实模式'")
        
    def browse_folder(self):
        """浏览并选择文件夹，使用对话框模式避免崩溃"""
        try:
            dialog = QFileDialog(self)
            dialog.setWindowTitle("选择Sentaurus工程目录")
            dialog.setFileMode(QFileDialog.Directory)
            dialog.setOption(QFileDialog.ShowDirsOnly, True)
            if dialog.exec_() == QDialog.Accepted:
                paths = dialog.selectedFiles()
                if paths:
                    self.project_path.setText(paths[0])
        except Exception as e:
            self.log_output.print(f"浏览目录出错: {e}")
    
    def load_parameters(self):
        """加载参数数据"""
        try:
            # 实际加载初始参数
            if not HAS_SWB_MODULES:
                self._load_sample_params()
                return
                
            project_path = self.project_path.text()
            if not os.path.exists(project_path):
                QMessageBox.warning(self, "错误", f"项目路径不存在: {project_path}")
                return
                
            # 初始化参数管理器
            self.log_output.print(f"正在加载项目参数: {project_path}")
            self.parameter_manager = ParameterManager(project_path)
            
            # 检查初始参数文件
            if not self.parameter_manager.initial_params_exist():
                if QMessageBox.question(self, "参数文件缺失", 
                                     "未找到初始参数文件，是否创建示例参数?",
                                     QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    self.parameter_manager.create_example_params()
                    self.log_output.print("已创建示例参数文件")
                else:
                    return
            
            # 获取初始参数
            initial_params = self.parameter_manager.get_initial_params()
            if not initial_params:
                QMessageBox.warning(self, "错误", "无法加载初始参数")
                return
                
            # 更新表格
            self.update_param_table(initial_params)
            self.log_output.print("初始参数加载完成")
            
        except Exception as e:
            self.log_output.print(f"加载参数出错: {str(e)}")
            traceback.print_exc()
            self._load_sample_params()  # 降级到示例参数
    
    def _load_sample_params(self):
        """加载示例参数（当实际加载失败时使用）"""
        # 模拟初始参数数据
        sample_params = {
            'Xmax': '6',
            'Wgate': '1.8',
            'Wnplus': '2',
            'Wpplus': '5.5',
            'Wemitter': '4.5',
            'Ymax': '80',
            'Ndrift': '1e14',
            'Pbase': '5e16',
            'Pplus': '5e19',
            'Nplus': '5e19'
        }
        self.update_param_table(sample_params)
        self.log_output.print("已加载示例参数（模拟模式）")
        
    def update_param_table(self, params):
        """更新参数表格"""
        self.param_table.setRowCount(len(params))
        for i, (param, value) in enumerate(params.items()):
            self.param_table.setItem(i, 0, QTableWidgetItem(param))
            self.param_table.setItem(i, 1, QTableWidgetItem(str(value)))
    
    def init_swb_project(self):
        """初始化SWB项目"""
        global ParameterManager, SWBInteraction, ResultAnalyzer, HAS_SWB_MODULES
        try:
            # 检查是否强制真实模式
            use_real_mode = HAS_SWB_MODULES or self.force_real_mode.isChecked()
            
            # 首先尝试确保项目路径存在
            project_path = self.project_path.text()
            if not os.path.exists(project_path):
                QMessageBox.warning(self, "错误", f"项目路径不存在: {project_path}")
                return
                
            # 即使是模拟模式，也加载初始参数
            self.log_output.print(f"正在加载项目参数: {project_path}")
            
            # 优先使用模拟模式
            if not use_real_mode:
                self.log_output.print("使用模拟模式: SWB项目初始化成功")
                self._load_sample_params()  # 加载示例参数
                QMessageBox.information(self, "初始化成功", "SWB项目初始化完成（模拟模式）")
                return
            
            # 如果HAS_SWB_MODULES为False，但强制使用真实模式，尝试动态导入
            if not HAS_SWB_MODULES and self.force_real_mode.isChecked():
                self.log_output.print("强制真实模式：尝试再次动态导入SWB模块...")
                # 确保swbpy2等Sentaurus特有模块不会阻止程序运行
                try:
                    params_cls, swb_cls, result_cls, import_success = import_project_modules(project_path)
                    if import_success:
                        self.log_output.print("✅ 动态导入成功")
                        ParameterManager, SWBInteraction, ResultAnalyzer = params_cls, swb_cls, result_cls
                        HAS_SWB_MODULES = True
                    else:
                        self.log_output.print("❌ 动态导入失败，但仍将尝试使用命令行模式")
                        # 加载示例参数
                        self._load_sample_params()
                        QMessageBox.information(self, "初始化成功", "SWB模块导入失败，但已初始化完成（命令行模式）")
                        return
                except Exception as e:
                    self.log_output.print(f"动态导入出错: {str(e)}")
                    self.log_output.print("将使用命令行模式继续")
                    # 加载示例参数
                    self._load_sample_params()
                    QMessageBox.information(self, "初始化成功", "SWB项目初始化完成（命令行模式）")
                    return
            
            # 如果成功导入了模块，尝试真实初始化
            try:
                if HAS_SWB_MODULES:
                    if not self.parameter_manager:
                        self.parameter_manager = ParameterManager(project_path)
                    
                    self.swb_interaction = SWBInteraction(
                        project_path=project_path
                    )
                    
                    # 初始化结果分析器
                    self.result_analyzer = ResultAnalyzer(project_path)
                    
                    self.log_output.print("SWB项目初始化成功（真实模式）")
                    QMessageBox.information(self, "初始化成功", "SWB项目初始化完成（真实模式）")
                else:
                    self.log_output.print("由于模块导入失败，将使用命令行方式启动全自动仿真")
                    self.log_output.print("SWB项目初始化成功（命令行真实模式）")
                    QMessageBox.information(self, "初始化成功", "SWB项目初始化完成（命令行真实模式）")
            except Exception as e:
                self.log_output.print(f"初始化SWB组件失败: {str(e)}")
                self.log_output.print(traceback.format_exc())
                # 加载示例参数作为回退方案
                self._load_sample_params()
                QMessageBox.warning(self, "初始化部分失败", f"SWB组件初始化失败: {str(e)}\n将尝试通过命令行方式启动")
            
        except Exception as e:
            self.log_output.print(f"初始化SWB项目出错: {str(e)}")
            self.log_output.print(traceback.format_exc())
            QMessageBox.warning(self, "初始化失败", f"SWB项目初始化失败: {str(e)}")
        
    def start_simulation(self):
        """开始自动模拟"""
        global ParameterManager, SWBInteraction, ResultAnalyzer, HAS_SWB_MODULES
        
        if not self.check_project_initialized():
            return
            
        try:
            # 检查是否强制真实模式
            use_real_mode = HAS_SWB_MODULES or self.force_real_mode.isChecked()
            
            # 1. 创建项目结构
            project_path = self.project_path.text()
            api_key = self.api_key.text()
            max_iterations = self.max_iter.value()
            
            # 从target_text中提取性能目标
            performance_target_text = self.target_text.toPlainText().strip()
            performance_target = {"description": performance_target_text}
            
            # 2. 读取参数
            param_data = self.get_param_data_from_table()
            
            # 默认优先执行真实全自动流程
            self.log_output.print("启动实际全自动仿真流程...")
            self.log_output.print(f"项目路径: {project_path}")
            self.log_output.print(f"性能目标: {performance_target}")
            self.log_output.print(f"最大迭代次数: {max_iterations}")

            # 更新界面状态
            self.is_simulation_running = True
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
            # 启动实际自动化脚本
            success = self._start_auto_sim_script(project_path, performance_target, max_iterations)
            
            if not success:
                self.log_output.print("启动全自动仿真失败，将回退至模拟模式")
                # 重置模拟进度并启动单步调度
                self.fake_step = 0
                self.progress.setValue(0)
                QTimer.singleShot(100, self._fake_loop)
        
        except Exception as e:
            self.log_output.print(f"启动全自动仿真失败: {str(e)}")
            self.log_output.print(traceback.format_exc())
    
    def _fake_loop(self):
        """QTimer.singleShot 驱动的单步模拟仿真"""
        # 如果已停止，则直接退出
        if not self.is_simulation_running:
            return
        # 更新进度
        self.fake_step += 1
        percent = min(self.fake_step, 100)
        self.progress.setValue(percent)
        if percent % 10 == 0:
            self.log_output.print(f"模拟进度: {percent}%")
        # 判断是否继续调度
        if percent < 100:
            QTimer.singleShot(100, self._fake_loop)
        else:
            self.log_output.print("模拟仿真完成")
            self.is_simulation_running = False
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def _start_auto_sim_script(self, project_path, performance_target, max_iterations):
        """使用 bash 登录 shell 启动 auto_sim_main.py，自动 source sentaurus_env.sh 和 venv"""
        try:
            # 验证项目路径
            if not os.path.exists(project_path):
                self.log_output.print(f"错误: 项目路径不存在: {project_path}")
                return False
                
            # 设置 API key 到环境变量
            api_key = self.api_key.text().strip()
            api_env = ""
            if api_key:
                # 防止API key显示在界面日志中
                masked_key = f"{api_key[:5]}...{api_key[-5:]}"
                self.log_output.print(f"正在使用API Key: {masked_key}")
                api_env = f"export DEEPSEEK_API_KEY=\"{api_key}\" && "
                
            # 更新auto_sim_config.json中的max_iterations
            try:
                config_file = os.path.join(project_path, "auto_sim_config.json")
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    # 更新配置
                    config['max_iterations'] = max_iterations
                    
                    # 更新API KEY
                    if api_key and 'api_key' in config:
                        config['api_key'] = api_key
                    
                    # 设置为非模拟模式
                    if 'use_fake_results' in config:
                        config['use_fake_results'] = False
                    
                    # 更新性能目标
                    if performance_target and 'performance_target' in config:
                        target_parts = performance_target["description"].lower().split()
                        if "voltage" in performance_target["description"] and "current" in performance_target["description"]:
                            # 尝试提取数值
                            for i, word in enumerate(target_parts):
                                if word in ["voltage", "电压"]:
                                    try:
                                        config['performance_target']['voltage'] = float(target_parts[i-1])
                                    except:
                                        pass
                                if word in ["current", "电流"]:
                                    try:
                                        config['performance_target']['current'] = float(target_parts[i-1])
                                    except:
                                        pass
                    
                    # 写回更新后的配置
                    with open(config_file, 'w') as f:
                        json.dump(config, f, indent=2)
                    self.log_output.print(f"已更新配置文件: {config_file}")
            except Exception as e:
                self.log_output.print(f"无法更新配置文件: {e}")
                self.log_output.print(traceback.format_exc())

            # 构建启动命令
            self.log_output.print(f"工作目录: {project_path}")
            self.process.setWorkingDirectory(project_path)

            # 直接使用 run_auto_sim.sh 脚本（保证使用相同环境和命令）
            run_script = os.path.join(project_path, "run_auto_sim.sh")
            if os.path.exists(run_script):
                self.log_output.print(f"使用自动仿真脚本: {run_script}")
                # 确保脚本有执行权限
                os.chmod(run_script, 0o755)
                self.process.start('/bin/bash', ['-c', f'cd "{project_path}" && {run_script}'])
                return True
            
            # 备用方法：如果找不到 run_auto_sim.sh，则手动构造类似命令
            self.log_output.print("未找到run_auto_sim.sh，使用备用启动方法...")
            
            # 设置虚拟环境激活脚本路径（注意：使用swb_env而不是.fs_auto_sim_env）
            venv_dir = os.path.join(project_path, "swb_env")
            venv_activate = os.path.join(venv_dir, "bin", "activate")
            
            if not os.path.exists(venv_activate):
                # 如果swb_env不存在，尝试使用.fs_auto_sim_env
                venv_dir = os.path.join(project_path, ".fs_auto_sim_env")
                venv_activate = os.path.join(venv_dir, "bin", "activate")
                self.log_output.print(f"尝试备用虚拟环境: {venv_activate}")

            # 查找 auto_sim_main.py 脚本
            main_script = os.path.join(project_path, "auto_sim", "auto_sim_main.py")
            if not os.path.exists(main_script):
                alt_locations = [
                    os.path.join(project_path, "auto_sim_main.py"),
                    os.path.join(project_path, "auto_sim.py")
                ]
                for alt in alt_locations:
                    if os.path.exists(alt):
                        main_script = alt
                        break
                else:
                    self.log_output.print(f"错误: 找不到auto_sim_main.py脚本: {main_script}")
                    return False

            # 构建 shell 命令
            shell_cmd_parts = []
            # 0. source 系统级 Sentaurus 环境脚本
            if system_env_script:
                shell_cmd_parts.append(f'source "{system_env_script}"')
            # 1. source 项目级 sentaurus_env.sh
            project_env = os.path.join(project_path, "sentaurus_env.sh")
            if os.path.exists(project_env):
                shell_cmd_parts.append(f'source "{project_env}"')
            # 2. 激活虚拟环境
            if os.path.exists(venv_activate):
                shell_cmd_parts.append(f'source "{venv_activate}"')
            # 3. 设置PYTHONIOENCODING
            shell_cmd_parts.append('export PYTHONIOENCODING=UTF-8')
            # 4. 设置API key
            if api_key:
                shell_cmd_parts.append(f'export DEEPSEEK_API_KEY="{api_key}"')
            # 5. 执行 auto_sim_main.py（与run_auto_sim.sh中相同的参数）
            api_key_param = f'--api-key {api_key}' if api_key else ''
            shell_cmd_parts.append(f'cd "{project_path}" && python "{main_script}" {api_key_param}')
            full_cmd = ' && '.join(shell_cmd_parts)

            self.log_output.print(f"执行命令: {full_cmd}")
            self.process.start('/bin/bash', ['-c', full_cmd])
            
            return True
        except Exception as e:
            self.log_output.print(f"启动自动化脚本失败: {str(e)}")
            self.log_output.print(traceback.format_exc())
            return False
    
    def run_actual_simulation(self, project_path, performance_target, max_iterations):
        """实际运行仿真流程的线程函数"""
        try:
            # 重新初始化组件（以防尚未初始化）
            if not self.parameter_manager:
                self.parameter_manager = ParameterManager(project_path)
                
            if not self.swb_interaction:
                self.swb_interaction = SWBInteraction(
                    project_path=project_path,
                    parameter_manager=self.parameter_manager
                )
                
            if not self.result_analyzer:
                self.result_analyzer = ResultAnalyzer(project_path)
                
            # 获取初始参数
            current_params = self.parameter_manager.get_initial_params()
            self.log_output.print("已获取初始参数")
            
            # 仿真迭代循环
            for iteration in range(1, max_iterations + 1):
                if not self.is_simulation_running:
                    self.log_output.print("仿真被用户中止")
                    break
                    
                self.log_output.print(f"\n===== 开始第 {iteration} 次迭代 =====")
                
                # 更新进度条
                progress_value = int((iteration - 1) / max_iterations * 100)
                self.progress.setValue(progress_value)
                
                # 1. 创建新实验
                self.log_output.print("正在创建新实验...")
                try:
                    # 调用SWB交互创建新实验
                    new_node_ids = self.swb_interaction.create_new_experiment(current_params)
                    if not new_node_ids or not new_node_ids.get('leaf_nodes', []):
                        self.log_output.print("创建实验失败: 未返回有效节点ID")
                        break
                        
                    leaf_nodes = new_node_ids.get('leaf_nodes', [])
                    self.log_output.print(f"创建了 {len(leaf_nodes)} 个叶节点: {leaf_nodes}")
                    
                except Exception as e:
                    self.log_output.print(f"创建实验出错: {str(e)}")
                    traceback.print_exc()
                    break
                
                # 2. 运行实验
                self.log_output.print("正在运行实验...")
                try:
                    # 调用SWB交互运行节点
                    # 运行前调用预处理
                    self.swb_interaction.deck.preprocess()
                    time.sleep(2)  # 给预处理留点时间
                    
                    # 确保按正确顺序运行所有节点
                    all_nodes = new_node_ids.get('all_nodes', [])
                    self.log_output.print(f"准备运行节点: {all_nodes}")
                    
                    # 逐个运行节点
                    for node_id in sorted(all_nodes):
                        self.log_output.print(f"运行节点 {node_id}...")
                        self.swb_interaction.deck.run(nodes=[node_id])
                        time.sleep(1)  # 重要：每个节点之间的间隔
                        
                except Exception as e:
                    self.log_output.print(f"运行实验出错: {str(e)}")
                    traceback.print_exc()
                    break
                
                # 3. 等待实验完成
                self.log_output.print("等待实验完成...")
                try:
                    self.swb_interaction.wait_for_simulation_completion(leaf_nodes)
                except Exception as e:
                    self.log_output.print(f"等待实验完成出错: {str(e)}")
                    traceback.print_exc()
                    break
                
                # 4. 解析结果
                self.log_output.print("正在解析结果...")
                try:
                    # 调用结果分析器处理结果
                    results = self.result_analyzer.process_simulation_results(leaf_nodes)
                    if not results:
                        self.log_output.print("未能获取有效结果")
                        break
                        
                    # 展示关键结果
                    self.log_output.print("\n--- 仿真结果摘要 ---")
                    for key, value in results.items():
                        self.log_output.print(f"{key}: {value}")
                    
                except Exception as e:
                    self.log_output.print(f"解析结果出错: {str(e)}")
                    traceback.print_exc()
                    break
                
                # 5. 获取优化建议
                self.log_output.print("正在获取优化建议...")
                try:
                    # 调用DeepSeek获取优化建议
                    # 这里默认SWB交互对象有获取优化建议的方法
                    optimized_params = self.swb_interaction.get_optimization_suggestions(
                        current_params=current_params,
                        simulation_results=results,
                        performance_target=performance_target
                    )
                    
                    if not optimized_params:
                        self.log_output.print("未能获取有效优化建议")
                        break
                        
                    # 更新当前参数为优化后的参数
                    current_params = optimized_params
                    
                    # 显示优化建议
                    self.log_output.print("\n--- 优化建议 ---")
                    for param, value in optimized_params.items():
                        self.log_output.print(f"{param}: {value}")
                    
                    # 更新参数表格
                    self.update_param_table(optimized_params)
                    
                except Exception as e:
                    self.log_output.print(f"获取优化建议出错: {str(e)}")
                    traceback.print_exc()
                    break
                
                # 6. 生成迭代报告
                self.log_output.print("正在生成迭代报告...")
                try:
                    # 调用报告生成功能
                    report_path = self.swb_interaction.generate_iteration_report(
                        iteration=iteration,
                        params=current_params,
                        results=results
                    )
                    
                    if report_path:
                        self.log_output.print(f"迭代报告已保存: {report_path}")
                    
                except Exception as e:
                    self.log_output.print(f"生成报告出错: {str(e)}")
                    # 报告生成失败不应中断流程
                
                # 迭代完成
                self.log_output.print(f"===== 第 {iteration} 次迭代完成 =====\n")
            
            # 全部迭代完成
            self.log_output.print("\n===== 全部仿真迭代完成 =====")
            
            # 生成最终报告
            try:
                final_report_path = self.swb_interaction.generate_final_report()
                if final_report_path:
                    self.log_output.print(f"最终报告已保存: {final_report_path}")
            except Exception as e:
                self.log_output.print(f"生成最终报告出错: {str(e)}")
            
            # 设置进度条为100%
            self.progress.setValue(100)
            
        except Exception as e:
            self.log_output.print(f"仿真过程中发生错误: {str(e)}")
            traceback.print_exc()
        
        finally:
            # 恢复界面状态
            self.is_simulation_running = False
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def stop_simulation(self):
        """立即停止模拟仿真 (发送 SIGINT 到进程组)"""
        if not self.is_simulation_running:
            return
        self.log_output.print("用户请求停止仿真，正在发送中断信号 (SIGINT) 到进程组...")
        
        if self.process.state() == QProcess.Running:
            pid = self.process.processId()
            if pid > 0:
                try:
                    # 获取进程组ID并发送信号
                    pgid = os.getpgid(pid)
                    os.killpg(pgid, signal.SIGINT)
                    self.log_output.print(f"已向进程组 {pgid} (父进程 {pid}) 发送 SIGINT 信号。")
                    # 不立即更新 is_simulation_running 或按钮状态
                    # 等待 _process_finished 或 _process_error 回调来处理
                except Exception as e: # 使用更通用的异常捕获
                    self.log_output.print(f"发送 SIGINT 信号到进程组失败: {e}，将尝试强制终止 (SIGKILL)。")
                    self.process.kill() # 发送SIGINT失败后的回退方案
                    self.is_simulation_running = False # 强制终止后立即更新状态
                    self.run_button.setEnabled(True)
                    self.stop_button.setEnabled(False)
            else:
                 self.log_output.print("无法获取有效的进程 ID，无法发送 SIGINT。")
                 self.is_simulation_running = False # 无法发送信号，认为已停止
                 self.run_button.setEnabled(True)
                 self.stop_button.setEnabled(False)
        else:
             self.log_output.print("进程未在运行状态。")
             self.is_simulation_running = False # 进程未运行，更新状态
             self.run_button.setEnabled(True)
             self.stop_button.setEnabled(False)
        
        # 注意：按钮状态的最终恢复现在依赖于进程结束的回调函数
    
    def view_interim_report(self):
        """查看最新的中间总结报告"""
        project_path = self.project_path.text()
        if not project_path:
            QMessageBox.warning(self, "警告", "请先设置 Sentaurus 工程目录！")
            return

        reports_dir = os.path.join(project_path, 'Reports')
        if not os.path.isdir(reports_dir):
            QMessageBox.warning(self, "警告", f"报告目录不存在: {reports_dir}")
            return

        # 查找所有中间报告文件
        interim_report_pattern = os.path.join(reports_dir, 'report_summary_iter_*.md')
        interim_reports = glob.glob(interim_report_pattern)

        if not interim_reports:
            QMessageBox.information(self, "提示", f"在目录 {reports_dir} 中未找到任何中间总结报告 (形如 report_summary_iter_*.md)。")
            return

        # 根据修改时间对报告进行排序（最新的在前）
        try:
            interim_reports.sort(key=os.path.getmtime, reverse=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"排序报告文件时出错: {e}")
            return
        
        # 恢复：查找最新的报告文件
        if not interim_reports: # 再次检查以防万一
            QMessageBox.information(self, "提示", "未找到任何中间总结报告。") # 更新提示信息
            return
            
        report_to_open = interim_reports[0] # 直接取排序后的第一个，即最新的
        self.log_output.print(f"找到最新的中间总结报告: {report_to_open}")

        # 使用系统默认程序打开文件
        try:
            if sys.platform == 'win32':
                os.startfile(report_to_open)
            elif sys.platform == 'darwin': # macOS
                subprocess.call(['open', report_to_open])
            else: # linux variants
                subprocess.call(['xdg-open', report_to_open])
            self.log_output.print(f"尝试打开报告文件: {report_to_open}")
        except Exception as e:
            self.log_output.print(f"无法自动打开报告文件: {e}")
            QMessageBox.warning(self, "提示", f"无法自动打开文件 {report_to_open}。请手动打开。错误: {e}")
            
    def view_final_report(self):
        """查看最终报告"""
        use_real_mode = HAS_SWB_MODULES or self.force_real_mode.isChecked()
        if not use_real_mode or not self.swb_interaction:
            QMessageBox.information(self, "模拟模式", "模拟模式: 最终报告功能不可用")
            return
            
        try:
            report_path = os.path.join(self.project_path.text(), "Reports", "final_report.md")
            if not os.path.exists(report_path):
                QMessageBox.warning(self, "报告不可用", "最终报告尚未生成")
                return
                
            # 打开报告文件
            os.system(f"xdg-open {report_path}")
            self.log_output.print(f"已打开最终报告: {report_path}")
            
        except Exception as e:
            self.log_output.print(f"打开最终报告出错: {str(e)}")
            QMessageBox.warning(self, "打开失败", f"打开最终报告失败: {str(e)}")
            
    def view_latest_iteration_report(self):
        """查看最新的迭代报告"""
        project_path = self.project_path.text()
        if not project_path:
            QMessageBox.warning(self, "警告", "请先设置 Sentaurus 工程目录！")
            return

        # 更新：迭代报告直接位于 Reports 目录
        reports_dir = os.path.join(project_path, 'Reports') 
        if not os.path.isdir(reports_dir):
            QMessageBox.warning(self, "警告", f"报告目录不存在: {reports_dir}")
            return

        # 查找所有迭代报告文件
        iteration_report_pattern = os.path.join(reports_dir, 'report_iteration_*.md')
        iteration_reports = glob.glob(iteration_report_pattern)

        if not iteration_reports:
            QMessageBox.information(self, "提示", f"在目录 {reports_dir} 中未找到任何迭代报告 (形如 report_iteration_*.md)。")
            return

        # 找到最新的报告文件（根据修改时间）
        try:
            latest_report = max(iteration_reports, key=os.path.getmtime)
            self.log_output.print(f"找到最新的迭代报告: {latest_report}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查找最新迭代报告时出错: {e}")
            return

        # 使用系统默认程序打开文件
        try:
            if sys.platform == 'win32':
                os.startfile(latest_report)
            elif sys.platform == 'darwin': # macOS
                subprocess.call(['open', latest_report])
            else: # linux variants
                subprocess.call(['xdg-open', latest_report])
            self.log_output.print(f"尝试打开报告文件: {latest_report}")
        except Exception as e:
            self.log_output.print(f"无法自动打开报告文件: {e}")
            QMessageBox.warning(self, "提示", f"无法自动打开文件 {latest_report}。请手动打开。错误: {e}")
            
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self.is_simulation_running:
            reply = QMessageBox.question(self, "确认退出", 
                                      "仿真正在进行中，确定要退出吗?",
                                      QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.log_output.print("用户确认退出，正在发送中断信号 (SIGINT) 到进程组... ")
                if self.process.state() == QProcess.Running:
                    pid = self.process.processId()
                    if pid > 0:
                        try:
                            # 获取进程组ID并发送信号
                            pgid = os.getpgid(pid)
                            os.killpg(pgid, signal.SIGINT)
                            self.log_output.print(f"已向进程组 {pgid} (父进程 {pid}) 发送 SIGINT 信号。")
                        except Exception as e: # 使用更通用的异常捕获
                            self.log_output.print(f"发送 SIGINT 信号到进程组失败: {e}，进程可能已经退出。")
                # 无论是否成功发送信号，都接受关闭事件
                self.is_simulation_running = False # 标记为不再运行，防止重复操作
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
        
    @Slot()
    def _read_process_output(self):
        """读取外部自动化进程输出并显示到日志区"""
        try:
            data = self.process.readAll().data().decode('utf-8', errors='ignore')
            if not data.strip():
                return
            self.log_output.print("------ 进程输出 ------")
            for line in data.splitlines():
                self.log_output.print(line)
        except Exception as e:
            self.log_output.print(f"读取进程输出错误: {e}")
            
    @Slot(QProcess.ProcessState)
    def _process_state_changed(self, state):
        """处理进程状态变化"""
        states = {
            QProcess.NotRunning: "未运行",
            QProcess.Starting: "正在启动",
            QProcess.Running: "运行中"
        }
        self.log_output.print(f"进程状态变化: {states.get(state, '未知状态')}")
        
    @Slot(int, QProcess.ExitStatus)
    def _process_finished(self, exit_code, exit_status):
        """处理进程完成事件"""
        if exit_status == QProcess.NormalExit:
            self.log_output.print(f"进程正常结束，退出码: {exit_code}")
        else:
            self.log_output.print("进程异常结束")
        
        # 恢复界面状态
        self.is_simulation_running = False
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    @Slot(QProcess.ProcessError)
    def _process_error(self, error):
        """处理进程错误"""
        errors = {
            QProcess.FailedToStart: "启动失败",
            QProcess.Crashed: "崩溃",
            QProcess.Timedout: "超时",
            QProcess.WriteError: "写入错误",
            QProcess.ReadError: "读取错误",
            QProcess.UnknownError: "未知错误"
        }
        self.log_output.print(f"进程错误: {errors.get(error, '未知错误类型')}")
        if error == QProcess.FailedToStart:
            self.log_output.print("请检查Python路径和脚本是否存在")
            
        # 显示错误输出
        error_output = self.process.readAllStandardError().data().decode('utf-8', errors='ignore')
        if error_output:
            self.log_output.print("错误输出:")
            for line in error_output.splitlines():
                self.log_output.print(f"  {line}")
        
        # 恢复界面状态
        self.is_simulation_running = False
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def get_param_data_from_table(self):
        """从参数表格获取数据"""
        params = {}
        for row in range(self.param_table.rowCount()):
            param_name = self.param_table.item(row, 0).text()
            param_value_text = self.param_table.item(row, 1).text()
            try:
                # 尝试转换为数值类型
                if '.' in param_value_text:
                    param_value = float(param_value_text)
                else:
                    param_value = int(param_value_text)
            except ValueError:
                # 如果无法转换，保留为字符串
                param_value = param_value_text
            params[param_name] = param_value
        return params

    def check_project_initialized(self):
        """检查项目是否已初始化"""
        project_path = self.project_path.text()
        if not project_path or not os.path.exists(project_path):
            QMessageBox.warning(self, "错误", f"项目路径不存在: {project_path}")
            return False
        return True

def main_ui():
    # 设置环境变量，避免Qt警告
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    window = AutoSimGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main_ui() 
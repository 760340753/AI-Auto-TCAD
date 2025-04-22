#!/bin/bash
# FS-IGBT 全自动仿真 GUI 启动脚本

# 设置环境变量
export LANG=en_US.UTF-8
export PYTHONIOENCODING=UTF-8
export LC_ALL=en_US.UTF-8
export DISPLAY=:0
export QT_XKB_CONFIG_ROOT=/usr/share/X11/xkb
export PYSIDE_GUI=1

# 进入项目目录
cd /home/tcad/STDB/MyProjects/AI_Lab/FS_IGBT

# 激活虚拟环境
source .fs_auto_sim_env/bin/activate

# 运行简化版的 PySide2 界面
python -c "
import os
import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide2.QtCore import Qt

class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FS-IGBT 项目 - 仿真启动器')
        self.setGeometry(100, 100, 500, 300)
        
        # 中央控件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # 添加标题
        title = QLabel('FS-IGBT 项目仿真控制面板')
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # 状态标签
        self.status = QLabel('项目目录: /home/tcad/STDB/MyProjects/AI_Lab/FS_IGBT')
        layout.addWidget(self.status)
        
        # 命令行模式按钮
        console_btn = QPushButton('启动命令行模式')
        console_btn.clicked.connect(self.run_console)
        layout.addWidget(console_btn)
        
        # 检查环境按钮
        check_btn = QPushButton('检查环境')
        check_btn.clicked.connect(self.check_env)
        layout.addWidget(check_btn)
        
        # 退出按钮
        exit_btn = QPushButton('退出')
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)
    
    def run_console(self):
        from fs_auto_sim.console_ui import console_ui
        self.hide()
        try:
            console_ui()
        finally:
            self.show()
    
    def check_env(self):
        import subprocess
        result = subprocess.run(['python', '-c', 'import sys; print(\"Python版本:\", sys.version); import PySide2; print(\"PySide2版本:\", PySide2.__version__)'], capture_output=True, text=True)
        from PySide2.QtWidgets import QMessageBox
        QMessageBox.information(self, '环境检查', result.stdout)

app = QApplication(sys.argv)
window = SimpleGUI()
window.show()
sys.exit(app.exec_())
"

# 如果GUI失败，回退到命令行
if [ $? -ne 0 ]; then
    echo "GUI启动失败，切换到命令行模式..."
    python -m fs_auto_sim.console_ui
fi 
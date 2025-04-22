import os
import sys
import subprocess

def install():
    """在当前工作目录创建虚拟环境并安装本包。"""
    env_dir = os.path.join(os.getcwd(), '.fs_auto_sim_env')
    python_exe = sys.executable
    # 检查 Python 版本
    if sys.version_info[:2] != (3, 11):
        print("请使用 Python 3.11 来安装本包。当前版本: {}".format(sys.version))
        sys.exit(1)
    # 创建虚拟环境
    if not os.path.exists(env_dir):
        print(f"创建虚拟环境: {env_dir}")
        subprocess.check_call([python_exe, '-m', 'venv', env_dir])
    else:
        print(f"虚拟环境已存在: {env_dir}")
    # 安装本包
    pip_exe = os.path.join(env_dir, 'bin', 'pip')
    print("安装包依赖...")
    subprocess.check_call([pip_exe, 'install', '--upgrade', 'pip'])
    subprocess.check_call([pip_exe, 'install', '-e', '.'])
    print("安装完成！请执行以下命令以激活虚拟环境:")
    print(f"  source {env_dir}/bin/activate")
    print("然后运行: fs-sim-ui")


def ui():
    """启动桌面 GUI（如果可能），否则使用命令行界面"""
    # 优先使用 PySide2 图形界面
    try:
        import PySide2
        # 设置环境变量标记使用PySide2
        os.environ['PYSIDE_GUI'] = '1'
        print("正在启动 PySide2 图形界面...")
        from fs_auto_sim.pyside_gui import main_ui
        main_ui()
    except ImportError as e:
        print(f"PySide2 图形界面启动失败: {e}")
        try:
            # 尝试使用标准 PySimpleGUI
            import PySimpleGUI
            print("正在启动 PySimpleGUI 图形界面...")
            from fs_auto_sim.gui import main_ui
            main_ui()
        except ImportError as e:
            print(f"图形界面启动失败: {e}")
            print("将使用命令行界面代替...\n")
            from fs_auto_sim.console_ui import console_ui
            console_ui()

def console():
    """直接启动命令行版UI"""
    from fs_auto_sim.console_ui import console_ui
    console_ui()

# 命令行直接调用
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python cli.py [install|ui|console]")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "install":
        install()
    elif command == "ui":
        ui()
    elif command == "console":
        console()
    else:
        print(f"未知命令: {command}")
        print("可用命令: install, ui, console")
        sys.exit(1) 
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
    """启动桌面 GUI"""
    # 首先尝试导入PySimpleGUI
    try:
        import PySimpleGUI
        # 如果导入成功，启动图形界面
        from fs_auto_sim.gui import main_ui
        main_ui()
    except (ImportError, ModuleNotFoundError) as e:
        # 如果无法导入PySimpleGUI或_tkinter，使用控制台UI作为备选
        print(f"无法启动图形界面: {e}")
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
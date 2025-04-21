import os
import sys
import time
import threading

def console_ui():
    """命令行版UI，不需要图形界面，便于演示"""
    print("\n==== AI-Auto-TCAD 全自动仿真工具 (命令行版) ====\n")
    
    # 默认值
    project_path = input("请输入Sentaurus工程目录 [默认:/home/tcad/STDB/MyProjects/AI_Lab/FS_IGBT]: ")
    if not project_path:
        project_path = "/home/tcad/STDB/MyProjects/AI_Lab/FS_IGBT"
    
    api_key = input("请输入DeepSeek API Key (可选，仿真模式可留空): ")
    
    # 显示性能目标
    print("\n性能目标描述示例:")
    print("  - 增加IGBT击穿电压同时保持导通电压（微伏级）")
    print("  - 提高MOSFET漏源耐压，同时保证正向导通特性良好")
    
    target = input("\n请输入您的性能目标描述: ")
    if not target:
        target = "增加IGBT击穿电压同时保持导通电压（微伏级）"
    
    # 模拟加载初始参数
    print("\n正在加载初始参数...")
    time.sleep(1)
    
    # 示例参数
    params = {
        'Xmax': 6,
        'Wgate': 1.8,
        'Wnplus': 2,
        'Wpplus': 5.5,
        'Wemitter': 4.5,
        'Ymax': 80,
        'Ndrift': '1e14',
        'Pbase': '5e16',
        'Pplus': '5e19',
        'Nplus': '5e19'
    }
    
    print("\n当前初始参数:")
    for k, v in params.items():
        print(f"  {k}: {v}")
    
    # 交互式修改参数
    modify = input("\n是否修改参数? (y/n): ")
    if modify.lower() == 'y':
        param_name = input("请输入要修改的参数名: ")
        if param_name in params:
            new_value = input(f"请输入{param_name}的新值: ")
            params[param_name] = new_value
            print(f"已更新{param_name}={new_value}")
        else:
            print(f"参数{param_name}不存在")
    
    # 检查参数唯一性
    print("\n正在检查参数唯一性...")
    time.sleep(1.5)
    print("参数组合检查通过，未发现重复实验")
    
    # 确认启动
    start = input("\n是否开始全自动仿真? (y/n): ")
    if start.lower() != 'y':
        print("已取消运行")
        return
    
    # 模拟进度条
    print("\n开始全自动仿真流程...")
    
    # 启动一个线程来显示进度
    def show_progress():
        for i in range(101):
            # 清除当前行
            sys.stdout.write("\r")
            # 显示进度条
            progress = "=" * (i // 2)
            spaces = " " * (50 - (i // 2))
            sys.stdout.write(f"进度: [{progress}{spaces}] {i}%")
            sys.stdout.flush()
            time.sleep(0.1)
            
            # 每10%显示一些日志信息
            if i % 10 == 0 and i > 0:
                print(f"\n[Info] 仿真进度: {i}% 完成")
                if i == 30:
                    print("[Info] 节点创建完成，开始执行仿真...")
                elif i == 50:
                    print("[Info] 仿真计算中，等待结果...")
                elif i == 70:
                    print("[Info] 正在分析结果，生成优化建议...")
                elif i == 90:
                    print("[Info] 正在生成报告...")
        
        print("\n\n[Info] 仿真流程已完成!")
        print("\n可以查看以下报告:")
        print(f"  - 阶段报告: {project_path}/Reports/iteration_report.md")
        print(f"  - 最终报告: {project_path}/Reports/final_report.md")
    
    # 启动进度线程
    threading.Thread(target=show_progress, daemon=True).start()
    
    # 主线程等待进度完成
    time.sleep(12)
    
if __name__ == "__main__":
    console_ui() 
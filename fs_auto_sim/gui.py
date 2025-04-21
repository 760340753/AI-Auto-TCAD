import os
import sys
import threading
try:
    # 尝试使用 Qt 后端
    import PySimpleGUIQt as sg
    sg.theme('LightBlue')  # Qt 版本亦支持主题
except ImportError:
    # 回退到 tkinter 后端
    import PySimpleGUI as sg

# 简化版 GUI，用于测试界面
def main_ui():
    sg.theme('LightBlue')
    layout = [
        [sg.Text('Sentaurus 工程目录:'), sg.InputText(key='-PROJECT-'), sg.FolderBrowse()],
        [sg.Text('DeepSeek API Key (可选):'), sg.InputText(key='-APIKEY-')],
        [sg.Text('性能目标描述:'), sg.Multiline('增加IGBT击穿电压同时保持导通电压（微伏级）', key='-TARGET-', size=(60,3))],
        [sg.Button('加载初始参数', key='-LOAD-')],
        [sg.Table(values=[], headings=['参数','值'], key='-PARAM_TABLE-', enable_events=True,
                  auto_size_columns=True, justification='center', num_rows=10)],
        [sg.Button('检查参数唯一性', key='-CHECK-'), sg.Button('开始全自动仿真', key='-RUN-')],
        [sg.ProgressBar(100, orientation='h', size=(40, 20), key='-PROG-')],
        [sg.Multiline(key='-LOG-', size=(80, 20), autoscroll=True, background_color='black', text_color='white')],
        [sg.Button('查看阶段报告', key='-VIEW_INTERIM-'), sg.Button('查看最终报告', key='-VIEW_FINAL-'), sg.Button('退出')]
    ]
    window = sg.Window('AI-Auto-TCAD 全自动仿真工具', layout, finalize=True)
    
    # 默认工程目录为当前FS-IGBT路径
    window['-PROJECT-'].update('/home/tcad/STDB/MyProjects/AI_Lab/FS_IGBT')
    window['-LOG-'].print('[GUI测试模式] 界面加载完成，可以测试各按钮交互效果')
    window['-LOG-'].print('提示: 此为简化版GUI，未连接实际仿真功能')

    # 模拟初始参数数据
    sample_params = [
        ['Xmax', '6'],
        ['Wgate', '1.8'],
        ['Wnplus', '2'],
        ['Wpplus', '5.5'],
        ['Wemitter', '4.5'],
        ['Ymax', '80'],
        ['Ndrift', '1e14'],
        ['Pbase', '5e16'],
        ['Pplus', '5e19'],
        ['Nplus', '5e19']
    ]

    # 模拟加载初始参数
    def load_params():
        window['-PARAM_TABLE-'].update(sample_params)
        window['-LOG-'].print('初始参数加载完成')
        
    # 模拟运行
    def fake_run():
        total = 100
        for i in range(total+1):
            if i % 10 == 0:
                window['-LOG-'].print(f'仿真进度: {i}%')
            window['-PROG-'].update(i)
            # 最后添加完成消息
            if i == total:
                window['-LOG-'].print('仿真流程已完成')
            import time
            time.sleep(0.05)

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, '退出'):
            break

        # 处理按钮事件
        if event == '-LOAD-':
            load_params()
            
        elif event == '-CHECK-':
            window['-LOG-'].print('检查参数唯一性...')
            import time
            time.sleep(1)  # 模拟一些延迟
            sg.popup('参数组合检查通过，未发现重复实验')
            
        elif event == '-RUN-':
            # 启动模拟进度条线程
            window['-LOG-'].print('开始自动仿真流程...')
            threading.Thread(target=fake_run, daemon=True).start()
            
        elif event == '-VIEW_INTERIM-':
            window['-LOG-'].print('尝试打开阶段报告...')
            sg.popup('阶段报告查看功能测试')
            
        elif event == '-VIEW_FINAL-':
            window['-LOG-'].print('尝试打开最终报告...')
            sg.popup('最终报告查看功能测试')

    window.close()
    
# 直接运行时启动GUI
if __name__ == '__main__':
    main_ui() 
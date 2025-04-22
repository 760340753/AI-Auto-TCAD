#!/usr/bin/env python
import os
import datetime
import time
import sys
import logging
from swbpy2 import *
from swbpy2.core.core import STATE_NONE, STATE_READY, STATE_NORMAL, STATE_DONE, STATE_VIRTUAL, STATE_FAILED

# ======================================
# 配置区
# ======================================
PROJECT_PATH = '/home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old'
# 设置 AUTO_RUN 为 True 表示自动运行仿真；False 表示仅添加新实验，等待手动运行
AUTO_RUN = True

# 迭代报告保存路径
REPORT_PATH = os.path.join(PROJECT_PATH, "iteration_report.md")

# 日志配置
LOG_DIR = os.path.join(PROJECT_PATH, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, f"swb_auto_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置等待时间(秒)
WAIT_TIME_AFTER_SAVE = 5       # 保存后等待时间
WAIT_TIME_AFTER_PREPROCESS = 5 # 预处理后等待时间
WAIT_TIME_BETWEEN_CHECKS = 10  # 状态检查间隔
MAX_WAIT_TIME = 300            # 最大等待时间(5分钟)

# ======================================
# sde 参数（需要迭代的器件结构参数）
# 参数顺序：Wtot, Wg, Wcp, Wcs, Tdrift, TPc, TNb, TNa, TPb, TPa, Tox, Tpoly, Tcathode, Zeropoint,
#             Pc, Nb, Na, Ndrift, Npoly, Pb, Pa, x, Length
sde_params = {
    "Wtot": 50,
    "Wg": 10,
    "Wcp": 15,
    "Wcs": 4,
    "Tdrift": 320,
    "TPc": 0.2,
    "TNb": 1.5,
    "TNa": 1.5,
    "TPb": 5,
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
    "Length": 30
}

# ======================================
# sdevice 参数（保持不变的部分）
# 参数顺序：eLifetime, angle, Vanode, LA, CL, LK, Vdd
sdevice_params = ["-", 90, 800, 5e-9, 0.1e-6, 5e-9, 2000]

# ======================================
# 组合所有参数，注意顺序必须与工程中新增实验时的参数顺序一致
def get_combined_parameters():
    # sde 参数顺序（23 个）
    sde_order = ["Wtot", "Wg", "Wcp", "Wcs", "Tdrift", "TPc", "TNb", "TNa", "TPb", "TPa",
                 "Tox", "Tpoly", "Tcathode", "Zeropoint", "Pc", "Nb", "Na", "Ndrift",
                 "Npoly", "Pb", "Pa", "x", "Length"]
    sde_list = [sde_params.get(key, 0) for key in sde_order]
    return sde_list + sdevice_params

# ======================================
# 检查SWB环境变量是否正确设置
def check_env():
    if not os.environ.get('STROOT'):
        logger.error("环境变量STROOT未设置，请确保已正确加载Sentaurus环境")
        return False
    
    if not os.environ.get('STRELEASE'):
        logger.error("环境变量STRELEASE未设置，请确保已正确加载Sentaurus环境")
        return False
    
    logger.info(f"检测到Sentaurus环境: STROOT={os.environ.get('STROOT')}, STRELEASE={os.environ.get('STRELEASE')}")
    return True

# ======================================
# 生成迭代报告（Markdown格式）
def generate_report(combined_params, iteration, run_info=None):
    report_lines = []
    report_lines.append("# 仿真迭代报告")
    report_lines.append(f"**迭代编号：** {iteration}")
    report_lines.append(f"**日期：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    report_lines.append("## sde 参数")
    for key in ["Wtot", "Wg", "Wcp", "Wcs", "Tdrift", "TPc", "TNb", "TNa", "TPb", "TPa",
                "Tox", "Tpoly", "Tcathode", "Zeropoint", "Pc", "Nb", "Na", "Ndrift",
                "Npoly", "Pb", "Pa", "x", "Length"]:
        report_lines.append(f"- **{key}**: {sde_params.get(key, 'N/A')}")
    
    report_lines.append("\n## sdevice 参数 (固定)")
    sdevice_order = ["eLifetime", "angle", "Vanode", "LA", "CL", "LK", "Vdd"]
    for key, value in zip(sdevice_order, sdevice_params):
        report_lines.append(f"- **{key}**: {value}")
    
    report_lines.append("\n## 操作记录")
    report_lines.append("新增实验参数已更新，并触发相应的仿真运行。")
    
    if run_info:
        report_lines.append("\n## 运行信息")
        for key, value in run_info.items():
            report_lines.append(f"- **{key}**: {value}")
    
    report_lines.append("\n---\n")
    
    report_content = "\n".join(report_lines)
    
    # 若报告文件不存在，则创建
    if not os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "w") as f:
            f.write("")
    
    # 追加新报告内容
    with open(REPORT_PATH, "a") as f:
        f.write(report_content)
    
    logger.info(f"报告已生成: {REPORT_PATH}")

# ======================================
# 监控并运行新添加的叶节点
def run_new_nodes(tree, deck):
    logger.info("开始检查新添加的叶节点...")
    # 获取所有叶节点
    leaf_nodes = tree.AllLeafNodes()
    # 按照节点ID排序，最新添加的节点通常有最大的ID
    leaf_nodes.sort()
    
    if not leaf_nodes:
        logger.error("没有找到叶节点！")
        return False
    
    # 获取最后添加的节点(通常是ID最大的)
    latest_node = leaf_nodes[-1]
    logger.info(f"最新添加的节点ID: {latest_node}")
    
    # 获取从根节点到最新节点的路径
    node_path = tree.NodeAncestors(latest_node)
    node_path.append(latest_node)  # 添加节点本身
    logger.info(f"节点路径: {node_path}")
    
    # 逐个检查路径上的节点并尝试运行
    run_success = True
    for node_id in node_path:
        node_status = tree.NodeStatus(node_id)
        node_tools = tree.NodeTools(node_id)
        logger.info(f"节点ID: {node_id}, 状态: {node_status}, 工具: {node_tools}")
        
        # 如果节点状态是NONE或READY，尝试运行它
        if node_status in (STATE_NONE, STATE_READY):
            try:
                logger.info(f"尝试运行节点 {node_id}...")
                # 先检查这个节点关联了哪些工具
                tools = tree.NodeTools(node_id)
                if tools:
                    # 使用deck.run指定节点运行
                    logger.info(f"使用deck.run运行节点 {node_id}")
                    deck.run(node_id)
                    time.sleep(2)  # 短暂等待启动
                else:
                    logger.info(f"节点 {node_id} 没有关联工具，跳过")
            except Exception as e:
                logger.error(f"运行节点 {node_id} 失败: {str(e)}")
                run_success = False
    
    return run_success

# ======================================
# 等待并监控节点状态
def wait_for_nodes_completion(tree, timeout=MAX_WAIT_TIME):
    logger.info(f"开始等待节点完成，最大等待时间: {timeout}秒")
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        # 检查所有节点状态
        running_nodes = tree.SearchNodesByStatus("all", STATE_NORMAL)
        ready_nodes = tree.SearchNodesByStatus("all", STATE_READY)
        none_nodes = tree.SearchNodesByStatus("all", STATE_NONE)
        done_nodes = tree.SearchNodesByStatus("all", STATE_DONE)
        failed_nodes = tree.SearchNodesByStatus("all", STATE_FAILED)
        
        logger.info(f"当前状态 - 运行中: {len(running_nodes)}, 就绪: {len(ready_nodes)}, " +
                   f"未处理: {len(none_nodes)}, 完成: {len(done_nodes)}, 失败: {len(failed_nodes)}")
        
        # 如果没有正在运行或准备运行的节点，退出等待
        if not running_nodes and not ready_nodes and not none_nodes:
            logger.info("所有节点已完成运行或失败")
            return True
        
        # 等待一段时间再检查
        logger.info(f"等待 {WAIT_TIME_BETWEEN_CHECKS} 秒后再次检查...")
        time.sleep(WAIT_TIME_BETWEEN_CHECKS)
    
    logger.warning(f"等待超时！已等待 {timeout} 秒")
    return False

# ======================================
# 主函数：添加新实验并运行
def main():
    # 检查环境是否就绪
    if not check_env():
        logger.error("环境检查失败，请确保正确安装并配置Sentaurus环境")
        sys.exit(1)
        
    try:
        logger.info("=== 开始执行自动化仿真脚本 ===")
        logger.info(f"项目路径: {PROJECT_PATH}")
        logger.info(f"自动运行模式: {'是' if AUTO_RUN else '否'}")
        logger.info(f"Python版本: {sys.version}")
        
        combined_params = get_combined_parameters()  # 共 23 + 7 = 30 个参数
        logger.info(f"组合参数数量: {len(combined_params)}")
        
        # 打开工程
        logger.info("正在打开SWB工程...")
        deck = Deck(PROJECT_PATH, True)
        tree = deck.getGtree()
        logger.info("成功打开SWB工程")
        
        # 记录添加前的节点数量
        before_nodes = tree.AllNodes()
        logger.info(f"添加前节点数量: {len(before_nodes)}")
        
        # 添加新实验（参数替换）
        try:
            logger.info("正在添加新实验...")
            tree.AddPath(pvalues=combined_params)
            logger.info("新实验添加成功")
        except RuntimeError as e:
            logger.error(f"添加新实验失败: {str(e)}")
            return
        
        # 记录添加后的节点数量
        after_nodes = tree.AllNodes()
        logger.info(f"添加后节点数量: {len(after_nodes)}")
        logger.info(f"新增节点数量: {len(after_nodes) - len(before_nodes)}")
        
        # 保存工程并刷新工程树
        logger.info("正在保存工程...")
        deck.save()
        logger.info(f"等待 {WAIT_TIME_AFTER_SAVE} 秒让系统处理保存操作...")
        time.sleep(WAIT_TIME_AFTER_SAVE)
        
        logger.info("正在刷新工程...")
        deck.reload()
        
        run_info = {
            "开始时间": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "状态": "未运行"
        }
        
        # 如果设置了 AUTO_RUN，则预处理并运行所有节点
        if AUTO_RUN:
            logger.info("开始自动运行流程...")
            
            # 预处理
            logger.info("执行预处理...")
            deck.preprocess()
            logger.info(f"等待 {WAIT_TIME_AFTER_PREPROCESS} 秒让预处理完成...")
            time.sleep(WAIT_TIME_AFTER_PREPROCESS)
            
            # 通过调用deck.run()开始运行
            logger.info("执行全局运行...")
            deck.run()
            time.sleep(5)  # 等待运行启动
            
            # 如果全局run命令不成功，尝试单独运行新节点
            logger.info("尝试单独运行新添加的节点...")
            node_run_success = run_new_nodes(tree, deck)
            
            # 等待所有节点完成
            wait_success = wait_for_nodes_completion(tree)
            
            run_info["状态"] = "完成" if wait_success else "超时"
            run_info["节点运行结果"] = "成功" if node_run_success else "部分失败"
            run_info["结束时间"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info("自动运行流程结束")
        else:
            logger.info("新实验已添加，请手动在 SWB 界面运行仿真")
            run_info["状态"] = "仅添加实验，未运行"
        
        # 最后再调用 reload() 更新 GUI 显示
        logger.info("最终刷新工程...")
        deck.reload()
        
        # 生成迭代报告
        logger.info("生成迭代报告...")
        generate_report(combined_params, iteration=1, run_info=run_info)
        
        logger.info("=== 脚本执行完成 ===")
        
    except Exception as e:
        logger.error(f"发生未处理的异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 
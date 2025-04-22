#!/usr/bin/env python3.11
import os
import datetime
import time
from swbpy2 import *
# Import status constants
from swbpy2.core.core import STATE_READY, STATE_NONE, STATE_DONE, STATE_FAILED, STATE_VIRTUAL, STATE_RUNNING, STATE_QUEUED, STATE_PENDING

# ======================================
# 配置区
# ======================================
PROJECT_PATH = '/home/tcad/STDB/MyProjects/AI_Lab/MCT-SEE-Normal-Old'
# 设置 AUTO_RUN 为 True 表示自动运行仿真；False 表示仅添加新实验，等待手动运行
AUTO_RUN = True

# 迭代报告保存路径
REPORT_PATH = os.path.join(PROJECT_PATH, "iteration_report.md")

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
    "Length": 35
}

# ======================================
# sdevice 参数（保持不变的部分）
# 参数顺序：eLifetime, angle, Vanode
sdevice_params = ["-", 90, 800]

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
# 生成迭代报告（Markdown格式）
def generate_report(combined_params, iteration, run_status):
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
    sdevice_order = ["eLifetime", "angle", "Vanode"]
    for key, value in zip(sdevice_order, sdevice_params):
        report_lines.append(f"- **{key}**: {value}")
    
    report_lines.append("\n## 操作记录")
    if run_status:
        report_lines.append(f"新增实验参数已更新，并触发了 {run_status['run_count']} 个新增节点的运行。")
        if run_status['fail_count'] > 0:
            report_lines.append(f"**警告：** {run_status['fail_count']} 个节点运行失败。")
    else:
        report_lines.append("新增实验参数已更新，设置为手动运行。")
    report_lines.append("\n---\n")
    
    report_content = "\n".join(report_lines)
    with open(REPORT_PATH, "a") as f:
        f.write(report_content)

# ======================================
# 主函数：添加新实验并运行 (修改后)
def main():
    combined_params = get_combined_parameters()
    run_status_report = None # For reporting

    # 打开工程
    print(f"Opening project: {PROJECT_PATH}")
    try:
        deck = Deck(PROJECT_PATH, True)
        tree = deck.getGtree()
        print("Project opened successfully.")
    except Exception as e:
        print(f"Failed to open project: {e}")
        return

    # 1. 获取添加前的叶节点和所有节点 IDs
    try:
        # Get both leaf nodes and all nodes before adding experiment
        old_leaf_node_ids = set(tree.AllLeafNodes())
        old_all_node_ids = set(tree.AllNodes())
        print(f"Before adding: {len(old_all_node_ids)} total nodes exist ({len(old_leaf_node_ids)} leaf nodes).")
    except Exception as e:
        print(f"Failed to get existing nodes: {e}")
        return

    # 2. 添加新实验并保存
    try:
        print("Adding new experiment...")
        tree.AddPath(pvalues=combined_params)
        print("New experiment structure added.")
        deck.save()
        print("Project saved.")
        # 3. Reload to ensure the tree object reflects saved changes
        deck.reload()
        # Add a short delay to allow SWB to potentially update its state
        print("Waiting for SWB state update (2 seconds)...")
        time.sleep(2)
        tree = deck.getGtree() # Refresh tree object instance
        print("Project reloaded.")
    except RuntimeError as e:
        print(f"Failed to add new experiment: {e}")
        return
    except Exception as e:
        print(f"Error saving or reloading project: {e}")
        return

    # 4. 获取添加后的叶节点和所有节点 IDs
    try:
        # Get BOTH leaf nodes and all nodes after adding experiment
        current_all_node_ids = set(tree.AllNodes())
        current_leaf_node_ids = set(tree.AllLeafNodes())
        print(f"After adding: {len(current_all_node_ids)} total nodes exist ({len(current_leaf_node_ids)} leaf nodes).")
        
        # Debug: Print the full node IDs
        print("DEBUG - Old leaf nodes:", old_leaf_node_ids)
        print("DEBUG - Current leaf nodes:", current_leaf_node_ids)
    except Exception as e:
        print(f"Failed to get updated nodes: {e}")
        return

    # 5. 计算新添加的节点 IDs - BOTH leaf nodes and ALL nodes
    added_leaf_node_ids = current_leaf_node_ids - old_leaf_node_ids
    added_all_node_ids = current_all_node_ids - old_all_node_ids
    
    if not added_leaf_node_ids:
        print("WARNING: No new leaf nodes detected after adding experiment. Check parameters or project state.")
        # Optionally decide whether to exit or log differently
    else:
        print(f"Detected {len(added_leaf_node_ids)} newly added leaf node IDs: {added_leaf_node_ids}")
        print(f"Detected {len(added_all_node_ids)} total newly added node IDs: {added_all_node_ids}")
        
        # Sort the newly added nodes by ID to run them in proper order
        all_new_nodes_to_run = sorted(list(added_all_node_ids))
        print(f"Will run only the new nodes in this order: {all_new_nodes_to_run}")
        
        # In case we somehow miss a node with the direct comparison, also try a heuristic approach
        # but only if we have at least one new node already identified
        if len(all_new_nodes_to_run) > 0 and len(all_new_nodes_to_run) < 3:  # If we found suspiciously few nodes
            print("Found fewer nodes than expected. Adding additional check:")
            
            # Calculate the expected range for a complete experiment
            lowest_new_id = min(all_new_nodes_to_run)
            highest_new_id = max(all_new_nodes_to_run)
            expected_range = set(range(lowest_new_id, highest_new_id + 1))
            
            # Check if any nodes in the expected range were missed
            potential_missed_nodes = expected_range - added_all_node_ids
            
            if potential_missed_nodes:
                # Check if these potential missed nodes exist in the current tree
                confirmed_missed_nodes = potential_missed_nodes.intersection(current_all_node_ids)
                
                if confirmed_missed_nodes:
                    print(f"Found {len(confirmed_missed_nodes)} potentially missed nodes: {confirmed_missed_nodes}")
                    # Add these to our run list only if they're not in the old_all_node_ids
                    for node_id in sorted(list(confirmed_missed_nodes)):
                        if node_id not in old_all_node_ids:
                            print(f"Adding node {node_id} to run list as it appears to be new")
                            all_new_nodes_to_run.append(node_id)
                    
                    # Re-sort the list
                    all_new_nodes_to_run = sorted(all_new_nodes_to_run)
                    print(f"Updated run list: {all_new_nodes_to_run}")

    # 6. 如果设置了 AUTO_RUN，预处理并仅运行新节点
    if AUTO_RUN:
        if not added_leaf_node_ids:
            print("No new nodes detected, skipping run stage.")
        else:
            print("AUTO_RUN=True, starting preprocessing...")
            try:
                deck.preprocess()
                print("Preprocessing complete.")
            except Exception as e:
                print(f"Preprocessing failed: {e}")
                # Decide if we should stop
                return

            print("Looking for runnable nodes among the new nodes...")
            run_count = 0
            fail_count = 0
            try:
                # Try to get all node states for diagnostic purposes
                print("Node states after preprocessing:")
                for state_name, state_val in [("ready", STATE_READY), ("none", STATE_NONE), 
                                             ("done", STATE_DONE), ("running", STATE_RUNNING),
                                             ("failed", STATE_FAILED)]:
                    try:
                        nodes = tree.SearchNodesByStatus(state_val)
                        print(f"  - Nodes in '{state_name}' state: {len(nodes)}")
                        if nodes and state_name in ["ready", "none"]:  # Only log details for actionable states
                            print(f"    Details: {[n for n in nodes]}")
                    except TypeError:
                        try:
                            nodes = tree.SearchNodesByStatus(state_name)
                            print(f"  - Nodes in '{state_name}' state (string param): {len(nodes)}")
                            if nodes and state_name in ["ready", "none"]:
                                print(f"    Details: {[n for n in nodes]}")
                        except Exception as e:
                            print(f"  - Could not check '{state_name}' state: {e}")
                
                # Try more direct approach - run the method that worked before (Method 3) but
                # for all identified nodes in the branch, in order
                print("\nRunning nodes in sequence, respecting potential dependencies:")
                for node_id in all_new_nodes_to_run:
                    print(f"  - Attempting to run node ID: {node_id}")
                    try:
                        # Use Method 3 which worked before
                        deck.run(nodes=[node_id])
                        print(f"    Successfully started node {node_id}.")
                        run_count += 1
                        
                        # Add a delay to allow the node to start processing
                        print(f"    Waiting 1 seconds for node to start processing...")
                        time.sleep(1)
                    except Exception as e:
                        print(f"    Failed to run node {node_id}: {e}")
                        fail_count += 1
                        
                        # Try alternative - if specific node run fails, fall back to running all
                        if node_id == all_new_nodes_to_run[-1]:  # If it's the last node
                            print("    This was the last node. Trying to run all nodes as fallback...")
                            try:
                                deck.run()
                                print("    Started general run. This will run ALL nodes needing execution.")
                            except Exception as e2:
                                print(f"    General run also failed: {e2}")
                
            except Exception as e:
                print(f"Error during node execution: {e}")
                return

            print(f"Node run attempts complete. Successfully started: {run_count}, failed: {fail_count}.")
            run_status_report = {"run_count": run_count, "fail_count": fail_count}

    else: # AUTO_RUN is False
        print("AUTO_RUN=False, new experiment added, please run simulation manually in SWB GUI.")
        run_status_report = None # Indicate manual run in report

    # 7. 生成迭代报告
    # Assuming iteration number needs logic to increment, using 1 for now
    current_iteration = 1 # Replace with actual iteration tracking if needed
    generate_report(combined_params, iteration=current_iteration, run_status=run_status_report)
    print(f"Iteration {current_iteration} report appended to {REPORT_PATH}")

if __name__ == "__main__":
    main()


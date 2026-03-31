"""任务管理器"""
import sys
import os
import traceback
import time
import threading
import queue

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.index import run_gui_task


class TaskManager:
    """任务管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.is_running = False
        self.task_data = []
    
    def scan_directory(self, target_dir):
        """扫描目录"""
        try:
            # 使用run_gui_task扫描目录
            success, success_count, total_count = run_gui_task(target_dir, self.main_window.log_queue)
            
            # 注意：run_gui_task已经处理了目录扫描和任务执行
            # 这里只需要更新UI状态
            
        except Exception as e:
            self.main_window.log_queue.put(f"扫描目录时发生错误: {e}")
    
    def run_tasks(self, target_dir):
        """运行任务"""
        self.is_running = True
        
        try:
            # 使用run_gui_task运行任务
            success, success_count, total_count = run_gui_task(target_dir, self.main_window.log_queue)
            
            # 更新状态栏
            self.main_window.update_status_bar(
                "任务完成",
                100,
                success_count,
                total_count - success_count
            )
            
        except Exception as e:
            self.main_window.log_queue.put(f"任务执行时发生错误: {e}")
        
        finally:
            self.is_running = False
            # 恢复UI状态
            self.main_window.root.after(0, self.restore_ui_state)
    
    def update_task_status(self, index, status, progress, time_str):
        """更新任务状态"""
        if index < len(self.task_data):
            self.task_data[index]["status"] = status
            self.task_data[index]["progress"] = progress
            self.task_data[index]["time"] = time_str
            
            # 更新UI
            self.main_window.root.after(0, lambda: self.main_window.update_task_list(self.task_data))
    
    def restore_ui_state(self):
        """恢复UI状态"""
        self.main_window.start_btn.config(state=tk.NORMAL)
        self.main_window.stop_btn.config(state=tk.DISABLED)
        self.main_window.select_dir_btn.config(state=tk.NORMAL)
    
    def stop(self):
        """停止任务"""
        self.is_running = False

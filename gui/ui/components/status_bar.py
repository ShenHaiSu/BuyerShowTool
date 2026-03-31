"""状态栏组件"""
import tkinter as tk
from tkinter import ttk


class StatusBar(ttk.Frame):
    """状态栏组件"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # 创建状态栏组件
        self.create_widgets()
    
    def create_widgets(self):
        """创建状态栏组件"""
        # 左侧状态信息
        self.status_label = ttk.Label(self, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 中间进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self, 
            variable=self.progress_var, 
            maximum=100,
            length=200
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5)
        
        # 右侧统计信息
        self.stats_label = ttk.Label(self, text="成功: 0 | 失败: 0", anchor=tk.E)
        self.stats_label.pack(side=tk.RIGHT, fill=tk.X, padx=5)
    
    def update_status(self, status, progress=None, success=0, failed=0):
        """更新状态栏信息"""
        self.status_label.config(text=status)
        
        if progress is not None:
            self.progress_var.set(progress)
        
        self.stats_label.config(text=f"成功: {success} | 失败: {failed}")

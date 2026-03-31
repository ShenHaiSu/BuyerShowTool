"""主窗口类"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import threading
import queue
import time

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from gui.ui.task_manager import TaskManager
from gui.ui.config_manager import ConfigManager
from gui.ui.logger import LoggerRedirector
from gui.ui.components.notebook import Notebook
from gui.ui.components.status_bar import StatusBar


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        self.root = root
        self.task_manager = None
        self.is_running = False
        self.target_dir = ""
        self.log_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(self)
        
        # 创建UI组件
        self.create_widgets()
        
        # 初始化日志重定向
        self.logger_redirector = LoggerRedirector(self.log_queue)
        
        # 启动日志更新定时器
        self.root.after(100, self.update_log)
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建UI组件"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主工作区（Notebook）
        self.create_notebook()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开配置文件", command=self.open_config_file)
        file_menu.add_command(label="打开日志目录", command=self.open_log_directory)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="使用指南", command=self.show_guide)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 选择目录按钮
        self.select_dir_btn = ttk.Button(
            toolbar_frame, 
            text="选择目录", 
            command=self.on_select_directory
        )
        self.select_dir_btn.pack(side=tk.LEFT, padx=5)
        
        # 开始生成按钮
        self.start_btn = ttk.Button(
            toolbar_frame, 
            text="开始生成", 
            command=self.on_start_generation
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_btn = ttk.Button(
            toolbar_frame, 
            text="停止", 
            command=self.on_stop_generation,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
    
    def create_notebook(self):
        """创建主工作区（Notebook）"""
        notebook_frame = ttk.Frame(self.root)
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 配置页面
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="配置页面")
        self.create_config_tab()
        
        # 任务页面
        self.task_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.task_frame, text="任务页面")
        self.create_task_tab()
    
    def create_config_tab(self):
        """创建配置页面"""
        # API 配置区域
        api_frame = ttk.LabelFrame(self.config_frame, text="API 配置")
        api_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # DeepSeek API Key
        ttk.Label(api_frame, text="DeepSeek API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.deepseek_key_entry = ttk.Entry(api_frame, show="*", width=50)
        self.deepseek_key_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 通义万相 API Key
        ttk.Label(api_frame, text="通义万相 API Key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.tongyi_key_entry = ttk.Entry(api_frame, show="*", width=50)
        self.tongyi_key_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 保存配置按钮
        self.save_config_btn = ttk.Button(
            api_frame, 
            text="保存配置", 
            command=self.config_manager.save_config
        )
        self.save_config_btn.grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)
        
        # 生成参数区域
        params_frame = ttk.LabelFrame(self.config_frame, text="生成参数")
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 好评文案生成数量
        ttk.Label(params_frame, text="好评文案生成数量:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.review_count_var = tk.IntVar(value=3)
        self.review_count_spin = ttk.Spinbox(
            params_frame, 
            from_=1, 
            to=10, 
            textvariable=self.review_count_var,
            width=10
        )
        self.review_count_spin.grid(row=0, column=1, padx=5, pady=5)
        
        # 买家秀图片生成数量
        ttk.Label(params_frame, text="买家秀图片生成数量:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.image_count_var = tk.IntVar(value=3)
        self.image_count_spin = ttk.Spinbox(
            params_frame, 
            from_=1, 
            to=10, 
            textvariable=self.image_count_var,
            width=10
        )
        self.image_count_spin.grid(row=1, column=1, padx=5, pady=5)
        
        # 目标目录显示
        dir_frame = ttk.LabelFrame(self.config_frame, text="目标目录")
        dir_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.dir_label = ttk.Label(dir_frame, text="未选择目录", foreground="gray")
        self.dir_label.pack(fill=tk.X, padx=5, pady=5)
    
    def create_task_tab(self):
        """创建任务页面"""
        # 任务列表
        tree_frame = ttk.Frame(self.task_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Treeview
        columns = ("序号", "目录路径", "状态", "进度", "耗时")
        self.task_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="headings",
            height=10
        )
        
        # 设置列标题
        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 日志输出区域
        log_frame = ttk.LabelFrame(self.task_frame, text="日志输出")
        log_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5, ipady=5)
        
        self.log_text = tk.Text(
            log_frame, 
            height=10, 
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滚动条
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def on_select_directory(self):
        """处理目录选择逻辑"""
        directory = filedialog.askdirectory(
            title="选择目标根目录",
            initialdir=os.path.expanduser("~")
        )
        
        if directory:
            self.target_dir = directory
            self.dir_label.config(text=directory, foreground="black")
            
            # 扫描目录并更新任务列表
            self.scan_directory()
    
    def scan_directory(self):
        """扫描目录并更新任务列表"""
        if not self.target_dir:
            return
        
        # 清空任务列表
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # 使用TaskManager扫描目录
        if self.task_manager is None:
            self.task_manager = TaskManager(self)
        
        # 在后台线程中扫描目录
        scan_thread = threading.Thread(
            target=self.task_manager.scan_directory,
            args=(self.target_dir,),
            daemon=True
        )
        scan_thread.start()
    
    def on_start_generation(self):
        """启动任务生成流程"""
        if not self.target_dir:
            messagebox.showerror("错误", "请先选择目标目录")
            return
        
        # 检查配置
        if not self.config_manager.validate_config():
            messagebox.showerror("错误", "请先配置API密钥")
            return
        
        # 更新UI状态
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.select_dir_btn.config(state=tk.DISABLED)
        
        # 更新配置
        self.config_manager.save_config()
        
        # 创建任务管理器
        if self.task_manager is None:
            self.task_manager = TaskManager(self)
        
        # 启动任务处理
        process_thread = threading.Thread(
            target=self.task_manager.run_tasks,
            args=(self.target_dir,),
            daemon=True
        )
        process_thread.start()
    
    def on_stop_generation(self):
        """停止任务生成流程"""
        self.is_running = False
        if self.task_manager:
            self.task_manager.stop()
        
        # 更新UI状态
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.select_dir_btn.config(state=tk.NORMAL)
        
        self.status_bar.update_status("已停止")
    
    def update_log(self):
        """更新日志显示"""
        try:
            while True:
                log_message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, log_message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        
        # 继续定时更新
        self.root.after(100, self.update_log)
    
    def update_task_list(self, task_data):
        """更新任务列表"""
        # 清空现有任务
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # 添加新任务
        for i, task in enumerate(task_data, 1):
            self.task_tree.insert(
                "", 
                tk.END, 
                values=(
                    i, 
                    task.get("path", ""), 
                    task.get("status", "待处理"),
                    task.get("progress", "0%"),
                    task.get("time", "")
                )
            )
    
    def update_status_bar(self, status, progress=None, success=0, failed=0):
        """更新状态栏"""
        self.status_bar.update_status(status, progress, success, failed)
    
    def open_config_file(self):
        """打开配置文件"""
        config_path = os.path.join(project_root, "config.yaml")
        if os.path.exists(config_path):
            os.startfile(config_path)
        else:
            messagebox.showinfo("提示", "配置文件不存在，请先运行程序生成配置文件")
    
    def open_log_directory(self):
        """打开日志目录"""
        os.startfile(project_root)
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于",
            "BuyerShowTool - 买家秀生成工具\n版本: 1.0.0\n作者: BuyerShowTool Team"
        )
    
    def show_guide(self):
        """显示使用指南"""
        guide_path = os.path.join(project_root, "README.md")
        if os.path.exists(guide_path):
            os.startfile(guide_path)
        else:
            messagebox.showinfo("提示", "使用指南文档不存在")
    
    def on_closing(self):
        """窗口关闭事件处理"""
        if self.is_running:
            if messagebox.askyesno("确认", "任务正在运行中，确定要退出吗？"):
                self.on_stop_generation()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def restore_ui_state(self):
        """恢复UI状态"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.select_dir_btn.config(state=tk.NORMAL)

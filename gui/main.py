"""BuyerShowTool GUI 入口文件"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from gui.ui.main_window import MainWindow


def main():
    """主入口函数"""
    root = tk.Tk()
    root.title("BuyerShowTool - 买家秀生成工具")
    root.geometry("1000x700")
    
    # 设置 Windows 图标 (可选)
    # root.iconbitmap("assets/icon.ico")
    
    # 设置 ttk 主题
    style = ttk.Style()
    style.theme_use('vista')
    
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()

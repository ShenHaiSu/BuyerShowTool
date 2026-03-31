"""自定义Notebook组件"""
import tkinter as tk
from tkinter import ttk


class Notebook(ttk.Notebook):
    """自定义Notebook组件"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
    
    def add_tab(self, tab_frame, text):
        """添加标签页"""
        self.add(tab_frame, text=text)

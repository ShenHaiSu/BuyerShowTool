"""进度追踪工具模块"""
import sys
import time
from typing import Optional


class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self, total_reviews: int = 0, total_images: int = 0):
        self.total_reviews = total_reviews
        self.total_images = total_images
        self.completed_reviews = 0
        self.completed_images = 0
        self.start_time = time.time()
    
    def update_review_progress(self, current: int, total: int = None):
        """更新好评文案进度"""
        if total is not None:
            self.total_reviews = total
        self.completed_reviews = current
        self._print_progress()
    
    def update_image_progress(self, current: int, total: int = None):
        """更新买家秀图片进度"""
        if total is not None:
            self.total_images = total
        self.completed_images = current
        self._print_progress()
    
    def _print_progress(self):
        """打印进度信息"""
        # 计算总进度
        total_items = self.total_reviews + self.total_images
        completed_items = self.completed_reviews + self.completed_images
        
        # 计算百分比
        if total_items > 0:
            percent = int((completed_items / total_items) * 100)
        else:
            percent = 0
        
        # 构建进度条
        bar_length = 30
        filled = int((completed_items / total_items) * bar_length) if total_items > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # 计算耗时
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)
        
        # 预估剩余时间
        if completed_items > 0:
            avg_time = elapsed / completed_items
            remaining = (total_items - completed_items) * avg_time
            remaining_str = self._format_time(remaining)
        else:
            remaining_str = "计算中..."
        
        # 打印进度
        print("\r" + " " * 80, end="")  # 清除上一行
        print(f"\r📊 进度: [{bar}] {percent}% | 好评文案: {self.completed_reviews}/{self.total_reviews} | 买家秀: {self.completed_images}/{self.total_images} | 耗时: {elapsed_str} | 预计剩余: {remaining_str}", end="")
        sys.stdout.flush()
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}小时{minutes}分"
    
    def finish(self):
        """完成进度追踪"""
        self._print_progress()
        print()  # 换行
    
    def print_summary(self):
        """打印汇总信息"""
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)
        
        total_items = self.total_reviews + self.total_images
        completed_items = self.completed_reviews + self.completed_images
        
        print("\n" + "=" * 50)
        print("📋 生成汇总")
        print("=" * 50)
        print(f"✅ 好评文案: {self.completed_reviews}/{self.total_reviews}")
        print(f"✅ 买家秀图片: {self.completed_images}/{self.total_images}")
        print(f"📦 总计: {completed_items}/{total_items}")
        print(f"⏱️ 总耗时: {elapsed_str}")
        print("=" * 50)


def print_header(title: str, width: int = 50):
    """打印带装饰的标题"""
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_step(step: str, current: int, total: int, item_type: str = "任务"):
    """打印步骤进度"""
    percent = int((current / total) * 100) if total > 0 else 0
    print(f"  🔄 {step}: {current}/{total} ({percent}%) {item_type}")


def print_success(message: str):
    """打印成功信息"""
    print(f"  ✅ {message}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"  ⚠️ {message}")


def print_error(message: str):
    """打印错误信息"""
    print(f"  ❌ {message}")
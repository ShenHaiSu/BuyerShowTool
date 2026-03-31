"""错误处理模块"""
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class ErrorRecord:
    """错误记录数据类"""
    timestamp: str
    target_path: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, project_root: str):
        """
        初始化错误处理器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.errors: List[ErrorRecord] = []
    
    def record_error(
        self, 
        target_path: str, 
        error_type: str, 
        error_message: str, 
        stack_trace: Optional[str] = None
    ):
        """
        记录一个错误
        
        Args:
            target_path: 目标路径
            error_type: 错误类型
            error_message: 错误消息
            stack_trace: 堆栈跟踪（可选）
        """
        error_record = ErrorRecord(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            target_path=target_path,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace
        )
        self.errors.append(error_record)
    
    def save_detail_error(self, target_path: str):
        """
        保存当前目标路径的错误详情到目标目录
        
        Args:
            target_path: 目标路径
        """
        # 筛选当前目标路径的错误
        target_errors = [e for e in self.errors if e.target_path == target_path]
        if not target_errors:
            return
        
        # 生成错误报告内容
        content = self._format_error_report(target_errors)
        
        # 写入目标目录
        error_file = os.path.join(target_path, "error_detail.log")
        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"写入错误详情文件失败: {error_file}, 错误: {e}")
    
    def save_summary_error(self):
        """
        保存所有错误的汇总报告到项目根目录
        """
        if not self.errors:
            return
        
        content = self._format_error_report(self.errors)
        
        # 写入项目根目录
        error_file = os.path.join(self.project_root, "run_error_summary.log")
        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"写入错误汇总文件失败: {error_file}, 错误: {e}")
    
    def _format_error_report(self, errors: List[ErrorRecord]) -> str:
        """
        格式化错误报告
        
        Args:
            errors: 错误记录列表
        
        Returns:
            str: 格式化的错误报告
        """
        lines = [
            "=" * 60,
            "错误报告",
            "=" * 60,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"错误总数: {len(errors)}",
            "=" * 60,
            ""
        ]
        
        for i, error in enumerate(errors, 1):
            lines.extend([
                f"--- 错误 #{i} ---",
                f"时间: {error.timestamp}",
                f"目标路径: {error.target_path}",
                f"错误类型: {error.error_type}",
                f"错误消息: {error.error_message}",
            ])
            if error.stack_trace:
                lines.extend([
                    "堆栈跟踪:",
                    error.stack_trace
                ])
            lines.append("")
        
        return "\n".join(lines)
    
    def has_errors(self) -> bool:
        """检查是否有错误记录"""
        return len(self.errors) > 0
    
    def get_error_count(self) -> int:
        """获取错误总数"""
        return len(self.errors)
    
    def get_errors_by_path(self, target_path: str) -> List[ErrorRecord]:
        """
        获取指定路径的错误记录
        
        Args:
            target_path: 目标路径
        
        Returns:
            List[ErrorRecord]: 错误记录列表
        """
        return [e for e in self.errors if e.target_path == target_path]
"""日志重定向"""
import sys
import queue


class LoggerRedirector:
    """日志重定向器"""
    
    def __init__(self, log_queue):
        self.log_queue = log_queue
        
        # 保存原始的 stdout 和 stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # 重定向 stdout 和 stderr
        sys.stdout = self
        sys.stderr = self
    
    def write(self, text):
        """写入日志到队列"""
        if text.strip():  # 忽略空行
            self.log_queue.put(text)
    
    def flush(self):
        """刷新缓冲区"""
        pass
    
    def restore(self):
        """恢复原始的 stdout 和 stderr"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

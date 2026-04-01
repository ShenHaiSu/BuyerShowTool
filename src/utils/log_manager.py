"""日志管理器模块"""
import os
import json
import threading
from datetime import datetime
from collections import defaultdict
from typing import List, Dict


class LogManager:
    """日志管理器 - 负责日志的内存缓存和持久化"""
    
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = log_dir
        self._ensure_log_dir()
        self.lock = threading.Lock()
        self.task_logs: Dict[str, List[str]] = defaultdict(list)
        self.subscribers: Dict[str, list] = defaultdict(list)
    
    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def get_log_callback(self, task_id: str):
        """获取日志回调函数"""
        def callback(log_entry: str):
            self.append_log(task_id, log_entry)
        return callback
    
    def append_log(self, task_id: str, log_entry: str):
        """追加日志"""
        with self.lock:
            self.task_logs[task_id].append(log_entry)
    
    def get_logs(self, task_id: str):
        """获取任务的所有日志（用于 SSE）"""
        # 返回一个生成器，持续监听新日志
        seen_count = 0
        while True:
            with self.lock:
                logs = self.task_logs[task_id]
                while seen_count < len(logs):
                    yield logs[seen_count]
                    seen_count += 1
            
            import time
            time.sleep(0.1)
    
    def persist_log(self, task_id: str, target_dir: str):
        """持久化日志到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.log_dir, f'run_{timestamp}_{task_id}.log')
        
        with self.lock:
            logs = self.task_logs.get(task_id, [])
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"任务ID: {task_id}\n")
            f.write(f"目标目录: {target_dir}\n")
            f.write(f"开始时间: {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
            
            for log_entry in logs:
                try:
                    data = json.loads(log_entry)
                    log_type = data.get('type', 'info')
                    message = data.get('message', '')
                    timestamp = data.get('timestamp', '')
                    f.write(f"[{timestamp}] [{log_type.upper()}] {message}\n")
                except:
                    f.write(f"{log_entry}\n")
        
        return log_file
    
    def get_history(self) -> List[Dict]:
        """获取历史运行记录"""
        history = []
        
        if os.path.exists(self.log_dir):
            for filename in os.listdir(self.log_dir):
                if filename.startswith('run_') and filename.endswith('.log'):
                    filepath = os.path.join(self.log_dir, filename)
                    stat = os.stat(filepath)
                    history.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        
        # 按修改时间倒序
        history.sort(key=lambda x: x['modified'], reverse=True)
        return history[:50]  # 返回最近50条
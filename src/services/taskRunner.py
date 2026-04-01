"""任务运行器模块"""
import os
import sys
import json
import uuid
import traceback
import threading
from datetime import datetime
from typing import Dict, Callable, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.loader import load_all_config, check_and_generate_config
from src.services.reviewGenerator import ReviewGenerator
from src.services.imageGenerator import ImageGenerator
from src.utils.error_handler import ErrorHandler
from src.utils.log_manager import LogManager


class TaskRunner:
    """任务运行器"""
    
    def __init__(self):
        self.tasks: Dict[str, dict] = {}
        self.log_manager = LogManager()
    
    def create_task(self, target_dir: str) -> str:
        """创建并启动任务"""
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
        
        self.tasks[task_id] = {
            'id': task_id,
            'targetDir': target_dir,
            'status': 'pending',
            'progress': {
                'reviewProgress': 0,
                'reviewTotal': 0,
                'imageProgress': 0,
                'imageTotal': 0
            }
        }
        
        # 在新线程中运行任务
        thread = threading.Thread(target=self._run_task, args=(task_id, target_dir))
        thread.daemon = True
        thread.start()
        
        return task_id
    
    def _run_task(self, task_id: str, target_dir: str):
        """在新线程中运行任务"""
        task = self.tasks[task_id]
        task['status'] = 'running'
        
        # 获取任务的日志回调
        log_callback = self.log_manager.get_log_callback(task_id)
        
        try:
            # 检查配置
            if not check_and_generate_config():
                self._emit_log(task_id, 'error', '配置文件不存在，请先配置 API 密钥')
                self._emit_complete(task_id, False, '配置文件不存在，请先配置 API 密钥')
                task['status'] = 'failed'
                return
            
            # 加载配置
            config, goods_data = load_all_config(target_dir)
            
            self._emit_log(task_id, 'info', f'商品名称: {goods_data.goods.name}')
            self._emit_log(task_id, 'info', f'商品图片: {len(goods_data.images)} 张')
            
            # 生成好评文案
            self._emit_log(task_id, 'info', '开始生成好评文案...')
            review_generator = ReviewGenerator(config)
            reviews = review_generator.generate_reviews(goods_data, target_dir)
            
            if reviews:
                self._emit_log(task_id, 'success', f'好评文案生成完成: {len(reviews)} 条')
            else:
                self._emit_log(task_id, 'warning', '未能生成好评文案')
            
            # 生成买家秀图片
            self._emit_log(task_id, 'info', '开始生成买家秀图片...')
            image_generator = ImageGenerator(config)
            image_paths = image_generator.generate_buyer_show_images(goods_data, target_dir)
            
            if image_paths:
                self._emit_log(task_id, 'success', f'买家秀图片生成完成: {len(image_paths)} 张')
            else:
                self._emit_log(task_id, 'warning', '未能生成买家秀图片')
            
            task['status'] = 'completed'
            self._emit_complete(task_id, True, '任务完成')
            
            # 持久化日志
            self.log_manager.persist_log(task_id, target_dir)
            
        except Exception as e:
            task['status'] = 'failed'
            self._emit_log(task_id, 'error', f'任务执行失败: {str(e)}')
            self._emit_complete(task_id, False, str(e))
            # 持久化日志
            self.log_manager.persist_log(task_id, target_dir)
    
    def _emit_log(self, task_id: str, log_type: str, message: str):
        """发送日志到前端"""
        log_entry = json.dumps({
            'type': log_type,
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # 通过 log_manager 推送到 SSE
        self.log_manager.append_log(task_id, log_entry)
    
    def _emit_complete(self, task_id: str, success: bool, message: str):
        """发送完成事件"""
        log_entry = json.dumps({
            'type': 'complete',
            'success': success,
            'message': message
        })
        self.log_manager.append_log(task_id, log_entry)
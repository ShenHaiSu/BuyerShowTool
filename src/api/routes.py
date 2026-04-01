"""API 路由模块"""
import os
import yaml
import json
import uuid
import threading
from datetime import datetime
from typing import Dict, List

from flask import Blueprint, request, jsonify, Response


api_bp = Blueprint('api', __name__)

# 任务运行器实例（延迟导入避免循环依赖）
_task_runner = None
_log_manager = None


def get_task_runner():
    """获取任务运行器实例"""
    global _task_runner
    if _task_runner is None:
        from src.services.taskRunner import TaskRunner
        _task_runner = TaskRunner()
    return _task_runner


def get_log_manager():
    """获取日志管理器实例"""
    global _log_manager
    if _log_manager is None:
        from src.utils.log_manager import LogManager
        _log_manager = LogManager()
    return _log_manager


def check_config_exists() -> bool:
    """检查配置文件是否存在"""
    return os.path.exists('config.yaml')


def load_config_from_file() -> dict:
    """从 config.yaml 读取配置"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
    if not os.path.exists(config_path):
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data


def save_config_to_file(config_data: dict) -> bool:
    """保存配置到 config.yaml"""
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
    config_path = os.path.join(config_dir, 'config.yaml')
    try:
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })


@api_bp.route('/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        config_exists = check_config_exists()
        
        if not config_exists:
            # 配置文件不存在，返回空配置提示前端需要配置
            return jsonify({
                'config': None,
                'configured': False,
                'message': '配置文件不存在，请先配置 API 密钥'
            })
        
        # 读取配置文件
        config_data = load_config_from_file()
        
        if not config_data:
            return jsonify({
                'config': None,
                'configured': False,
                'message': '配置文件为空，请先配置 API 密钥'
            })
        
        # 返回配置信息给前端（隐藏 apiKey 敏感信息）
        return jsonify({
            'config': {
                'deepseek': {
                    'url': config_data.get('deepseek', {}).get('url', ''),
                    'apiKey': mask_api_key(config_data.get('deepseek', {}).get('apiKey', '')),
                    'model': config_data.get('deepseek', {}).get('model', ''),
                    'reviewCount': config_data.get('deepseek', {}).get('reviewCount', 4)
                },
                'tongyi': {
                    'apiKey': mask_api_key(config_data.get('tongyi', {}).get('apiKey', '')),
                    'model': config_data.get('tongyi', {}).get('model', ''),
                    'imageCount': config_data.get('tongyi', {}).get('imageCount', 4)
                }
            },
            'configured': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'configured': False,
            'message': f'读取配置失败: {str(e)}'
        }), 500


@api_bp.route('/config', methods=['POST'])
def save_config():
    """保存配置到 config.yaml"""
    try:
        config_data = request.get_json()
        
        if not config_data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        # 验证必要字段
        if 'deepseek' not in config_data or 'tongyi' not in config_data:
            return jsonify({'error': '配置数据缺少必要字段'}), 400
        
        deepseek = config_data['deepseek']
        tongyi = config_data['tongyi']
        
        # 验证 DeepSeek 配置
        required_deepseek = ['url', 'apiKey', 'model', 'reviewCount']
        for field in required_deepseek:
            if field not in deepseek:
                return jsonify({'error': f'DeepSeek 配置缺少字段: {field}'}), 400
        
        # 验证通义配置
        required_tongyi = ['apiKey', 'model', 'imageCount']
        for field in required_tongyi:
            if field not in tongyi:
                return jsonify({'error': f'通义配置缺少字段: {field}'}), 400
        
        # 保存配置
        if save_config_to_file(config_data):
            return jsonify({
                'success': True,
                'message': '配置保存成功'
            })
        else:
            return jsonify({'error': '配置保存失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def mask_api_key(api_key: str) -> str:
    """掩码 API 密钥，只显示前4位和后4位"""
    if not api_key or len(api_key) <= 8:
        return '****'
    return api_key[:4] + '****' + api_key[-4:]


@api_bp.route('/run', methods=['POST'])
def run_task():
    """启动任务"""
    data = request.get_json()
    target_dir = data.get('targetDir')
    
    if not target_dir:
        return jsonify({'error': 'targetDir is required'}), 400
    
    # 创建任务
    task_runner = get_task_runner()
    task_id = task_runner.create_task(target_dir)
    
    return jsonify({
        'taskId': task_id,
        'status': 'started'
    })


@api_bp.route('/logs/<task_id>', methods=['GET'])
def get_logs(task_id):
    """SSE 日志流"""
    log_manager = get_log_manager()
    
    def generate():
        for log in log_manager.get_logs(task_id):
            yield f"event: log\ndata: {log}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )


@api_bp.route('/history', methods=['GET'])
def get_history():
    """获取历史运行记录"""
    log_manager = get_log_manager()
    runs = log_manager.get_history()
    return jsonify({'runs': runs})
# BuyerShowTool 前后端分离重构开发计划

## 文档概述

本文档为 BuyerShowTool Python 项目的重构开发计划，目标是将其从命令行工具重构为前后端分离的 Web 应用。

### 重构目标

- 将当前命令行工具重构为 **后端 API 服务**
- 编写 **HTML + CSS + JavaScript** 前端界面
- 用户可通过 **URL 访问前端页面**进行交互
- 点击运行后，后端将**实时运行日志**发送到前端展示
- 所有运行日志在**项目根目录进行持久化**

---

## 一、技术方案选型

### 1.1 后端技术选型

| 技术栈 | 选择 | 说明 |
|--------|------|------|
| Web 框架 | **Flask** | 轻量级、简单易用、适合小型项目 |
| 实时通信 | **SSE (Server-Sent Events)** | 简单可靠的单向实时通信，无需 WebSocket |
| 日志持久化 | 文件系统 | 在项目根目录 `logs/` 下按日期存储 |
| 任务队列 | 线程/异步 | 使用 Python `threading` 或 `concurrent.futures` |

**推荐理由**：
- Flask 足够轻量，适合本项目的简单 API 需求
- SSE 比 WebSocket 更简单，适合后端→前端单向推送场景
- 无需额外的消息队列依赖，降低部署复杂度

### 1.2 前端技术选型

| 技术栈 | 选择 | 说明 |
|--------|------|------|
| HTML | HTML5 | 语义化标签 |
| CSS | 原生 CSS | 简单样式，使用 Flexbox/Grid 布局 |
| JavaScript | 原生 ES6+ | 无需框架，保持简单 |
| 实时通信 | EventSource API | 配合 SSE 使用 |

### 1.3 项目依赖

```
flask>=2.3.0
flask-cors>=4.0.0
```

---

## 二、目录结构重构

### 2.1 重构后目录结构

```
BuyerShowTool/
├── src/                          # Python 后端源码
│   ├── __init__.py
│   ├── api/                      # API 模块
│   │   ├── __init__.py
│   │   ├── routes.py             # API 路由定义 (新增)
│   │   └── sse.py                # SSE 实时推送模块 (新增)
│   ├── config/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── types.py
│   │   └── guide.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── goodsParser.py
│   │   ├── reviewGenerator.py
│   │   ├── imageGenerator.py
│   │   └── taskRunner.py         # 任务运行器 (重构)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── file.py
│   │   ├── error_handler.py
│   │   ├── progress.py
│   │   └── log_manager.py        # 日志管理器 (新增)
│   └── app.py                   # Flask 应用入口 (新增)
├── static/                       # 前端静态文件
│   ├── index.html               # 主页面
│   ├── css/
│   │   └── style.css            # 样式文件
│   └── js/
│       └── app.js               # 前端逻辑
├── templates/                     # HTML 模板 (可选)
│   └── index.html
├── logs/                         # 日志持久化目录 (新增)
│   └── run_YYYYMMDD_HHMMSS.log
├── plans/                        # 开发计划文档
│   └── BuyerShowTool_Web_Restructuring.md
├── config.yaml                   # 项目配置文件
├── config.example.yaml
├── requirements.txt
└── README.md
```

### 2.2 关键变更说明

| 变更类型 | 路径 | 说明 |
|----------|------|------|
| 新增 | `src/app.py` | Flask 应用主入口 |
| 新增 | `src/api/routes.py` | API 路由定义 |
| 新增 | `src/api/sse.py` | SSE 实时推送模块 |
| 新增 | `src/utils/log_manager.py` | 日志管理器 |
| 新增 | `static/` | 前端静态资源目录 |
| 新增 | `logs/` | 日志持久化目录 |
| 重构 | `src/services/taskRunner.py` | 从 index.py 重构出任务运行器 |

---

## 三、API 设计

### 3.1 API 端点列表

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | `/api/health` | 健康检查 | - | `{status: "ok"}` |
| GET | `/api/config` | 获取当前配置 | - | `{config: {...}}` |
| POST | `/api/run` | 启动任务 | `{targetDir: string}` | `{taskId: string, status: "started"}` |
| GET | `/api/status/{taskId}` | 获取任务状态 | - | `{status: string, progress: {...}}` |
| GET | `/api/logs/{taskId}` | SSE 端点，实时推送日志 | - | SSE stream |
| GET | `/api/history` | 获取历史运行记录 | - | `{runs: [...]}` |

### 3.2 API 详细设计

#### 3.2.1 健康检查

```
GET /api/health
```

**响应示例**：
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 3.2.2 获取配置

```
GET /api/config
```

**响应示例**：
```json
{
  "config": {
    "deepseek": {
      "url": "https://api.deepseek.com/v1/chat/completions",
      "model": "deepseek-chat",
      "reviewCount": 4
    },
    "tongyi": {
      "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/generation",
      "model": "wanx-v1",
      "imageCount": 4
    }
  }
}
```

#### 3.2.3 启动任务

```
POST /api/run
Content-Type: application/json

{
  "targetDir": "C:\\example\\dir"
}
```

**响应示例**：
```json
{
  "taskId": "20240101_120000_abc123",
  "status": "started"
}
```

#### 3.2.4 SSE 日志推送

```
GET /api/logs/{taskId}
```

**SSE 事件格式**：
```
event: log
data: {"type": "info", "message": "正在加载配置...", "timestamp": "12:00:00"}

event: log
data: {"type": "success", "message": "好评文案生成完成", "timestamp": "12:00:05"}

event: progress
data: {"reviewProgress": 2, "reviewTotal": 4, "imageProgress": 0, "imageTotal": 4}

event: complete
data: {"success": true, "message": "任务完成"}
```

---

## 四、后端模块设计

### 4.1 Flask 应用入口 (src/app.py)

```python
"""Flask 应用入口"""
from flask import Flask
from flask_cors import CORS
from src.api.routes import api_bp

def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__, static_folder='../static', static_url_path='')
    
    # 启用 CORS
    CORS(app)
    
    # 注册 API 蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 根路径返回前端页面
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 4.2 API 路由 (src/api/routes.py)

```python
"""API 路由模块"""
from flask import Blueprint, request, jsonify, Response
from src.services.taskRunner import TaskRunner
from src.utils.log_manager import LogManager
from src.config.loader import load_config

api_bp = Blueprint('api', __name__)

# 任务运行器实例
task_runner = TaskRunner()
log_manager = LogManager()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    from datetime import datetime
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        config = load_config()
        return jsonify({
            'config': {
                'deepseek': {
                    'url': config.deepseek.url,
                    'model': config.deepseek.model,
                    'reviewCount': config.deepseek.reviewCount
                },
                'tongyi': {
                    'url': config.tongyi.url,
                    'model': config.tongyi.model,
                    'imageCount': config.tongyi.imageCount
                }
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/run', methods=['POST'])
def run_task():
    """启动任务"""
    data = request.get_json()
    target_dir = data.get('targetDir')
    
    if not target_dir:
        return jsonify({'error': 'targetDir is required'}), 400
    
    # 创建任务
    task_id = task_runner.create_task(target_dir)
    
    return jsonify({
        'taskId': task_id,
        'status': 'started'
    })

@api_bp.route('/logs/<task_id>', methods=['GET'])
def get_logs(task_id):
    """SSE 日志流"""
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
    runs = log_manager.get_history()
    return jsonify({'runs': runs})
```

### 4.3 任务运行器 (src/services/taskRunner.py)

```python
"""任务运行器模块"""
import os
import sys
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
                self._emit_log(task_id, 'error', '配置文件不存在，请先配置 config.yaml')
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
            
        except Exception as e:
            task['status'] = 'failed'
            self._emit_log(task_id, 'error', f'任务执行失败: {str(e)}')
            self._emit_complete(task_id, False, str(e))
    
    def _emit_log(self, task_id: str, log_type: str, message: str):
        """发送日志到前端"""
        import json
        log_entry = json.dumps({
            'type': log_type,
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        # 通过 log_manager 推送到 SSE
        self.log_manager.append_log(task_id, log_entry)
    
    def _emit_complete(self, task_id: str, success: bool, message: str):
        """发送完成事件"""
        import json
        log_entry = json.dumps({
            'type': 'complete',
            'success': success,
            'message': message
        })
        self.log_manager.append_log(task_id, log_entry)
```

### 4.4 日志管理器 (src/utils/log_manager.py)

```python
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
```

---

## 五、前端页面设计

### 5.1 HTML 结构 (static/index.html)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuyerShowTool - 买家秀生成工具</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🛒 BuyerShowTool</h1>
            <p class="subtitle">买家秀生成工具 - 自动化好评文案与买家秀图片生成</p>
        </header>
        
        <main>
            <!-- 配置区域 -->
            <section class="config-section">
                <h2>📁 配置</h2>
                <div class="form-group">
                    <label for="targetDir">目标目录</label>
                    <input type="text" id="targetDir" placeholder="请输入商品配置目录路径">
                    <button id="browseBtn" type="button">浏览...</button>
                </div>
                <div class="config-info">
                    <p>好评文案数量: <span id="reviewCount">4</span> 条</p>
                    <p>买家秀图片数量: <span id="imageCount">4</span> 张</p>
                </div>
            </section>
            
            <!-- 操作区域 -->
            <section class="action-section">
                <button id="runBtn" class="btn-primary">
                    🚀 开始生成
                </button>
                <button id="stopBtn" class="btn-danger" disabled>
                    ⏹️ 停止
                </button>
            </section>
            
            <!-- 日志区域 -->
            <section class="log-section">
                <div class="log-header">
                    <h2>📋 运行日志</h2>
                    <button id="clearLogBtn" type="button">清空</button>
                </div>
                <div id="logContainer" class="log-container">
                    <div class="log-placeholder">点击"开始生成"后，日志将显示在这里...</div>
                </div>
            </section>
        </main>
        
        <footer>
            <p>BuyerShowTool v1.0 | 基于 DeepSeek & 通义万相 API</p>
        </footer>
    </div>
    
    <script src="js/app.js"></script>
</body>
</html>
```

### 5.2 CSS 样式 (static/css/style.css)

```css
/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    overflow: hidden;
}

/* 头部 */
header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    text-align: center;
}

header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
}

.subtitle {
    opacity: 0.9;
    font-size: 0.95rem;
}

/* 主内容 */
main {
    padding: 30px;
}

/* 配置区域 */
.config-section {
    margin-bottom: 30px;
}

.config-section h2 {
    font-size: 1.2rem;
    margin-bottom: 15px;
    color: #333;
}

.form-group {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.form-group label {
    width: 80px;
    line-height: 40px;
    font-weight: 500;
}

.form-group input {
    flex: 1;
    padding: 10px 15px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s;
}

.form-group input:focus {
    outline: none;
    border-color: #667eea;
}

.form-group button {
    padding: 10px 20px;
    background: #f5f5f5;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s;
}

.form-group button:hover {
    background: #e0e0e0;
}

.config-info {
    display: flex;
    gap: 30px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.config-info p {
    color: #666;
}

.config-info span {
    font-weight: 600;
    color: #667eea;
}

/* 操作区域 */
.action-section {
    display: flex;
    gap: 15px;
    margin-bottom: 30px;
}

.btn-primary, .btn-danger {
    flex: 1;
    padding: 15px;
    border: none;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-danger {
    background: #dc3545;
    color: white;
}

.btn-danger:hover:not(:disabled) {
    background: #c82333;
}

.btn-danger:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* 日志区域 */
.log-section {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    overflow: hidden;
}

.log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background: #f8f9fa;
    border-bottom: 1px solid #e0e0e0;
}

.log-header h2 {
    font-size: 1.1rem;
    color: #333;
}

.log-header button {
    padding: 5px 15px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
}

.log-header button:hover {
    background: #f0f0f0;
}

.log-container {
    height: 400px;
    overflow-y: auto;
    padding: 15px;
    background: #1e1e1e;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9rem;
}

.log-placeholder {
    color: #888;
    text-align: center;
    padding-top: 100px;
}

.log-entry {
    margin-bottom: 8px;
    line-height: 1.5;
}

.log-entry.info { color: #fff; }
.log-entry.success { color: #4caf50; }
.log-entry.warning { color: #ff9800; }
.log-entry.error { color: #f44336; }
.log-entry .timestamp {
    color: #888;
    margin-right: 10px;
}
.log-entry .type {
    font-weight: 600;
    margin-right: 10px;
}

/* 页脚 */
footer {
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    color: #666;
    font-size: 0.85rem;
}

/* 响应式 */
@media (max-width: 600px) {
    .form-group {
        flex-direction: column;
    }
    .form-group label {
        width: 100%;
    }
    .config-info {
        flex-direction: column;
        gap: 10px;
    }
}
```

### 5.3 JavaScript 逻辑 (static/js/app.js)

```javascript
/**
 * BuyerShowTool 前端逻辑
 */

class BuyerShowTool {
    constructor() {
        this.currentTaskId = null;
        this.eventSource = null;
        
        // DOM 元素
        this.targetDirInput = document.getElementById('targetDir');
        this.runBtn = document.getElementById('runBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.clearLogBtn = document.getElementById('clearLogBtn');
        this.logContainer = document.getElementById('logContainer');
        this.reviewCountSpan = document.getElementById('reviewCount');
        this.imageCountSpan = document.getElementById('imageCount');
        
        this.init();
    }
    
    init() {
        // 绑定事件
        this.runBtn.addEventListener('click', () => this.startTask());
        this.stopBtn.addEventListener('click', () => this.stopTask());
        this.clearLogBtn.addEventListener('click', () => this.clearLog());
        
        // 加载配置
        this.loadConfig();
    }
    
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.config) {
                this.reviewCountSpan.textContent = data.config.deepseek.reviewCount;
                this.imageCountSpan.textContent = data.config.tongyi.imageCount;
            }
        } catch (error) {
            console.error('加载配置失败:', error);
        }
    }
    
    async startTask() {
        const targetDir = this.targetDirInput.value.trim();
        
        if (!targetDir) {
            alert('请输入目标目录路径');
            return;
        }
        
        // 清空日志
        this.clearLog();
        this.appendLog('info', '正在启动任务...');
        
        // 禁用开始按钮
        this.runBtn.disabled = true;
        this.stopBtn.disabled = false;
        
        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ targetDir })
            });
            
            const data = await response.json();
            
            if (data.taskId) {
                this.currentTaskId = data.taskId;
                this.appendLog('info', `任务已启动，ID: ${data.taskId}`);
                this.connectSSE(data.taskId);
            } else {
                this.appendLog('error', `启动失败: ${data.error}`);
                this.resetButtons();
            }
        } catch (error) {
            this.appendLog('error', `请求失败: ${error.message}`);
            this.resetButtons();
        }
    }
    
    connectSSE(taskId) {
        // 关闭之前的连接
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // 创建 SSE 连接
        this.eventSource = new EventSource(`/api/logs/${taskId}`);
        
        this.eventSource.addEventListener('log', (event) => {
            const data = JSON.parse(event.data);
            this.appendLog(data.type, data.message);
        });
        
        this.eventSource.addEventListener('complete', (event) => {
            const data = JSON.parse(event.data);
            if (data.success) {
                this.appendLog('success', '✅ 任务完成！');
            } else {
                this.appendLog('error', `❌ 任务失败: ${data.message}`);
            }
            this.resetButtons();
            this.eventSource.close();
        });
        
        this.eventSource.onerror = (error) => {
            console.error('SSE 错误:', error);
            this.appendLog('error', '连接断开');
            this.resetButtons();
        };
    }
    
    stopTask() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        this.appendLog('warning', '任务已停止');
        this.resetButtons();
    }
    
    resetButtons() {
        this.runBtn.disabled = false;
        this.stopBtn.disabled = true;
    }
    
    appendLog(type, message) {
        // 移除 placeholder
        const placeholder = this.logContainer.querySelector('.log-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        
        const now = new Date();
        const timestamp = now.toLocaleTimeString('zh-CN', { hour12: false });
        
        const typeLabels = {
            info: 'INFO',
            success: 'SUCCESS',
            warning: 'WARNING',
            error: 'ERROR'
        };
        
        entry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="type">[${typeLabels[type] || type.toUpperCase()}]</span>
            <span class="message">${this.escapeHtml(message)}</span>
        `;
        
        this.logContainer.appendChild(entry);
        this.logContainer.scrollTop = this.logContainer.scrollHeight;
    }
    
    clearLog() {
        this.logContainer.innerHTML = '<div class="log-placeholder">点击"开始生成"后，日志将显示在这里...</div>';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new BuyerShowTool();
});
```

---

## 六、日志持久化设计

### 6.1 日志存储结构

```
logs/
├── run_20240101_120000_abc123.log
├── run_20240101_121500_def456.log
└── run_20240101_123000_ghi789.log
```

### 6.2 日志文件格式

```
任务ID: 20240101_120000_abc123
目标目录: C:\example\dir
开始时间: 2024-01-01T12:00:00
============================================================

[12:00:00] [INFO] 正在加载配置...
[12:00:01] [INFO] 商品名称: 纯棉休闲T恤
[12:00:01] [INFO] 商品图片: 4 张
[12:00:02] [INFO] 开始生成好评文案...
[12:00:05] [SUCCESS] 好评文案生成完成: 4 条
[12:00:06] [INFO] 开始生成买家秀图片...
[12:01:30] [SUCCESS] 买家秀图片生成完成: 4 张
[12:01:31] [SUCCESS] ✅ 任务完成！
```

### 6.3 日志清理策略

- 保留最近 **100 个**日志文件
- 或保留最近 **30 天**的日志（以先到为准）
- 启动时自动清理过期日志

---

## 七、部署方案

### 7.1 开发环境运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python src/app.py

# 访问 http://localhost:5000
```

### 7.2 生产环境部署

```bash
# 使用 gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.app:create_app\(\)
```

### 7.3 注意事项

1. **端口选择**：默认使用 5000 端口，确保防火墙开放
2. **CORS 配置**：已启用 CORS，允许跨域访问
3. **日志目录**：确保 `logs/` 目录有写入权限
4. **配置文件**：确保 `config.yaml` 已正确配置

---

## 八、开发任务分解

### 8.1 任务清单

| 序号 | 任务 | 优先级 | 预计工时 |
|------|------|--------|----------|
| 1 | 创建 `src/app.py` Flask 应用入口 | P0 | 1h |
| 2 | 创建 `src/api/routes.py` API 路由 | P0 | 2h |
| 3 | 创建 `src/api/sse.py` SSE 模块 | P0 | 1h |
| 4 | 创建 `src/utils/log_manager.py` 日志管理器 | P0 | 2h |
| 5 | 重构 `src/services/taskRunner.py` 任务运行器 | P0 | 3h |
| 6 | 创建 `static/index.html` 前端页面 | P0 | 1h |
| 7 | 创建 `static/css/style.css` 样式文件 | P0 | 1h |
| 8 | 创建 `static/js/app.js` 前端逻辑 | P0 | 2h |
| 9 | 创建 `logs/` 目录和 .gitkeep | P1 | 0.5h |
| 10 | 更新 `requirements.txt` 添加 Flask 依赖 | P0 | 0.5h |
| 11 | 测试完整流程 | P1 | 2h |
| 12 | 更新 README 文档 | P2 | 1h |

### 8.2 实施顺序

```
Phase 1: 后端核心 (预计 6h)
├── 任务 1: 创建 Flask 应用入口
├── 任务 2: 创建 API 路由
├── 任务 3: 创建 SSE 模块
└── 任务 4: 创建日志管理器

Phase 2: 业务逻辑 (预计 3h)
└── 任务 5: 重构任务运行器

Phase 3: 前端界面 (预计 4h)
├── 任务 6: 创建 HTML 页面
├── 任务 7: 创建 CSS 样式
└── 任务 8: 创建 JavaScript 逻辑

Phase 4: 完善工作 (预计 4.5h)
├── 任务 9: 创建日志目录
├── 任务 10: 更新依赖文件
├── 任务 11: 测试流程
└── 任务 12: 更新文档
```

---

## 九、向后兼容

### 9.1 保持命令行模式

原有的命令行运行方式仍然保留：

```bash
# 命令行模式（原有功能）
python src/index.py "C:\example\dir"

# Web 模式（新增功能）
python src/app.py
```

### 9.2 配置文件复用

Web 模式和命令行模式共用同一份 `config.yaml` 配置文件，无需额外配置。

---

## 十、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| SSE 连接断开 | 用户可能看不到实时日志 | 添加重连机制，显示最后状态 |
| 任务执行时间过长 | 用户可能以为卡死 | 显示预估剩余时间，定期心跳 |
| 并发任务冲突 | 多个任务同时操作同一目录 | 添加任务队列，限制并发数 |
| 日志文件过多 | 占用磁盘空间 | 实施日志清理策略 |

---

## 十一、后续扩展

### 11.1 可选功能

1. **WebSocket 支持**：如果需要双向通信（如取消任务），可升级为 WebSocket
2. **任务队列**：使用 Redis/RabbitMQ 管理任务，支持分布式部署
3. **用户认证**：添加简单的密码保护
4. **历史记录页面**：查看历史运行记录和日志回放

### 11.2 性能优化

1. **API 并发限制**：限制同时生成的图片数量
2. **缓存机制**：缓存配置加载结果
3. **资源清理**：定期清理临时文件

---

## 十二、总结

本文档详细描述了 BuyerShowTool 项目从命令行工具到前后端分离 Web 应用的重构方案：

1. **后端**：使用 Flask 框架，提供简洁的 REST API 和 SSE 实时日志推送
2. **前端**：使用原生 HTML/CSS/JavaScript，提供友好的用户界面
3. **实时通信**：通过 SSE 实现后端到前端的实时日志推送
4. **日志持久化**：在项目根目录 `logs/` 下存储所有运行日志

该方案保持了原有的功能完整性，同时提供了更好的用户体验和可扩展性。

"""Flask 应用入口"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__, static_folder='../static', static_url_path='')
    
    # 启用 CORS
    CORS(app)
    
    # 注册 API 蓝图
    from src.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 根路径返回前端页面
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
"""配置管理器"""
import sys
import os
import yaml

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.config.loader import check_and_generate_config


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.config_path = os.path.join(project_root, "config.yaml")
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置到UI控件"""
        try:
            # 检查配置文件是否存在
            if not os.path.exists(self.config_path):
                # 尝试生成配置文件
                check_and_generate_config()
            
            # 读取配置文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 填充UI控件
            if config:
                # API配置
                deepseek_config = config.get('deepseek', {})
                tongyi_config = config.get('tongyi', {})
                
                if deepseek_config.get('apiKey'):
                    self.main_window.deepseek_key_entry.delete(0, tk.END)
                    self.main_window.deepseek_key_entry.insert(0, deepseek_config['apiKey'])
                
                if tongyi_config.get('apiKey'):
                    self.main_window.tongyi_key_entry.delete(0, tk.END)
                    self.main_window.tongyi_key_entry.insert(0, tongyi_config['apiKey'])
                
                # 生成参数
                review_count = deepseek_config.get('reviewCount', 3)
                image_count = tongyi_config.get('imageCount', 3)
                
                self.main_window.review_count_var.set(review_count)
                self.main_window.image_count_var.set(image_count)
                
                self.main_window.log_queue.put("配置加载成功")
            
        except Exception as e:
            self.main_window.log_queue.put(f"加载配置时发生错误: {e}")
    
    def save_config(self):
        """从UI控件保存配置到文件"""
        try:
            # 读取UI控件的值
            deepseek_key = self.main_window.deepseek_key_entry.get().strip()
            tongyi_key = self.main_window.tongyi_key_entry.get().strip()
            review_count = self.main_window.review_count_var.get()
            image_count = self.main_window.image_count_var.get()
            
            # 从现有配置文件读取默认值（如果存在）
            default_config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    default_config = yaml.safe_load(f) or {}
            
            # 创建配置字典，保留默认值
            config = {
                'deepseek': {
                    'url': default_config.get('deepseek', {}).get('url', 'https://api.deepseek.com/v1/chat/completions'),
                    'apiKey': deepseek_key,
                    'model': default_config.get('deepseek', {}).get('model', 'deepseek-chat'),
                    'systemPrompt': default_config.get('deepseek', {}).get('systemPrompt', '你是一位专业的电商运营专家...'),
                    'reviewCount': review_count
                },
                'tongyi': {
                    'url': default_config.get('tongyi', {}).get('url', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/generation'),
                    'apiKey': tongyi_key,
                    'model': default_config.get('tongyi', {}).get('model', 'wanx-v1'),
                    'systemPrompt': default_config.get('tongyi', {}).get('systemPrompt', '请生成一张电商买家秀模特图...'),
                    'imageCount': image_count
                }
            }
            
            # 保存到文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.main_window.log_queue.put("配置保存成功")
            
        except Exception as e:
            self.main_window.log_queue.put(f"保存配置时发生错误: {e}")
    
    def validate_config(self):
        """验证配置的有效性"""
        deepseek_key = self.main_window.deepseek_key_entry.get().strip()
        tongyi_key = self.main_window.tongyi_key_entry.get().strip()
        
        if not deepseek_key or not tongyi_key:
            return False
        
        return True

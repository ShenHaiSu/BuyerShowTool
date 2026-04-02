"""CLI交互模块 - 提供命令行交互式用户界面"""
import os
import sys
import yaml
from typing import Optional, Tuple

# 从loader.py导入配置模板
from src.config.loader import CONFIG_EXAMPLE_TEMPLATE


class CLI:
    """命令行交互工具类"""
    
    # ANSI 颜色代码
    COLOR_RESET = "\033[0m"
    COLOR_BOLD = "\033[1m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_BLUE = "\033[94m"
    COLOR_RED = "\033[91m"
    COLOR_CYAN = "\033[96m"
    
    @staticmethod
    def print_banner():
        """打印程序横幅"""
        banner = f"""
{CLI.COLOR_CYAN}{CLI.COLOR_BOLD}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ██████╗  ██████╗  ██████╗ ███╗   ███╗                   ║
║     ██╔══██╗██╔═══██╗██╔═══██╗████╗ ████║                   ║
║     ██████╔╝██║   ██║██║   ██║██╔████╔██║                   ║
║     ██╔═══╝ ██║   ██║██║   ██║██║╚██╔╝██║                   ║
║     ██║     ╚██████╔╝╚██████╔╝██║ ╚═╝ ██║                   ║
║     ╚═╝      ╚═════╝  ╚═════╝ ╚═╝     ╚═╝                   ║
║                                                              ║
║     {CLI.COLOR_RESET}买家秀生成工具 v1.0 - CLI Edition{CLI.COLOR_CYAN}               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{CLI.COLOR_RESET}
"""
        print(banner)
    
    @staticmethod
    def print_header(title: str, width: int = 60):
        """打印标题"""
        print(f"\n{CLI.COLOR_BOLD}{'─' * width}")
        print(f"  {title}")
        print(f"{'─' * width}{CLI.COLOR_RESET}\n")
    
    @staticmethod
    def print_step(step_num: int, total: int, message: str):
        """打印步骤信息"""
        print(f"{CLI.COLOR_BLUE}[{step_num}/{total}]{CLI.COLOR_RESET} {message}")
    
    @staticmethod
    def print_success(message: str):
        """打印成功信息"""
        print(f"{CLI.COLOR_GREEN}✓{CLI.COLOR_RESET} {message}")
    
    @staticmethod
    def print_warning(message: str):
        """打印警告信息"""
        print(f"{CLI.COLOR_YELLOW}⚠{CLI.COLOR_RESET} {message}")
    
    @staticmethod
    def print_error(message: str):
        """打印错误信息"""
        print(f"{CLI.COLOR_RED}✗{CLI.COLOR_RESET} {message}")
    
    @staticmethod
    def print_info(message: str):
        """打印普通信息"""
        print(f"{CLI.COLOR_CYAN}ℹ{CLI.COLOR_RESET} {message}")
    
    @staticmethod
    def input_path(prompt: str = "请输入工作路径", default: str = None) -> str:
        """询问用户输入路径"""
        if default:
            response = input(f"{CLI.COLOR_YELLOW}{prompt}{CLI.COLOR_RESET}\n[默认: {default}] > ")
            return response.strip() if response.strip() else default
        else:
            response = input(f"{CLI.COLOR_YELLOW}{prompt}{CLI.COLOR_RESET}\n> ")
            return response.strip()
    
    @staticmethod
    def input_yes_no(prompt: str, default: str = "n") -> bool:
        """询问是否确认 (y/n)"""
        default_str = "Y/n" if default == "y" else "N/y" if default == "n" else ""
        response = input(f"{CLI.COLOR_YELLOW}{prompt}{CLI.COLOR_RESET} [{default_str}] > ").strip().lower()
        
        if not response:
            return default == "y"
        
        return response in ["y", "yes", "是", "确认"]
    
    @staticmethod
    def input_api_key(service_name: str, current_key: str = None) -> str:
        """询问用户输入API Key"""
        print(f"\n{CLI.COLOR_BOLD}┌─ {service_name} API Key{CLI.COLOR_RESET}")
        print(f"{CLI.COLOR_BOLD}│{CLI.COLOR_RESET}")
        
        if current_key and current_key != "your-xxx-api-key-here":
            masked_key = CLI._mask_key(current_key)
            print(f"{CLI.COLOR_BOLD}│{CLI.COLOR_RESET} 当前Key: {CLI.COLOR_GREEN}{masked_key}{CLI.COLOR_RESET}")
        
        print(f"{CLI.COLOR_BOLD}│{CLI.COLOR_RESET} 请输入新的API Key (直接回车保留当前): ")
        print(f"{CLI.COLOR_BOLD}└{'─' * 40}{CLI.COLOR_RESET}")
        
        response = input("> ").strip()
        
        if not response:
            return current_key if current_key else None
        
        return response
    
    @staticmethod
    def _mask_key(key: str) -> str:
        """遮蔽Key的中间部分"""
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    
    @staticmethod
    def print_progress_bar(current: int, total: int, prefix: str = "", suffix: str = "", 
                          bar_length: int = 30, fill: str = "█", empty: str = "░"):
        """打印进度条"""
        if total == 0:
            percent = 0
        else:
            percent = int((current / total) * 100)
        
        filled = int((current / total) * bar_length) if total > 0 else 0
        bar = f"{CLI.COLOR_GREEN}{fill}{CLI.COLOR_RESET}" * filled + empty * (bar_length - filled)
        
        print(f"\r{prefix} [{bar}] {percent}% {suffix}", end="", flush=True)
        
        if current >= total:
            print()  # 完成后换行


class ConfigManager:
    """配置管理类 - 处理API Key的读写和CLI交互"""
    
    def __init__(self, config_dir: str = None):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = config_dir or os.path.join(self.project_root, 'src')
        self.config_path = os.path.join(self.config_dir, 'config.yaml')
        self.example_path = os.path.join(self.project_root, 'config.example.yaml')
        self.template = CONFIG_EXAMPLE_TEMPLATE
    
    def check_config_exists(self) -> bool:
        """检查config.yaml是否存在"""
        return os.path.exists(self.config_path)
    
    def load_existing_keys(self) -> Tuple[Optional[str], Optional[str]]:
        """加载已保存的API Keys"""
        try:
            if not os.path.exists(self.config_path):
                return None, None
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return None, None
            
            deepseek_key = data.get('deepseek', {}).get('apiKey')
            tongyi_key = data.get('tongyi', {}).get('apiKey')
            
            return deepseek_key, tongyi_key
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return None, None
    
    def save_config(self, deepseek_key: str, tongyi_key: str) -> bool:
        """保存配置到config.yaml"""
        try:
            config_data = {
                'deepseek': {
                    'url': 'https://api.deepseek.com/v1/chat/completions',
                    'apiKey': deepseek_key,
                    'model': 'deepseek-chat',
                    'systemPrompt': '你是一位专业的电商运营专家，擅长撰写真实、客观的买家好评文案。\n请根据提供的商品信息生成买家好评文案。\n要求：\n- 字数80字左右\n- 使用较为中肯的语气\n- 禁止使用感叹号\n- 禁止使用夸张的语态\n- 禁止使用"太棒了"、"超级推荐"等夸张词汇',
                    'reviewCount': 4
                },
                'tongyi': {
                    'apiKey': tongyi_key,
                    'model': 'wan2.7-image',
                    'systemPrompt': '请生成一张电商买家秀模特图。\n要求：\n- 模特不出现面部和头部\n- 背景为家居室内客厅环境或户外草地环境\n- 随机生成合适的姿势\n- 图片主体为商品本身\n- 画面真实自然，符合真实买家秀风格',
                    'imageCount': 4
                }
            }
            
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def generate_example_config(self):
        """生成config.example.yaml模板"""
        try:
            with open(self.example_path, 'w', encoding='utf-8') as f:
                f.write(self.template)
            return True
        except Exception as e:
            print(f"生成模板文件失败: {e}")
            return False
    
    def interactive_init(self):
        """CLI交互式初始化配置"""
        CLI.print_header("API Key 初始化配置")
        
        print(f"{CLI.COLOR_YELLOW}首次使用需要配置API Key{CLI.COLOR_RESET}\n")
        print("请到以下平台获取API Key:")
        print("  • DeepSeek: https://platform.deepseek.com/")
        print("  • 通义万相: https://dashscope.console.aliyun.com/")
        print()
        
        # 输入 DeepSeek API Key
        deepseek_key = CLI.input_api_key("DeepSeek")
        while not deepseek_key:
            CLI.print_error("DeepSeek API Key 不能为空!")
            deepseek_key = CLI.input_api_key("DeepSeek")
        
        # 输入 TongYi API Key
        tongyi_key = CLI.input_api_key("通义万相 (TongYi)")
        while not tongyi_key:
            CLI.print_error("通义万相 API Key 不能为空!")
            tongyi_key = CLI.input_api_key("通义万相 (TongYi)")
        
        # 保存配置
        CLI.print_info("正在保存配置...")
        if self.save_config(deepseek_key, tongyi_key):
            CLI.print_success("配置保存成功!")
        else:
            CLI.print_error("配置保存失败!")
            return False
        
        return True
    
    def interactive_update(self) -> bool:
        """CLI交互式更新配置 - 询问用户是否更换Key"""
        deepseek_key, tongyi_key = self.load_existing_keys()
        
        CLI.print_header("API Key 管理")
        CLI.print_info("当前已配置以下API Key:\n")
        
        # 显示 DeepSeek Key
        if deepseek_key:
            masked = CLI._mask_key(deepseek_key)
            CLI.print_success(f"DeepSeek: {masked}")
        else:
            CLI.print_warning("DeepSeek: 未配置")
        
        # 显示 TongYi Key
        if tongyi_key:
            masked = CLI._mask_key(tongyi_key)
            CLI.print_success(f"通义万相: {masked}")
        else:
            CLI.print_warning("通义万相: 未配置")
        
        print()
        
        # 询问是否需要更换
        if CLI.input_yes_no("是否需要更换或补充API Key?"):
            return self.interactive_init()
        
        return True

# BuyerShowTool CLI交互优化 - 实施指南

## 📋 需求概述

对 BuyerShowTool 进行 CLI 交互优化，实现以下功能：

1. **CLI命令行交互风格** - 优化用户交互体验，但不废除启动参数解析能力
2. **配置文件初始化引导** - 启动时检查 `config.yaml`，不存在则引导用户初始化 API Key
3. **API Key 管理** - 读取已保存的 Key，询问用户是否需要更换
4. **工作路径交互选择** - 用户未指定工作路径时，通过 CLI 步进交互询问
5. **进度可视化展示** - 逐步展示生成进度
6. **执行报告生成** - 任务完成后生成详细的统计报告

---

## 🔄 整体流程设计

### 启动流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      程序启动                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  解析命令行参数 (sys.argv)                                  │
│  - 检查是否指定了工作路径 (target_dir)                        │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │  已指定工作路径   │             │  未指定工作路径   │
    │  (跳过路径询问)  │             │  (进入CLI询问)   │
    └─────────────────┘             └─────────────────┘
              │                               │
              │                               ▼
              │               ┌─────────────────────────────┐
              │               │  CLI步进交互:询问工作路径    │
              │               │  - 显示当前目录              │
              │               │  - 支持输入路径/回车确认     │
              │               │  - 支持拖拽文件夹            │
              │               └─────────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  检查 src/config.yaml 是否存在                              │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │   config.yaml   │             │  config.yaml    │
    │    不存在       │             │    已存在       │
    └─────────────────┘             └─────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────────────┐
│  生成 config.example.yaml │    │  读取现有config.yaml内容         │
│  进入CLI初始化引导流程    │    │  询问用户: 是否需要更换Key?      │
└─────────────────────────┘    └─────────────────────────────────┘
              │                               │
              │               ┌───────────────┴───────────────┐
              │               │                               │
              ▼               ▼                               ▼
    ┌─────────────────┐  ┌───────────┐              ┌───────────────┐
    │ 输入DeepSeek    │  │  不更换   │              │   更换        │
    │ API Key        │  │  继续     │              │   进入CLI     │
    └─────────────────┘  └───────────┘              │   修改流程    │
              │                                   └───────────────┘
              ▼                                           │
    ┌─────────────────┐                                   │
    │ 输入TongYi      │◄──────────────────────────────────┘
    │ API Key        │
    └─────────────────┘
              │
              ▼
    ┌─────────────────────────────┐
    │  持久化配置到 config.yaml   │
    │  保存用户输入的API Keys     │
    └─────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  路径自动探索                                               │
│  - 在工作目录下递归搜索包含 goods.yaml 的目录                │
│  - 显示搜索进度                                             │
└─────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  逐一处理目标目录                                           │
│  - 显示当前处理进度 (n/total)                               │
│  - 生成好评文案 (带进度条)                                  │
│  - 生成买家秀图片 (带进度条)                                 │
│  - 统计字数、图片数量、磁盘占用                             │
└─────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  生成执行报告                                               │
│  - 本次生成字数统计                                         │
│  - 本次生成图片数量                                         │
│  - 图片磁盘占用 (总计/平均)                                 │
│  - 耗时统计 (总计/平均)                                     │
│  - 输出到屏幕并可选保存到文件                               │
└─────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                      程序退出                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 CLI 交互模块设计

### 新增文件: `src/utils/cli.py`

```python
"""CLI交互模块 - 提供命令行交互式用户界面"""
import os
import sys
import yaml
from typing import Optional, Tuple

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
            response = input(f"{CLI.COLOR_YELLOW}{prompt}{CLI.COLOR_RESET}\n[默认: {}] > ".format(default))
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
        self.template = CONFIG_EXAMPLE_TEMPLATE  # 从loader.py导入
    
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
```

---

## 📝 修改 `src/index.py` 详细设计

### 主要修改点

#### 1. 命令行参数解析增强

```python
import argparse

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='BuyerShowTool - 买家秀生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python src/index.py                                    # 交互式选择工作路径
  python src/index.py C:\\work\\products                  # 指定工作路径
  python src/index.py --path C:\\work\\products            # 使用--path参数
  python src/index.py --reconfig                          # 重新配置API Key
  python src/index.py --check                             # 仅检查配置状态
        """
    )
    
    parser.add_argument(
        'path', 
        nargs='?',  # 可选参数
        default=None,
        help='商品配置目录路径 (支持拖拽文件夹)'
    )
    
    parser.add_argument(
        '--path', '-p',
        dest='path',
        help='商品配置目录路径 (与位置参数等价)'
    )
    
    parser.add_argument(
        '--reconfig', '-r',
        action='store_true',
        help='重新配置API Key'
    )
    
    parser.add_argument(
        '--check', '-c',
        action='store_true',
        help='仅检查配置状态，不执行生成'
    )
    
    return parser.parse_args()
```

#### 2. 主函数重构

```python
def main():
    """主入口函数"""
    # 打印横幅
    CLI.print_banner()
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 处理 --check 参数
    if args.check:
        check_config_status(config_manager)
        sys.exit(0)
    
    # 处理 --reconfig 参数
    if args.reconfig:
        if config_manager.check_config_exists():
            config_manager.interactive_update()
        else:
            config_manager.generate_example_config()
            config_manager.interactive_init()
        sys.exit(0)
    
    # 确定工作路径
    target_dir = args.path
    
    if not target_dir:
        # 未指定路径，进入CLI交互选择
        CLI.print_header("选择工作路径")
        target_dir = interactive_select_workdir()
    
    # 验证工作路径
    if not os.path.exists(target_dir):
        CLI.print_error(f"路径不存在: {target_dir}")
        sys.exit(1)
    
    if not os.path.isdir(target_dir):
        CLI.print_error(f"路径不是目录: {target_dir}")
        sys.exit(1)
    
    # 检查并处理配置文件
    if not config_manager.check_config_exists():
        # config.yaml 不存在，进入初始化流程
        CLI.print_warning("配置文件不存在，首次使用需要配置API Key")
        config_manager.generate_example_config()
        if not config_manager.interactive_init():
            sys.exit(1)
    else:
        # config.yaml 存在，检查是否需要更换
        deepseek_key, tongyi_key = config_manager.load_existing_keys()
        
        # 检查Key是否有效
        if not deepseek_key or deepseek_key == "your-deepseek-api-key-here" or \
           not tongyi_key or tongyi_key == "your-tongyi-api-key-here":
            CLI.print_warning("检测到API Key未配置或无效")
            if not config_manager.interactive_init():
                sys.exit(1)
        else:
            # Key有效，询问是否更换
            CLI.print_info("检测到已配置的API Key")
            if CLI.input_yes_no("是否需要更换API Key?"):
                if not config_manager.interactive_update():
                    sys.exit(1)
    
    # 初始化错误处理器
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    error_handler = ErrorHandler(project_root)
    
    # 开始执行任务
    execute_tasks(target_dir, error_handler, config_manager)


def interactive_select_workdir() -> str:
    """CLI交互式选择工作目录"""
    CLI.print_step(1, 2, "选择工作目录")
    
    # 获取当前目录作为默认
    default_dir = os.getcwd()
    
    print(f"""
{CLI.COLOR_CYAN}请输入包含商品配置的目录路径{CLI.COLOR_RESET}

提示:
  • 可以直接输入路径，如: C:\\work\\products
  • 支持拖拽文件夹到终端
  • 直接回车使用当前目录: {default_dir}
""")
    
    while True:
        user_input = input(f"工作路径 [{CLI.COLOR_GREEN}回车确认{CLI.COLOR_RESET}] > ").strip()
        
        if not user_input:
            target_dir = default_dir
        else:
            target_dir = user_input
        
        # 验证路径
        if not os.path.exists(target_dir):
            CLI.print_error(f"路径不存在: {target_dir}")
            CLI.print_info("请重新输入有效路径")
            continue
        
        if not os.path.isdir(target_dir):
            CLI.print_error(f"路径不是目录: {target_dir}")
            continue
        
        # 确认选择
        CLI.print_success(f"已选择: {target_dir}")
        
        if CLI.input_yes_no("确认使用此目录?"):
            return target_dir
        
        CLI.print_info("请重新输入路径")


def check_config_status(config_manager: ConfigManager):
    """检查配置状态"""
    CLI.print_header("配置状态检查")
    
    if not config_manager.check_config_exists():
        CLI.print_warning("config.yaml 不存在")
        CLI.print_info("运行程序将引导您进行初始配置")
        return
    
    deepseek_key, tongyi_key = config_manager.load_existing_keys()
    
    CLI.print_info("config.yaml 状态:\n")
    
    # DeepSeek
    if deepseek_key and deepseek_key != "your-deepseek-api-key-here":
        CLI.print_success(f"DeepSeek API Key: {CLI._mask_key(deepseek_key)}")
    else:
        CLI.print_error("DeepSeek API Key: 未配置或无效")
    
    # TongYi
    if tongyi_key and tongyi_key != "your-tongyi-api-key-here":
        CLI.print_success(f"通义万相 API Key: {CLI._mask_key(tongyi_key)}")
    else:
        CLI.print_error("通义万相 API Key: 未配置或无效")


def execute_tasks(target_dir: str, error_handler: ErrorHandler, config_manager: ConfigManager):
    """执行任务"""
    # 搜索商品配置目录
    CLI.print_step(2, 4, "搜索商品配置目录")
    print()
    
    CLI.print_info("正在搜索包含 goods.yaml 的目录...")
    
    target_paths = find_goods_yaml_paths(target_dir, deep=True)
    
    if not target_paths:
        # 未找到，生成模板
        CLI.print_warning(f"未在 {target_dir} 下找到 goods.yaml")
        CLI.print_info("正在生成模板...")
        generate_goods_yaml_template(target_dir)
        
        print(f"""
{CLI.COLOR_YELLOW}商品配置模板已生成: {os.path.join(target_dir, 'goods.yaml')}{CLI.COLOR_RESET}

请编辑 goods.yaml 文件，配置商品信息后重新运行程序。
""")
        sys.exit(1)
    
    # 显示找到的目录
    print(f"\n{CLI.COLOR_GREEN}✓{CLI.COLOR_RESET} 找到 {len(target_paths)} 个商品配置目录:\n")
    for i, path in enumerate(target_paths, 1):
        print(f"  {CLI.COLOR_CYAN}{i}.{CLI.COLOR_RESET} {path}")
    print()
    
    if not CLI.input_yes_no("是否开始生成?"):
        CLI.print_info("已取消")
        sys.exit(0)
    
    # 初始化统计
    total_stats = {
        'reviews_count': 0,
        'reviews_chars': 0,
        'images_count': 0,
        'images_size': 0,
        'start_time': time.time(),
        'dirs_success': 0,
        'dirs_total': len(target_paths)
    }
    
    # 逐一处理
    for i, path in enumerate(target_paths, 1):
        CLI.print_header(f"处理目录 ({i}/{len(target_paths)})")
        print(f"📂 {path}\n")
        
        try:
            dir_stats = process_single_target(path)
            total_stats['dirs_success'] += 1
            
            # 累计统计
            if dir_stats:
                total_stats['reviews_count'] += dir_stats.get('reviews_count', 0)
                total_stats['reviews_chars'] += dir_stats.get('reviews_chars', 0)
                total_stats['images_count'] += dir_stats.get('images_count', 0)
                total_stats['images_size'] += dir_stats.get('images_size', 0)
                
        except Exception as e:
            error_handler.record_error(
                target_path=path,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
            CLI.print_error(f"处理失败: {e}")
    
    # 生成执行报告
    generate_execution_report(total_stats, error_handler)
    
    sys.exit(0 if total_stats['dirs_success'] == len(target_paths) else 1)
```

---

## 📊 执行报告设计

### 新增函数: `generate_execution_report()`

```python
def generate_execution_report(stats: dict, error_handler: ErrorHandler):
    """生成并显示执行报告"""
    
    # 计算耗时
    total_elapsed = time.time() - stats['start_time']
    total_minutes = int(total_elapsed // 60)
    total_seconds = int(total_elapsed % 60)
    
    # 平均计算
    avg_review_chars = stats['reviews_chars'] / stats['reviews_count'] if stats['reviews_count'] > 0 else 0
    avg_image_size = stats['images_size'] / stats['images_count'] if stats['images_count'] > 0 else 0
    avg_time_per_dir = total_elapsed / stats['dirs_total'] if stats['dirs_total'] > 0 else 0
    
    # 格式化磁盘大小
    def format_size(bytes_size):
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.2f} KB"
        else:
            return f"{bytes_size / (1024 * 1024):.2f} MB"
    
    # 格式化时间
    def format_time(seconds):
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}小时{minutes}分"
    
    # 构建报告
    report = f"""
{'═' * 60}
{CLI.COLOR_BOLD}                    执行报告                    {CLI.COLOR_RESET}
{'═' * 60}

{CLI.COLOR_CYAN}📦 任务概览{CLI.COLOR_RESET}
  • 处理目录: {stats['dirs_success']}/{stats['dirs_total']} 个
  • 执行状态: {'全部成功 ✓' if stats['dirs_success'] == stats['dirs_total'] else f'部分失败 ({stats["dirs_total"] - stats["dirs_success"]}个失败)'}

{CLI.COLOR_CYAN}📝 好评文案统计{CLI.COLOR_RESET}
  • 生成数量: {stats['reviews_count']} 条
  • 总字数: {stats['reviews_chars']} 字
  • 平均每条: {avg_review_chars:.1f} 字

{CLI.COLOR_CYAN}🖼️ 买家秀图片统计{CLI.COLOR_RESET}
  • 生成数量: {stats['images_count']} 张
  • 磁盘占用: {format_size(stats['images_size'])}
  • 平均每张: {format_size(avg_image_size)}

{CLI.COLOR_CYAN}⏱️ 耗时统计{CLI.COLOR_RESET}
  • 总耗时: {format_time(total_elapsed)}
  • 平均每目录: {format_time(avg_time_per_dir)}
"""

    # 添加错误信息（如有）
    if error_handler.has_errors():
        report += f"""
{CLI.COLOR_RED}❌ 错误信息{CLI.COLOR_RESET}
  • 错误数量: {error_handler.get_error_count()}
  • 详情已保存到: run_error_summary.log
"""

    report += f"""
{'═' * 60}
"""

    print(report)
    
    # 可选：保存报告到文件
    report_path = os.path.join(stats.get('project_root', os.getcwd()), 'execution_report.txt')
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            # 去掉颜色代码后保存
            clean_report = re.sub(r'\033\[[0-9;]*m', '', report)
            f.write(clean_report)
        CLI.print_success(f"报告已保存: {report_path}")
    except Exception as e:
        CLI.print_warning(f"报告保存失败: {e}")
```

---

## 🔧 修改 `process_single_target()` 函数

需要在处理单个目录时返回统计信息：

```python
def process_single_target(target_dir: str) -> dict:
    """处理单个目标目录，返回统计信息"""
    # 设置日志
    logger = setup_logger(target_dir)
    
    # 加载配置
    config, goods_data = load_all_config(target_dir)
    
    stats = {
        'reviews_count': 0,
        'reviews_chars': 0,
        'images_count': 0,
        'images_size': 0,
        'start_time': time.time()
    }
    
    # 生成好评文案
    review_generator = ReviewGenerator(config)
    reviews = review_generator.generate_reviews(goods_data, target_dir)
    
    if reviews:
        stats['reviews_count'] = len(reviews)
        stats['reviews_chars'] = sum(len(r.strip()) for r in reviews)
    
    # 生成买家秀图片
    image_generator = ImageGenerator(config)
    image_paths = image_generator.generate_buyer_show_images(goods_data, target_dir)
    
    if image_paths:
        stats['images_count'] = len(image_paths)
        for img_path in image_paths:
            if os.path.exists(img_path):
                stats['images_size'] += os.path.getsize(img_path)
    
    return stats
```

---

## ⚠️ 注意事项和细节

### 1. API Key 安全提示

- 在CLI交互中输入Key时，屏幕会有掩码显示
- 保存到文件时使用 `yaml.dump()` 确保格式正确
- 不在日志中记录完整的API Key

### 2. 路径处理兼容性

- Windows 路径使用 `os.path` 处理，自动兼容
- 支持拖拽文件夹到终端（自动获取路径字符串）
- 用户输入时自动 `strip()` 去除首尾空白

### 3. 进度展示优化

- 使用 `\r` 回车符覆盖同一行，实现动态进度
- 进度条使用 Unicode 块字符 `█░`
- 预估剩余时间基于已完成项的平均耗时

### 4. 错误恢复

- 单个目录处理失败不影响其他目录
- 所有错误记录到 `run_error_summary.log`
- 每个失败目录单独记录到 `error_detail.log`

### 5. 配置持久化

- 使用 `yaml.dump()` 保存，支持中文
- 配置路径: `src/config.yaml`
- 模板路径: `config.example.yaml`

### 6. 交互式输入验证

- 空输入使用默认值
- 无效路径重新询问
- 确认操作防止误执行

---

## 📁 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/index.py` | 修改 | 重构主入口，集成CLI交互 |
| `src/utils/cli.py` | 新增 | CLI工具类和ConfigManager |
| `src/config/loader.py` | 修改 | 导出CONFIG_EXAMPLE_TEMPLATE常量 |
| `src/utils/progress.py` | 修改 | 增强进度统计功能 |

---

## 🧪 测试清单

### 功能测试

- [ ] 无参数启动，进入CLI路径选择
- [ ] 指定 `-p` 参数启动，跳过路径询问
- [ ] config.yaml 不存在时触发初始化引导
- [ ] config.yaml 存在时询问是否更换Key
- [ ] API Key 输入验证（非空检查）
- [ ] 工作路径验证（存在性、目录类型）
- [ ] 多目录递归搜索功能
- [ ] 单目录处理失败不影响其他目录

### UI/UX测试

- [ ] 横幅显示正常
- [ ] 颜色代码正常渲染
- [ ] 进度条动态更新
- [ ] 交互提示清晰易懂
- [ ] 错误信息明确

### 报告生成测试

- [ ] 字数统计准确
- [ ] 图片数量准确
- [ ] 磁盘大小计算准确
- [ ] 耗时计算准确
- [ ] 报告文件保存成功

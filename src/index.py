"""BuyerShowTool 入口文件"""
import sys
import os
import traceback
import time
import re
import argparse

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.loader import load_all_config, check_and_generate_config, generate_goods_yaml_template
from src.services.reviewGenerator import ReviewGenerator
from src.services.imageGenerator import ImageGenerator
from src.utils.logger import setup_logger
from src.utils.file import find_goods_yaml_paths
from src.utils.error_handler import ErrorHandler
from src.utils.progress import ProgressTracker
from src.utils.cli import CLI, ConfigManager


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
{CLI.COLOR_BOLD}{'═' * 60}{CLI.COLOR_RESET}
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


def execute_tasks(target_dir: str, error_handler: ErrorHandler, config_manager: ConfigManager):
    """执行任务"""
    project_root = config_manager.project_root
    
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
        'dirs_total': len(target_paths),
        'project_root': project_root
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


def process_single_target(target_dir: str, progress: ProgressTracker = None) -> dict:
    """处理单个目标目录，返回统计信息"""
    # 设置日志
    logger = setup_logger(target_dir)
    
    stats = {
        'reviews_count': 0,
        'reviews_chars': 0,
        'images_count': 0,
        'images_size': 0,
        'start_time': time.time()
    }
    
    print(f"\n📁 目标目录: {target_dir}")
    
    # 加载配置
    print("正在加载配置...")
    
    config, goods_data = load_all_config(target_dir)
    
    print(f"  📦 商品名称: {goods_data.goods.name}")
    print(f"  🖼️ 商品图片: {len(goods_data.images)} 张")
    
    # 获取生成数量
    review_count = config.deepseek.reviewCount
    image_count = config.tongyi.imageCount
    
    # 初始化进度追踪器
    if progress is None:
        progress = ProgressTracker(review_count, image_count)
    else:
        progress.total_reviews = review_count
        progress.total_images = image_count
    
    print_header(f"📋 任务概览: 好评文案 {review_count} 条 + 买家秀图片 {image_count} 张")
    
    # 生成好评文案
    print("\n📝 开始生成好评文案...")
    
    review_generator = ReviewGenerator(config)
    reviews = review_generator.generate_reviews(goods_data, target_dir)
    
    if reviews:
        progress.completed_reviews = len(reviews)
        stats['reviews_count'] = len(reviews)
        stats['reviews_chars'] = sum(len(r.strip()) for r in reviews)
        print_success(f"好评文案生成完成: {len(reviews)}/{review_count} 条")
    else:
        print_warning("未能生成好评文案")
    
    print()
    
    # 生成买家秀图片
    print("🖼️ 开始生成买家秀图片...")
    
    image_generator = ImageGenerator(config)
    image_paths = image_generator.generate_buyer_show_images(goods_data, target_dir)
    
    if image_paths:
        progress.completed_images = len(image_paths)
        stats['images_count'] = len(image_paths)
        for img_path in image_paths:
            if os.path.exists(img_path):
                stats['images_size'] += os.path.getsize(img_path)
        print_success(f"买家秀图片生成完成: {len(image_paths)}/{image_count} 张")
    else:
        print_warning("未能生成买家秀图片")
    
    # 打印本次任务汇总
    progress.print_summary()
    
    # 完成
    print_header(f"✅ 目录 {target_dir} 处理完成!")
    
    return stats


def print_header(title: str, width: int = 60):
    """打印标题（兼容函数）"""
    print(f"\n{CLI.COLOR_BOLD}{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}{CLI.COLOR_RESET}\n")


def print_success(message: str):
    """打印成功信息（兼容函数）"""
    CLI.print_success(message)


def print_warning(message: str):
    """打印警告信息（兼容函数）"""
    CLI.print_warning(message)


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


if __name__ == "__main__":
    main()

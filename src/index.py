"""BuyerShowTool 入口文件"""
import sys
import os
import traceback
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.loader import load_all_config, check_and_generate_config, generate_goods_yaml_template
from src.services.reviewGenerator import ReviewGenerator
from src.services.imageGenerator import ImageGenerator
from src.utils.logger import setup_logger
from src.utils.file import find_goods_yaml_paths
from src.utils.error_handler import ErrorHandler
from src.utils.progress import ProgressTracker, print_header, print_success, print_warning, print_error


def main():
    """主入口函数"""
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("用法: python src/index.py <目标目录路径>")
        print("示例: python src/index.py C:\\example\\dir")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    # 验证目标目录
    if not os.path.exists(target_dir):
        print(f"错误: 目标目录不存在: {target_dir}")
        sys.exit(1)
    
    if not os.path.isdir(target_dir):
        print(f"错误: 目标路径不是目录: {target_dir}")
        sys.exit(1)
    
    # 初始化错误处理器
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    error_handler = ErrorHandler(project_root)
    
    print("=" * 50)
    print("BuyerShowTool - 买家秀生成工具")
    print("=" * 50)
    
    # 检查配置文件
    config_exists = check_and_generate_config()
    if not config_exists:
        print("错误: 配置文件不存在")
        print()
        print("请先配置项目:")
        print("1. 复制 config.example.yaml 为 config.yaml")
        print("2. 修改 config.yaml 中的 API 密钥配置")
        print("3. 重新运行程序")
        print()
        print("配置文件已生成: config.example.yaml")
        print("=" * 50)
        sys.exit(1)
    
    # 查找所有包含 goods.yaml 的目标路径
    print("正在搜索商品配置目录...")
    target_paths = find_goods_yaml_paths(target_dir, deep=True)
    
    if not target_paths:
        # 如果没有找到，尝试在目标目录生成 goods.yaml 模板
        print(f"未在 {target_dir} 下找到 goods.yaml，正在生成模板...")
        generate_goods_yaml_template(target_dir)
        print("错误: 商品配置文件不存在")
        print()
        print("请先配置商品信息:")
        print("1. 编辑 goods.yaml 文件")
        print("2. 配置商品名称、图片等信息")
        print("3. 重新运行程序")
        print()
        print("商品配置模板已生成: goods.yaml")
        print("=" * 50)
        sys.exit(1)
    
    print(f"找到 {len(target_paths)} 个商品配置目录:")
    for path in target_paths:
        print(f"  - {path}")
    print()
    
    # 逐一处理每个目标路径
    success_count = 0
    total_start_time = time.time()
    
    # 打印总任务信息
    print_header("🚀 开始执行任务", 60)
    print(f"  📂 待处理目录: {len(target_paths)} 个")
    print()
    
    for i, path in enumerate(target_paths, 1):
        print(f"\n{'='*60}")
        print(f"  📂 处理第 {i}/{len(target_paths)} 个目录: {path}")
        print(f"{'='*60}")
        
        try:
            process_single_target(path)
            success_count += 1
        except Exception as e:
            # 记录错误但不终止进程
            error_handler.record_error(
                target_path=path,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
            print_error(f"处理目录 {path} 时发生错误: {e}")
            print_warning("继续处理下一个目录...\n")
    
    # 保存错误报告
    error_handler.save_summary_error()
    for path in target_paths:
        error_handler.save_detail_error(path)
    
    # 计算总耗时
    total_elapsed = time.time() - total_start_time
    total_minutes = int(total_elapsed // 60)
    total_seconds = int(total_elapsed % 60)
    elapsed_str = f"{total_minutes}分{total_seconds}秒" if total_minutes > 0 else f"{total_seconds}秒"
    
    # 输出汇总信息
    print("\n" + "=" * 60)
    print("  🎉 任务执行完成!")
    print("=" * 60)
    print(f"  ✅ 成功处理: {success_count}/{len(target_paths)} 个目录")
    print(f"  ⏱️  总耗时: {elapsed_str}")
    
    if error_handler.has_errors():
        error_count = error_handler.get_error_count()
        print(f"  ❌ 错误数量: {error_count}")
        print(f"\n  错误详情已保存到:")
        print(f"    - 项目根目录: run_error_summary.log")
        for path in target_paths:
            print(f"    - {path}: error_detail.log")
    
    print("=" * 60)
    
    sys.exit(0 if success_count == len(target_paths) else 1)




def process_single_target(target_dir: str, progress: ProgressTracker = None):
    """处理单个目标目录"""
    # 设置日志
    logger = setup_logger(target_dir)
    
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
        print_success(f"买家秀图片生成完成: {len(image_paths)}/{image_count} 张")
    else:
        print_warning("未能生成买家秀图片")
    
    # 打印本次任务汇总
    progress.print_summary()
    
    # 完成
    print_header(f"✅ 目录 {target_dir} 处理完成!")


if __name__ == "__main__":
    main()
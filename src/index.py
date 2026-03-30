"""BuyerShowTool 入口文件"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.loader import load_all_config
from src.services.reviewGenerator import ReviewGenerator
from src.services.imageGenerator import ImageGenerator
from src.utils.logger import setup_logger


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
    
    # 设置日志
    logger = setup_logger(target_dir)
    
    print("=" * 50)
    print("BuyerShowTool - 买家秀生成工具")
    print("=" * 50)
    print(f"目标目录: {target_dir}")
    print()
    
    try:
        # 加载配置
        print("正在加载配置...")
        config, goods_data = load_all_config(target_dir)
        print(f"商品名称: {goods_data.goods.name}")
        print(f"商品图片: {goods_data.images}")
        print()
        
        # 生成好评文案
        print("-" * 50)
        print("开始生成好评文案...")
        print("-" * 50)
        review_generator = ReviewGenerator(config)
        reviews = review_generator.generate_reviews(goods_data, target_dir)
        
        if reviews:
            print(f"成功生成 {len(reviews)} 条好评文案")
        else:
            print("警告: 未能生成好评文案")
        print()
        
        # 生成买家秀图片
        print("-" * 50)
        print("开始生成买家秀图片...")
        print("-" * 50)
        image_generator = ImageGenerator(config)
        image_paths = image_generator.generate_buyer_show_images(goods_data, target_dir)
        
        if image_paths:
            print(f"成功生成 {len(image_paths)} 张买家秀图片")
        else:
            print("警告: 未能生成买家秀图片")
        print()
        
        # 完成
        print("=" * 50)
        print("任务完成!")
        print("=" * 50)
        print(f"生成的文件:")
        print(f"  - review.txt: 好评文案")
        for i, img_path in enumerate(image_paths, 1):
            print(f"  - buyer_show_{i}.jpg: 买家秀图片")
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
        logger.error(str(e))
        sys.exit(1)
    except ValueError as e:
        print(f"配置错误: {e}")
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        logger.error(str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
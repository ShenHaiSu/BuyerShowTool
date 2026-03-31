"""文件操作工具模块"""
import os
import shutil
from typing import List
from urllib.request import urlretrieve
from urllib.error import URLError


def ensure_dir(path: str) -> None:
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)


def save_text_file(file_path: str, content: str) -> None:
    """保存文本文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def read_text_file(file_path: str) -> str:
    """读取文本文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def download_image(url: str, save_path: str) -> bool:
    """下载图片"""
    try:
        urlretrieve(url, save_path)
        return True
    except URLError as e:
        print(f"下载图片失败: {url}, 错误: {e}")
        return False
    except Exception as e:
        print(f"下载图片失败: {url}, 错误: {e}")
        return False


def check_file_exists(file_path: str) -> bool:
    """检查文件是否存在"""
    return os.path.exists(file_path)


def get_file_list(dir_path: str, extensions: List[str] = None) -> List[str]:
    """获取目录下的文件列表"""
    if not os.path.exists(dir_path):
        return []
    
    files = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            if extensions:
                ext = os.path.splitext(item)[1].lower()
                if ext in extensions:
                    files.append(item)
            else:
                files.append(item)
    
    return files


def copy_file(src: str, dst: str) -> bool:
    """复制文件"""
    try:
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"复制文件失败: {src} -> {dst}, 错误: {e}")
        return False


def find_goods_yaml_paths(root_path: str, deep: bool = False) -> List[str]:
    """
    查找所有包含 goods.yaml 的文件夹路径
    
    Args:
        root_path: 根路径
        deep: 是否深度遍历（找到后仍继续搜索子目录）
    
    Returns:
        List[str]: 包含 goods.yaml 的文件夹路径列表
    """
    result = []
    
    goods_yaml_path = os.path.join(root_path, "goods.yaml")
    if os.path.exists(goods_yaml_path):
        result.append(root_path)
        if not deep:
            return result
    
    if os.path.isdir(root_path):
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path):
                sub_results = find_goods_yaml_paths(item_path, deep)
                result.extend(sub_results)
    
    return result
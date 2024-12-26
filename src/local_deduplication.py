"""本地文件去重工具
使用MD5值去重本地文件
使用方法:python local_deduplication.py "目录路径"
"""
import os
import hashlib
import logging
import argparse
import re
from typing import Dict, Set

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deduplication.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def calculate_md5(file_path: str) -> str:
    """
    计算文件的MD5值
    Args:
        file_path: 文件路径
    Returns:
        文件的MD5值
    """
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError) as e:
        logging.error(f"计算文件 {file_path} 的MD5值时出错: {e}")
        return ""

def is_duplicate_filename(filename: str) -> bool:
    """
    判断文件名是否为重复文件
    检查以下情况：
    1. (1), (2) 等数字后缀
    2. 副本
    3. copy
    4. 复制
    Args:
        filename: 文件名
    Returns:
        是否为重复文件名
    """
    name, _ = os.path.splitext(filename)
    duplicate_patterns = [
        r'\(\d+\)$',           # 匹配 (1), (2) 等
        r'副本$',              # 匹配 "副本"
        r'[cC]opy$',          # 匹配 "copy" 或 "Copy"
        r'复制$',             # 匹配 "复制"
        r'副本\s*\(\d+\)$',   # 匹配 "副本 (1)" 等
        r'[cC]opy\s*\(\d+\)$' # 匹配 "copy (1)" 等
    ]

    return any(bool(re.search(pattern, name)) for pattern in duplicate_patterns)

def deduplicate_files(directory: str) -> None:
    """
    去重文件
    Args:
        directory: 要处理的目录路径
    """
    try:
        # 修改 Path 相关的检查
        if not os.path.exists(directory):
            logging.error(f"目录 {directory} 不存在")
            return

        logging.info(f"开始处理目录: {directory}")

        # 记录处理的统计信息
        total_files = 0
        deleted_files = 0
        error_files = 0

        # 用于存储每个目录下文件的MD5值
        for root, _, files in os.walk(directory):
            logging.info(f"处理子目录: {root}")
            md5_dict: Dict[str, str] = {}  # MD5 -> 文件路径
            processed_files: Set[str] = set()  # 已处理的文件集合

            # 首先处理非重复文件名的文件
            for file in sorted(files):
                if file in processed_files:
                    continue

                total_files += 1
                file_path = os.path.join(root, file)

                try:
                    # 如果是重复文件名格式，先跳过
                    if is_duplicate_filename(file):
                        continue

                    file_md5 = calculate_md5(file_path)
                    if not file_md5:
                        error_files += 1
                        continue

                    md5_dict[file_md5] = file_path
                    processed_files.add(file)

                except Exception as e:
                    logging.error(f"处理文件 {file_path} 时出错: {str(e)}")
                    error_files += 1
                    continue

            # 然后处理可能的重复文件
            for file in sorted(files):
                if file in processed_files:
                    continue

                file_path = os.path.join(root, file)

                try:
                    file_md5 = calculate_md5(file_path)
                    if not file_md5:
                        error_files += 1
                        continue

                    if file_md5 in md5_dict:
                        # 发现重复文件
                        logging.info(f"发现重复文件:")
                        logging.info(f"  原文件: {md5_dict[file_md5]}")
                        logging.info(f"  重复文件: {file_path}")

                        # 删除重复文件
                        os.remove(file_path)
                        deleted_files += 1
                        logging.info(f"已删除重复文件: {file_path}")
                    else:
                        md5_dict[file_md5] = file_path

                    processed_files.add(file)

                except (IOError, OSError) as e:
                    logging.error(f"处理文件 {file_path} 时出错: {e}")
                    error_files += 1
                    continue

        # 输出统计信息
        logging.info("\n处理完成!")
        logging.info(f"总文件数: {total_files}")
        logging.info(f"删除重复文件数: {deleted_files}")
        logging.info(f"处理出错文件数: {error_files}")

    except (IOError, OSError) as e:
        logging.error(f"处理目录时发生错误: {e}")

def main():
    """主函数"""


    parser = argparse.ArgumentParser(description='文件去重工具')
    parser.add_argument('directory', type=str, help='要处理的目录路径')
    args = parser.parse_args()

    logging.info("文件去重工具启动")
    deduplicate_files(args.directory)
    logging.info("文件去重工具结束")

if __name__ == "__main__":
    main()

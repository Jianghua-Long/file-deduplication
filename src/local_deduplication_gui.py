"""本地文件去重工具
使用MD5值去重本地文件
使用方法:python local_deduplication.py "目录路径"
"""
import os
import hashlib
import logging
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Set
from threading import Thread

class FileDeduplicationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文件去重工具")
        self.root.geometry("600x400")

        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('deduplication.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        self.setup_ui()

    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 文件夹选择区域
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.folder_path = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.grid(row=0, column=0, padx=5)

        browse_btn = ttk.Button(folder_frame, text="选择文件夹", command=self.browse_folder)
        browse_btn.grid(row=0, column=1, padx=5)

        # 开始按钮
        start_btn = ttk.Button(main_frame, text="开始去重", command=self.start_deduplication)
        start_btn.grid(row=1, column=0, columnspan=2, pady=10)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate',
                                          variable=self.progress_var)
        self.progress_bar.grid(row=2, column=0, columnspan=2, pady=5)

        # 状态显示
        self.status_text = tk.Text(main_frame, height=15, width=70)
        self.status_text.grid(row=3, column=0, columnspan=2, pady=5)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)

        # 统计信息
        self.stats_label = ttk.Label(main_frame, text="等待开始...")
        self.stats_label.grid(row=4, column=0, columnspan=2, pady=5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def update_status(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()

    def calculate_md5(self, file_path: str) -> str:
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError) as e:
            self.update_status(f"计算文件 {file_path} 的MD5值时出错: {e}")
            return ""

    def is_duplicate_filename(self, filename: str) -> bool:
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

    def deduplicate_files(self):
        directory = self.folder_path.get()
        try:
            if not os.path.exists(directory):
                messagebox.showerror("错误", f"目录 {directory} 不存在")
                return

            self.update_status(f"开始处理目录: {directory}")

            total_files = sum(len(files) for _, _, files in os.walk(directory))
            processed_count = 0
            deleted_files = 0
            error_files = 0

            for root, _, files in os.walk(directory):
                self.update_status(f"处理子目录: {root}")
                md5_dict: Dict[str, str] = {}
                processed_files: Set[str] = set()

                # 首先处理非重复文件名的文件
                for file in sorted(files):
                    if file in processed_files:
                        continue

                    processed_count += 1
                    self.progress_var.set((processed_count / total_files) * 100)

                    file_path = os.path.join(root, file)

                    try:
                        if self.is_duplicate_filename(file):
                            continue

                        file_md5 = self.calculate_md5(file_path)
                        if not file_md5:
                            error_files += 1
                            continue

                        md5_dict[file_md5] = file_path
                        processed_files.add(file)

                    except (IOError, OSError) as e:
                        self.update_status(f"处理文件 {file_path} 时出错: {e}")
                        error_files += 1
                        continue

                # 处理可能的重复文件
                for file in sorted(files):
                    if file in processed_files:
                        continue

                    file_path = os.path.join(root, file)

                    try:
                        file_md5 = self.calculate_md5(file_path)
                        if not file_md5:
                            error_files += 1
                            continue

                        if file_md5 in md5_dict:
                            self.update_status("发现重复文件:")
                            self.update_status(f"  原文件: {md5_dict[file_md5]}")
                            self.update_status(f"  重复文件: {file_path}")

                            os.remove(file_path)
                            deleted_files += 1
                            self.update_status(f"已删除重复文件: {file_path}")
                        else:
                            md5_dict[file_md5] = file_path

                        processed_files.add(file)

                    except (IOError, OSError) as e:
                        self.update_status(f"处理文件 {file_path} 时出错: {e}")
                        error_files += 1
                        continue

            # 更新最终统计信息
            stats = f"处理完成!\n总文件数: {total_files}\n删除重复文件数: {deleted_files}\n处理出错文件数: {error_files}"
            self.stats_label.config(text=stats)
            messagebox.showinfo("完成", "文件去重完成！")

        except (IOError, OSError) as e:
            messagebox.showerror("错误", f"处理过程中发生错误: {str(e)}")
        finally:
            self.progress_var.set(0)

    def start_deduplication(self):
        if not self.folder_path.get():
            messagebox.showwarning("警告", "请先选择要处理的文件夹！")
            return

        # 清空状态显示
        self.status_text.delete(1.0, tk.END)
        self.stats_label.config(text="处理中...")

        # 在新线程中运行去重操作
        Thread(target=self.deduplicate_files, daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FileDeduplicationGUI()
    app.run()

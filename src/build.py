import PyInstaller.__main__
import shutil
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 确保输出目录存在
dist_dir = os.path.join(current_dir, 'dist')
if not os.path.exists(dist_dir):
    os.makedirs(dist_dir)

# 构建源文件的完整路径
cli_script = os.path.join(current_dir, 'local_deduplication.py')
gui_script = os.path.join(current_dir, 'local_deduplication_gui.py')

# 打包命令行版本
PyInstaller.__main__.run([
    cli_script,
    '--onefile',
    '--name', 'file_dedup_cli',
    '--distpath', dist_dir
])

# 打包GUI版本
PyInstaller.__main__.run([
    gui_script,
    '--onefile',
    '--windowed',
    '--name', 'file_dedup_gui',
    '--distpath', dist_dir
])
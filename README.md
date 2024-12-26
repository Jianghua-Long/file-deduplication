# 文件去重工具

一个简单的文件去重工具，支持命令行和图形界面两种使用方式。

## 功能特点

- 使用MD5值精确检测重复文件
- 智能识别常见重复文件命名（如"副本"、"copy"等）
- 自动生成详细的操作日志
- 支持命令行和图形界面两种操作方式
- 实时显示处理进度（GUI版本）

## 下载和安装

1. 从 [Releases](https://github.com/Jianghua-Long/file-deduplication/releases) 页面下载最新版本
2. [GUI版](https://github.com/Jianghua-Long/file-deduplication/releases/download/v1.0.0/file_dedup_gui.exe)
3. [命令行版](https://github.com/Jianghua-Long/file-deduplication/releases/download/v1.0.0/file_dedup_cli.exe)
4. 解压下载的文件到任意目录

## 使用方法

### GUI版本（推荐）

1. 运行 `file_dedup_gui.exe`
2. 点击"选择文件夹"按钮选择要处理的目录
3. 点击"开始去重"按钮开始处理
4. 等待处理完成，查看结果

### 命令行版本

1. 打开命令提示符（CMD）
2. 运行：file_dedup_cli.exe "文件夹路径"

## 注意事项

- 使用前请备份重要文件，删除的文件无法恢复
- 程序会在运行目录生成 `deduplication.log` 日志文件
- 默认会删除以下命名形式的重复文件：
  - (1), (2) 等数字后缀
  - 副本
  - copy/Copy
  - 复制
  - 副本 (1) 等组合形式

## 运行环境要求

- Windows 7/8/10/11
- 不需要安装Python或其他依赖

## 日志文件

程序会在运行目录生成 `deduplication.log` 文件，记录：
- 处理的文件信息
- 删除的重复文件
- 错误信息
- 统计数据

## 常见问题

Q: 如何确定文件是否真的重复？
A: 程序使用MD5值进行严格比对，只有内容完全相同的文件才会被视为重复文件。

Q: 删除的文件可以恢复吗？
A: 不可以，请在使用前备份重要文件。

Q: 为什么处理大文件时比较慢？
A: 因为需要读取整个文件计算MD5值，大文件处理会相对较慢。

## 技术支持

如有问题或建议，请：
1. 查看 [Issues](https://github.com/Jianghua-Long/file-deduplication/issues)
2. 提交新的 Issue

## 许可证

MIT License

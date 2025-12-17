import os
import re
from typing import List, Dict, Any
from pathlib import Path
import tkinter as tk
from tkinter import filedialog


def select_save_directory() -> str:
    """
    弹出对话框让用户选择保存目录

    Returns:
        用户选择的目录路径，如果取消选择则返回空字符串
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    folder_path = filedialog.askdirectory(title="选择文件保存目录")
    root.destroy()
    return folder_path


def format_string(text: str, columns: List[int] = [1, 2, 3], save_dir: str = "") -> Dict[str, str]:
    """
    格式化字符串并提取内容，支持自定义保存目录

    Args:
        text: 输入的文本字符串
        columns: 需要提取的列
        save_dir: 文件保存目录，默认为空（当前目录）

    Returns:
        包含提取结果和完整文件路径的字典
    """
    if not text.strip():
        raise ValueError("请输入文本")

    # 文本处理逻辑（与之前相同）
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    groups = []
    current_group = None

    for line in lines:
        if re.match(r'^\d+$', line):
            if current_group:
                groups.append(current_group)
            current_group = {'id': line, 'columns': []}
        elif current_group and line:
            current_group['columns'].append(line)

    if current_group:
        groups.append(current_group)

    storyboard = ""
    image_description = ""
    video_description = ""

    for group in groups:
        columns_data = group['columns'].copy()
        if columns_data:
            video_description += columns_data.pop() + '\n'
        if columns_data:
            image_description += columns_data.pop() + '\n'
        if columns_data:
            filtered_columns = [
                item for item in columns_data
                if not item.startswith('🎬') and not item.startswith('⏱️')
            ]
            storyboard += '\n'.join(filtered_columns) + '\n'

    # 确定保存目录
    if not save_dir:
        save_dir = os.getcwd()  # 默认为当前工作目录

    # 确保目录存在
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    # 构建完整的文件路径
    result = {'save_dir': save_dir}
    file_paths = {}

    if 1 in columns:
        file_paths['storyboard'] = os.path.join(save_dir, '分镜.txt')
        result['storyboard'] = storyboard
    if 2 in columns:
        file_paths['image_description'] = os.path.join(save_dir, '图片描述词.txt')
        result['image_description'] = image_description
    if 3 in columns:
        file_paths['video_description'] = os.path.join(save_dir, '视频描述词.txt')
        result['video_description'] = video_description

    result['file_paths'] = file_paths
    return result


def save_to_file(content: str, file_path: str) -> bool:
    """
    将内容保存到指定路径

    Args:
        content: 要保存的内容
        file_path: 完整文件路径

    Returns:
        保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"文件保存失败: {e}")
        return False


def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as file:
        sample_text = file.read()
    return sample_text


# 使用示例
if __name__ == "__main__":
    # 示例文本
    split_path = input("请输入文件(.txt)路径: ").strip()

    try:
        print("请选择文件保存目录（取消将使用当前目录）...")
        custom_dir = select_save_directory()

        # 处理文本
        result = format_string(read_file(split_path), [1, 2, 3], custom_dir)

        # 保存文件
        for file_type, content_key in [('storyboard', '分镜'),
                                       ('image_description', '图片描述词'),
                                       ('video_description', '视频描述词')]:
            if file_type in result['file_paths']:
                success = save_to_file(result[file_type], result['file_paths'][file_type])
                if success:
                    print(f"{content_key}已保存至: {result['file_paths'][file_type]}")

    except ValueError as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

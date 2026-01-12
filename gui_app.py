#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频处理工具图形界面
集成视频时长调整和分镜描述词提取功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
from datetime import datetime

# 导入现有功能模块
try:
    from main import adjust_video_to_target_duration, process_folder_videos, get_duration_dict
    from txt_split import format_string, select_save_directory, save_to_file, read_file
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保 main.py 和 txt_split.py 在同一目录下")
    sys.exit(1)


class VideoProcessorGUI:
    """视频处理工具图形界面主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("视频处理工具 v1.0")
        self.root.geometry("800x600")
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # 创建消息队列用于线程通信
        self.message_queue = queue.Queue()
        
        # 创建主框架
        self.create_widgets()
        
        # 启动消息处理循环
        self.process_messages()
    
    def create_widgets(self):
        """创建界面组件"""
        
        # 创建笔记本（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建两个标签页
        self.create_video_tab()
        self.create_split_tab()
        self.create_log_tab()
    
    def create_video_tab(self):
        """创建视频处理标签页"""
        self.video_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.video_frame, text="视频时长调整")
        
        # 字幕文件选择
        ttk.Label(self.video_frame, text="字幕文件 (.srt):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.srt_path_var = tk.StringVar()
        ttk.Entry(self.video_frame, textvariable=self.srt_path_var, width=50).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(self.video_frame, text="选择文件", command=self.select_srt_file).grid(row=0, column=2, padx=10, pady=10)
        
        # 分镜文件选择
        ttk.Label(self.video_frame, text="分镜文件 (.txt):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.split_path_var = tk.StringVar()
        ttk.Entry(self.video_frame, textvariable=self.split_path_var, width=50).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(self.video_frame, text="选择文件", command=self.select_split_file).grid(row=1, column=2, padx=10, pady=10)
        
        # 视频文件夹选择
        ttk.Label(self.video_frame, text="视频文件夹:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.video_folder_var = tk.StringVar()
        ttk.Entry(self.video_frame, textvariable=self.video_folder_var, width=50).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(self.video_frame, text="选择文件夹", command=self.select_video_folder).grid(row=2, column=2, padx=10, pady=10)
        
        # 目标时长设置
        ttk.Label(self.video_frame, text="目标时长(秒):").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        self.target_duration_var = tk.StringVar(value="6")
        ttk.Entry(self.video_frame, textvariable=self.target_duration_var, width=20).grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        
        # 处理按钮
        self.process_video_btn = ttk.Button(self.video_frame, text="开始处理视频", command=self.process_videos)
        self.process_video_btn.grid(row=4, column=1, pady=20)
        
        # 进度标签
        self.video_progress_var = tk.StringVar(value="就绪")
        ttk.Label(self.video_frame, textvariable=self.video_progress_var).grid(row=5, column=0, columnspan=3, pady=10)
    
    def create_split_tab(self):
        """创建分镜提取标签页"""
        self.split_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.split_frame, text="分镜描述词提取")
        
        # 输入文件选择
        ttk.Label(self.split_frame, text="输入文件 (.txt):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.input_file_var = tk.StringVar()
        ttk.Entry(self.split_frame, textvariable=self.input_file_var, width=50).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(self.split_frame, text="选择文件", command=self.select_input_file).grid(row=0, column=2, padx=10, pady=10)
        
        # 保存目录选择
        ttk.Label(self.split_frame, text="保存目录:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.save_dir_var = tk.StringVar()
        ttk.Entry(self.split_frame, textvariable=self.save_dir_var, width=50).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(self.split_frame, text="选择目录", command=self.select_save_dir).grid(row=1, column=2, padx=10, pady=10)
        
        # 提取选项
        ttk.Label(self.split_frame, text="提取内容:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        
        self.extract_storyboard_var = tk.BooleanVar(value=True)
        self.extract_image_var = tk.BooleanVar(value=True)
        self.extract_video_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(self.split_frame, text="分镜", variable=self.extract_storyboard_var).grid(row=2, column=1, sticky=tk.W, padx=10)
        ttk.Checkbutton(self.split_frame, text="图片描述词", variable=self.extract_image_var).grid(row=3, column=1, sticky=tk.W, padx=10)
        ttk.Checkbutton(self.split_frame, text="视频描述词", variable=self.extract_video_var).grid(row=4, column=1, sticky=tk.W, padx=10)
        
        # 处理按钮
        self.process_split_btn = ttk.Button(self.split_frame, text="开始提取", command=self.process_split)
        self.process_split_btn.grid(row=5, column=1, pady=20)
        
        # 进度标签
        self.split_progress_var = tk.StringVar(value="就绪")
        ttk.Label(self.split_frame, textvariable=self.split_progress_var).grid(row=6, column=0, columnspan=3, pady=10)
    
    def create_log_tab(self):
        """创建日志标签页"""
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="处理日志")
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(self.log_frame, width=80, height=25)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 清空日志按钮
        ttk.Button(self.log_frame, text="清空日志", command=self.clear_log).pack(pady=5)
    
    # 文件选择方法
    def select_srt_file(self):
        """选择字幕文件"""
        filename = filedialog.askopenfilename(
            title="选择字幕文件",
            filetypes=[("SRT文件", "*.srt"), ("所有文件", "*.*")]
        )
        if filename:
            self.srt_path_var.set(filename)
    
    def select_split_file(self):
        """选择分镜文件"""
        filename = filedialog.askopenfilename(
            title="选择分镜文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.split_path_var.set(filename)
    
    def select_video_folder(self):
        """选择视频文件夹"""
        folder = filedialog.askdirectory(title="选择视频文件夹")
        if folder:
            self.video_folder_var.set(folder)
    
    def select_input_file(self):
        """选择输入文件"""
        filename = filedialog.askopenfilename(
            title="选择输入文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
    
    def select_save_dir(self):
        """选择保存目录"""
        folder = filedialog.askdirectory(title="选择保存目录")
        if folder:
            self.save_dir_var.set(folder)
    
    # 处理功能方法
    def process_videos(self):
        """处理视频"""
        # 验证输入
        srt_path = self.srt_path_var.get()
        split_path = self.split_path_var.get()
        video_folder = self.video_folder_var.get()
        
        if not srt_path:
            messagebox.showerror("错误", "请选择字幕文件")
            return
        
        if not split_path:
            messagebox.showerror("错误", "请选择分镜文件")
            return
        
        if not video_folder:
            messagebox.showerror("错误", "请选择视频文件夹")
            return
        
        # 禁用按钮，防止重复点击
        self.process_video_btn.config(state=tk.DISABLED)
        self.video_progress_var.set("正在处理...")
        
        # 在新线程中处理视频
        thread = threading.Thread(target=self._process_videos_thread, 
                                 args=(srt_path, split_path, video_folder))
        thread.daemon = True
        thread.start()
    
    def _process_videos_thread(self, srt_path, split_path, video_folder):
        """视频处理线程"""
        try:
            # 计算目标时长
            self.add_log("正在计算目标时长...")
            duration_dict = get_duration_dict(srt_path, split_path)
            self.add_log(f"计算完成，共 {len(duration_dict)} 个视频片段")
            
            # 处理视频
            self.add_log("开始处理视频...")
            
            # 这里需要调用 process_folder_videos 函数
            # 由于原函数需要修改，我们创建一个适配器
            from moviepy.video.fx import all as vfx
            import shutil
            
            # 支持的视频格式
            video_extensions = ('.mp4', '.MP4')
            
            # 创建输出子文件夹
            output_folder = os.path.join(video_folder, "adjusted_videos")
            os.makedirs(output_folder, exist_ok=True)
            
            processed_count = 0
            error_count = 0
            
            # 遍历文件夹中的文件
            for filename in os.listdir(video_folder):
                if filename.lower().endswith(video_extensions):
                    input_path = os.path.join(video_folder, filename)
                    
                    try:
                        # 检查视频时长
                        from moviepy.editor import VideoFileClip
                        with VideoFileClip(input_path) as video:
                            original_duration = video.duration
                        
                        self.add_log(f"\n处理视频: {filename}")
                        self.add_log(f"原始时长: {original_duration:.2f}秒")
                        
                        # 生成输出文件名
                        name, ext = os.path.splitext(filename)
                        output_filename = f"{name}{ext}"
                        index = name.split(".")[0]
                        
                        try:
                            target_duration = duration_dict[int(index) - 1]
                        except (ValueError, IndexError):
                            target_duration = 6  # 默认值
                            
                        output_path = os.path.join(output_folder, output_filename)
                        
                        # 时长小于目标时长的视频
                        if original_duration < target_duration:
                            self.add_log(f"视频时长不足{target_duration}秒，进行慢速处理...")
                            success = adjust_video_to_target_duration(
                                input_path, output_path, target_duration
                            )
                            
                            if success:
                                processed_count += 1
                                self.add_log(f"✓ 成功处理: {filename}")
                            else:
                                error_count += 1
                                self.add_log(f"✗ 处理失败: {filename}")
                        elif original_duration > target_duration > 2:
                            self.add_log(f"视频时长超过{target_duration}秒，进行加速处理...")
                            success = adjust_video_to_target_duration(
                                input_path, output_path, target_duration
                            )
                            
                            if success:
                                processed_count += 1
                                self.add_log(f"✓ 成功处理: {filename}")
                            else:
                                error_count += 1
                                self.add_log(f"✗ 处理失败: {filename}")
                        else:
                            self.add_log(f"字幕时长{target_duration}秒，视频时长已满足要求，跳过处理")
                            # 复制到输出文件夹保持原样
                            shutil.copy2(input_path, output_path)
                            
                    except Exception as e:
                        error_count += 1
                        self.add_log(f"处理视频 {filename} 时发生异常: {str(e)}")
            
            self.add_log(f"\n处理完成！")
            self.add_log(f"成功处理: {processed_count} 个视频")
            self.add_log(f"处理失败: {error_count} 个视频")
            self.add_log(f"输出文件夹: {output_folder}")
            
            # 更新UI
            self.message_queue.put(("video_complete", f"处理完成！成功: {processed_count}, 失败: {error_count}"))
            
        except Exception as e:
            self.add_log(f"处理过程中发生错误: {str(e)}")
            self.message_queue.put(("video_error", str(e)))
    
    def process_split(self):
        """处理分镜提取"""
        # 验证输入
        input_file = self.input_file_var.get()
        save_dir = self.save_dir_var.get()
        
        if not input_file:
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        # 确定提取的列
        columns = []
        if self.extract_storyboard_var.get():
            columns.append(1)
        if self.extract_image_var.get():
            columns.append(2)
        if self.extract_video_var.get():
            columns.append(3)
        
        if not columns:
            messagebox.showerror("错误", "请至少选择一项提取内容")
            return
        
        # 禁用按钮
        self.process_split_btn.config(state=tk.DISABLED)
        self.split_progress_var.set("正在提取...")
        
        # 在新线程中处理
        thread = threading.Thread(target=self._process_split_thread,
                                 args=(input_file, save_dir, columns))
        thread.daemon = True
        thread.start()
    
    def _process_split_thread(self, input_file, save_dir, columns):
        """分镜提取线程"""
        try:
            self.add_log("开始提取分镜描述词...")
            
            # 读取文件
            text_content = read_file(input_file)
            
            # 处理文本
            result = format_string(text_content, columns, save_dir)
            
            # 保存文件
            file_types = {
                'storyboard': '分镜',
                'image_description': '图片描述词', 
                'video_description': '视频描述词'
            }
            
            saved_count = 0
            for file_type, content_key in file_types.items():
                if file_type in result['file_paths']:
                    success = save_to_file(result[file_type], result['file_paths'][file_type])
                    if success:
                        self.add_log(f"{content_key}已保存至: {result['file_paths'][file_type]}")
                        saved_count += 1
            
            self.add_log(f"提取完成！共保存 {saved_count} 个文件")
            
            # 更新UI
            self.message_queue.put(("split_complete", f"提取完成！保存了 {saved_count} 个文件"))
            
        except Exception as e:
            self.add_log(f"提取过程中发生错误: {str(e)}")
            self.message_queue.put(("split_error", str(e)))
    
    # 日志相关方法
    def add_log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.message_queue.put(("log", log_message))
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def process_messages(self):
        """处理消息队列中的消息"""
        try:
            while True:
                msg_type, msg_content = self.message_queue.get_nowait()
                
                if msg_type == "log":
                    self.log_text.insert(tk.END, msg_content + "\n")
                    self.log_text.see(tk.END)
                elif msg_type == "video_complete":
                    self.video_progress_var.set(msg_content)
                    self.process_video_btn.config(state=tk.NORMAL)
                    messagebox.showinfo("完成", msg_content)
                elif msg_type == "video_error":
                    self.video_progress_var.set("处理失败")
                    self.process_video_btn.config(state=tk.NORMAL)
                    messagebox.showerror("错误", msg_content)
                elif msg_type == "split_complete":
                    self.split_progress_var.set(msg_content)
                    self.process_split_btn.config(state=tk.NORMAL)
                    messagebox.showinfo("完成", msg_content)
                elif msg_type == "split_error":
                    self.split_progress_var.set("提取失败")
                    self.process_split_btn.config(state=tk.NORMAL)
                    messagebox.showerror("错误", msg_content)
                    
        except queue.Empty:
            pass
        
        # 每100毫秒检查一次消息队列
        self.root.after(100, self.process_messages)


def main():
    """主函数"""
    root = tk.Tk()
    app = VideoProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
import os
from moviepy.editor import VideoFileClip
import re
from datetime import datetime, timedelta


def adjust_video_to_target_duration(input_path, output_path, target_duration=6):
    """
    将视频调整到目标时长

    参数:
    input_path: 输入视频路径
    output_path: 输出视频路径
    target_duration: 目标时长(秒)
    """
    try:
        # 读取视频
        with VideoFileClip(input_path) as video:
            original_duration = video.duration

            if original_duration < target_duration:
                # 计算速度因子：原时长/目标时长
                speed_factor = original_duration / target_duration
                print(f"计算得到的速度因子: {speed_factor:.4f}")

                # 检查速度因子是否在有效范围内
                if speed_factor <= 0:
                    print(f"速度因子 {speed_factor:.4f} 超出合理范围，视频可能无法正常处理")
                    return False

                # 放慢视频速度
                adjusted_video = video.fx(vfx.speedx, factor=speed_factor)
                print(f"调整后视频的计算时长: {original_duration / speed_factor:.2f}秒")
                # **关键步骤：根据帧率重新计算精确的持续时间**
                # 计算目标时长内应包含的总帧数（四舍五入到整数）
                total_frames = int(round(target_duration * video.fps))
                # 通过裁剪确保帧数精确
                final_clip = adjusted_video.subclip(0, total_frames / video.fps)

                # 保存调整后的视频
                final_clip.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    fps=video.fps,
                    audio_bitrate="192k",
                    bitrate='6900k'
                )
            else:
                adjusted_video = video.fx(vfx.speedx, final_duration=target_duration)
                adjusted_video.write_videofile(output_path,
                                               codec="libx264",
                                               audio_codec="aac",
                                               fps=video.fps,
                                               audio_bitrate="192k",
                                               bitrate='6900k')

            # 验证输出视频时长
            output_video = VideoFileClip(output_path)
            actual_duration = output_video.duration
            output_video.close()

            print(f"处理完成！实际输出视频时长: {actual_duration:.2f}秒")
            return True

    except Exception as e:
        print(f"处理视频 {input_path} 时出错: {str(e)}")
        return False


def process_folder_videos(folder_path, duration_dict):
    """
    处理文件夹中的所有MP4视频文件

    参数:
    folder_path: 文件夹路径
    duration_dict: 目标时长数组
    """
    # 支持的视频格式
    video_extensions = ('.mp4', '.MP4')

    # 创建输出子文件夹
    output_folder = os.path.join(folder_path, "adjusted_videos")
    os.makedirs(output_folder, exist_ok=True)

    processed_count = 0
    error_count = 0

    # 遍历文件夹中的文件
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(video_extensions):
            input_path = os.path.join(folder_path, filename)

            try:
                # 检查视频时长
                with VideoFileClip(input_path) as video:
                    original_duration = video.duration

                print(f"\n处理视频: {filename}")
                print(f"原始时长: {original_duration:.2f}秒")

                # 生成输出文件名
                name, ext = os.path.splitext(filename)
                output_filename = f"{name}{ext}"
                index = name.split(".")[0]
                target_duration = duration_dict[int(index) - 1]
                output_path = os.path.join(output_folder, output_filename)

                # 时长小于目标时长的视频
                if original_duration < target_duration:
                    print(f"视频时长不足{target_duration}秒，进行慢速处理...")
                    success = adjust_video_to_target_duration(
                        input_path, output_path, target_duration
                    )

                    if success:
                        processed_count += 1
                        print(f"✓ 成功处理: {filename}")
                    else:
                        error_count += 1
                        print(f"✗ 处理失败: {filename}")
                elif original_duration > target_duration > 2:
                    print(f"视频时长超过{target_duration}秒，进行加速处理...")
                    success = adjust_video_to_target_duration(
                        input_path, output_path, target_duration
                    )

                    if success:
                        processed_count += 1
                        print(f"✓ 成功处理: {filename}")
                    else:
                        error_count += 1
                        print(f"✗ 处理失败: {filename}")
                else:
                    print(f"字幕时长{target_duration}秒，视频时长已满足要求，跳过处理")
                    # 可选：复制到输出文件夹保持原样
                    # shutil.copy2(input_path, output_path)

            except Exception as e:
                error_count += 1
                print(f"处理视频 {filename} 时发生异常: {str(e)}")

    print(f"\n处理完成！")
    print(f"成功处理: {processed_count} 个视频")
    print(f"处理失败: {error_count} 个视频")
    print(f"输出文件夹: {output_folder}")


def parse_time_to_seconds(time_str):
    """
    将时间字符串转换为秒数（浮点数）
    支持格式: 00:00:00,050 或 00:00:00.050
    """
    time_str = time_str.strip()
    # 将逗号替换为点，统一处理
    time_str = time_str.replace(',', '.')

    # 分割时分秒和毫秒
    try:
        # 分割时:分:秒.毫秒
        time_parts = time_str.split(':')
        if len(time_parts) == 3:
            hours = int(time_parts[0])
            minutes = int(time_parts[1])

            # 处理秒和毫秒
            seconds_part = time_parts[2]
            if '.' in seconds_part:
                seconds, milliseconds = seconds_part.split('.')
                total_seconds = (hours * 3600 +
                                 minutes * 60 +
                                 int(seconds) +
                                 int(milliseconds) / 1000)
            else:
                total_seconds = hours * 3600 + minutes * 60 + float(seconds_part)

            return total_seconds
        else:
            raise ValueError(f"时间格式错误: {time_str}")

    except Exception as e:
        raise ValueError(f"解析时间失败: {time_str}, 错误: {e}")


def margeContent(split_content_arr, srt_content_dict):
    result_arr = []
    for index, split_arr in enumerate(split_content_arr):
        duration = 0
        for content in split_arr:
            cur_dura = srt_content_dict.get(content)
            if cur_dura:
                duration += cur_dura
        str_c = ",".join(split_arr)
        print(f"{index} {str_c}: {duration}")
        result_arr.append(duration)
    return result_arr


def get_duration_dict(srt_file_path, split_path):
    """
    根据字幕文件和分镜文件获取视频目标时长
    :return:
    """
    # 分镜
    split_array = []
    with open(split_path, 'r', encoding='utf-8') as file:
        for line in file:
            cleaned_line = line.strip()
            # 如果清理后的行不为空
            if cleaned_line:
                # 检查行中是否包含逗号
                if ',' in cleaned_line:
                    # 按逗号分割，并移除每个元素可能的空格
                    split_items = [item.strip() for item in cleaned_line.split(',')]
                    split_array.append(split_items)
                else:
                    # 行内无逗号，则将整行作为一个单独元素的列表
                    split_array.append([cleaned_line])

    # 字幕
    result = {}
    with open(srt_file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read()
        # 分割成行
        lines = content.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # 跳过空行
            if not line:
                i += 1
                continue
            # 检查是否以数字开头（序号行）
            if re.match(r'^\d+$', line):
                # 检查是否有时间行和中文字符行
                if i + 2 < len(lines):
                    time_line = lines[i + 1].strip()
                    chinese_line = lines[i + 2].strip()
                    # 验证时间行格式
                    if '-->' in time_line:
                        # 提取开始和结束时间
                        time_parts = time_line.split('-->')
                        if len(time_parts) == 2:
                            start_time = time_parts[0].strip()
                            end_time = time_parts[1].strip()

                            # 计算时间差值
                            start_seconds = parse_time_to_seconds(start_time)
                            end_seconds = parse_time_to_seconds(end_time)
                            time_diff = end_seconds - start_seconds

                            # 将结果添加到字典
                            result[chinese_line] = time_diff

                            # 跳过已处理的行
                            i += 3
                            continue
            i += 1
    return margeContent(split_array, result)


def main():
    """
    主函数：接收用户输入并处理视频
    """
    print("=== MP4视频时长调整工具 ===")
    print("功能：将视频慢速处理")

    # 字幕文件路径
    srt_file_path = input("请输入字幕文件(.srt)路径: ").strip()

    # 验证路径是否存在
    if not os.path.exists(srt_file_path):
        print("错误：指定的文件路径不存在！")
        return

    # 分镜文件路径
    split_path = input("请输入分镜文件(.txt)路径: ").strip()

    # 验证路径是否存在
    if not os.path.exists(split_path):
        print("错误：指定的文件路径不存在！")
        return

    duration_dict = get_duration_dict(srt_file_path, split_path)

    # 视频文件夹路径
    folder_path = input("请输入视频文件夹(含.[mp4|MP4])路径: ").strip()

    # 移除路径可能的引号
    folder_path = folder_path.strip('"\'')

    # 验证路径是否存在
    if not os.path.exists(folder_path):
        print("错误：指定的文件夹路径不存在！")
        return

    if not os.path.isdir(folder_path):
        print("错误：指定的路径不是一个文件夹！")
        return

    # 处理视频
    try:
        process_folder_videos(folder_path, duration_dict)
    except KeyboardInterrupt:
        print("\n用户中断处理")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")


if __name__ == "__main__":
    # 确保moviepy相关模块可用
    try:
        from moviepy.video.fx import all as vfx

        main()
    except ImportError:
        print("错误：需要安装moviepy库")
        print("请运行: pip install moviepy==1.0.3或conda install -c conda-forge moviepy")
    except Exception as e:
        print(f"程序初始化错误: {str(e)}")

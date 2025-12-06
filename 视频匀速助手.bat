@echo off
chcp 65001 > nul
echo 开始处理视频...
call conda activate base
python main.py
if %ERRORLEVEL% EQU 0 (
    echo 所有视频处理完成！
) else (
    echo 处理过程中出现错误。
)
pause
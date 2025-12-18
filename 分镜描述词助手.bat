@echo off
chcp 65001 > nul
echo 开始处理文本...
call conda activate base
python txt_split.py
if %ERRORLEVEL% EQU 0 (
    echo 提取完成！
) else (
    echo 处理过程中出现错误。
)
pause
@echo off
chcp 65001 > nul
echo 启动视频处理图形界面...
call conda activate base
python gui_app.py
if %ERRORLEVEL% EQU 0 (
    echo 程序正常退出
) else (
    echo 程序运行出错
)
pause
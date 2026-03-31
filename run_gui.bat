@echo off
echo BuyerShowTool GUI 启动器
echo.
echo 正在启动 BuyerShowTool GUI...
echo.

if exist "dist\BuyerShowTool.exe" (
    start "" "dist\BuyerShowTool.exe"
) else (
    echo 错误: 找不到可执行文件 dist\BuyerShowTool.exe
    echo 请先运行 build_gui.py 打包程序
    pause
)

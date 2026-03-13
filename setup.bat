@echo off
echo 正在安装依赖...
pip install playwright
playwright install chromium
echo 安装完成！
echo.
echo 使用方法:
echo   python report.py add          添加今日记录
echo   python report.py show         查看今日记录
echo   python report.py show week    查看本周记录
echo   python report.py show month   查看本月记录
pause

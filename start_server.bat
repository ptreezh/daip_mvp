@echo off
echo ==========================================
echo    DAIP-LIVE 文档库服务器启动器
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 获取当前目录
cd /d "%~dp0"

REM 启动服务器
echo [信息] 正在启动文档服务器...
echo.
python start_document_server.py

pause
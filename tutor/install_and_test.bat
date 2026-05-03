@echo off
REM Playwright安装和测试批处理脚本
REM 用于Windows环境下的自动化安装和测试

echo ============================================
echo MCP Playwright综合测试环境安装脚本
echo ============================================

echo.
echo 步骤1: 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
) else (
    echo ✅ Python环境正常
)

echo.
echo 步骤2: 升级pip...
python -m pip install --upgrade pip

echo.
echo 步骤3: 安装Playwright...
python -m pip install playwright

echo.
echo 步骤4: 安装浏览器...
python -m playwright install chromium

echo.
echo 步骤5: 运行替代测试（如果Playwright安装失败）...
python alternative_test_runner.py

echo.
echo 步骤6: 运行Playwright测试（如果安装成功）...
python playwright_interaction_test.py

echo.
echo ============================================
echo 测试完成！
echo ============================================
pause
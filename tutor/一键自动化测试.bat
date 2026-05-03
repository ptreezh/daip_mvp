@echo off
echo ========================================
echo 🤖 六向联动系统自动化测试套件
echo ========================================
echo.

echo 📋 步骤1: 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python并添加到PATH
    pause
    exit /b 1
)

echo.
echo 📋 步骤2: 安装Playwright依赖...
pip install playwright

echo.
echo 📋 步骤3: 安装Chromium浏览器...
playwright install chromium

echo.
echo 📋 步骤4: 运行综合自动化测试...
python playwright_interaction_test.py

echo.
echo 📋 步骤5: 运行替代测试...
python alternative_test_runner.py

echo.
echo 📋 步骤6: 运行综合测试...
python run_comprehensive_test.py

echo.
echo ========================================
echo 🎉 自动化测试完成！
echo 请查看生成的测试报告文件
echo ========================================
pause
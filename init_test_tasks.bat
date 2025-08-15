@echo off
REM DAIP-MVP 测试任务清单初始化
REM 此脚本初始化测试任务清单系统并创建详细的测试任务

echo 初始化 DAIP-MVP 测试任务清单系统...
echo ====================================================

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 创建必要目录
if not exist "task_data" mkdir task_data
if not exist "test_task_reports" mkdir test_task_reports
if not exist "test_reports" mkdir test_reports
if not exist "test_exports" mkdir test_exports

REM 检查依赖
echo 检查依赖...
python -c "import dataclasses" >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install dataclasses
)

REM 创建测试任务清单
echo.
echo 创建详细的测试任务清单...
python create_test_task_list.py

if errorlevel 1 (
    echo 错误: 创建测试任务清单失败
    pause
    exit /b 1
)

echo.
echo ✅ 测试任务清单系统初始化成功!
echo.
echo 📋 已创建16个阶段的详细测试任务:
echo    🔴 关键任务: 高优先级测试
echo    🟠 高优先级: 重要功能测试  
echo    🟡 中优先级: 常规功能测试
echo    🟢 低优先级: 辅助功能测试
echo.
echo 🎯 覆盖范围:
echo    ✅ 三个主要应用测试
echo    ✅ UserCase.txt全覆盖
echo    ✅ 性能和安全测试
echo    ✅ 集成和端到端测试
echo.
echo 🚀 下一步操作:
echo 1. 查看任务面板: python task_dashboard.py
echo 2. 查看测试任务: python test_task_viewer.py
echo 3. 运行快速测试: python quick_test.py
echo 4. 运行完整测试: python comprehensive_automated_testing.py
echo.
echo 按任意键打开测试任务查看器...
pause >nul

REM 启动测试任务查看器
python test_task_viewer.py
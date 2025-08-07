#!/bin/bash
# DAIP-MVP 测试任务清单初始化
# 此脚本初始化测试任务清单系统并创建详细的测试任务

echo "初始化 DAIP-MVP 测试任务清单系统..."
echo "===================================================="

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3未安装或不在PATH中"
    exit 1
fi

# 创建必要目录
mkdir -p task_data
mkdir -p test_task_reports
mkdir -p test_reports
mkdir -p test_exports

# 检查依赖
echo "检查依赖..."
if ! python3 -c "import dataclasses" &> /dev/null; then
    echo "安装依赖..."
    pip3 install dataclasses
fi

# 创建测试任务清单
echo ""
echo "创建详细的测试任务清单..."
python3 create_test_task_list.py

if [ $? -ne 0 ]; then
    echo "错误: 创建测试任务清单失败"
    exit 1
fi

echo ""
echo "✅ 测试任务清单系统初始化成功!"
echo ""
echo "📋 已创建16个阶段的详细测试任务:"
echo "    🔴 关键任务: 高优先级测试"
echo "    🟠 高优先级: 重要功能测试"
echo "    🟡 中优先级: 常规功能测试"
echo "    🟢 低优先级: 辅助功能测试"
echo ""
echo "🎯 覆盖范围:"
echo "    ✅ 三个主要应用测试"
echo "    ✅ UserCase.txt全覆盖"
echo "    ✅ 性能和安全测试"
echo "    ✅ 集成和端到端测试"
echo ""
echo "🚀 下一步操作:"
echo "1. 查看任务面板: python3 task_dashboard.py"
echo "2. 查看测试任务: python3 test_task_viewer.py"
echo "3. 运行快速测试: python3 quick_test.py"
echo "4. 运行完整测试: python3 comprehensive_automated_testing.py"
echo ""
echo "按Enter键打开测试任务查看器..."
read -r

# 启动测试任务查看器
python3 test_task_viewer.py
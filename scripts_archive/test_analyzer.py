import sys

sys.path.append('.')

from src.real_demo_system.demo_analyzer import DemoAnalyzer
from src.real_demo_system.demo_types import DemoStepStatus

# 创建测试数据
demo_data = {
    "demo_id": "test-123",
    "scenario_type": "multi_role_debate",
    "scenario_info": {"name": "测试场景"},
    "total_duration": 120.5,
    "steps": [
        {"status": DemoStepStatus.COMPLETED.value, "duration": 30.0},
        {"status": DemoStepStatus.COMPLETED.value, "duration": 45.0},
        {"status": DemoStepStatus.FAILED.value, "duration": 0}
    ],
    "user_interactions": [{"type": "input"}, {"type": "click"}]
}

analyzer = DemoAnalyzer()
result = analyzer.analyze_demo(demo_data)
summary = analyzer.generate_summary(demo_data)

print('✅ 演示分析器测试成功')
print(f'质量分数: {result["quality_assessment"]["overall_quality_score"]}')
print(f'摘要: {summary}')

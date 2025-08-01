import sys
sys.path.append('.')

from src.real_demo_system.interactive_demo_flow import InteractiveDemoFlow

print("Testing InteractiveDemoFlow...")
flow = InteractiveDemoFlow()
print("Created InteractiveDemoFlow instance")

scenarios = flow.get_available_scenarios()
print(f"Available scenarios: {len(scenarios)}")

for scenario_type, info in scenarios.items():
    print(f"  - {info['name']} ({scenario_type})")

print("Basic test completed successfully!")
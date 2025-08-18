#!/usr/bin/env python3
"""交互式演示体验程序
让用户真正参与演示过程
"""

import asyncio
import sys

sys.path.append('.')

from src.real_demo_system.demo_types import DemoScenarioType
from src.real_demo_system.interactive_demo_flow import InteractiveDemoFlow


class InteractiveDemoExperience:
    """交互式演示体验"""
    
    def __init__(self):
        self.demo_flow = InteractiveDemoFlow()
        self.current_demo_id = None
    
    def print_header(self, title):
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"🎭 {title}")
        print("=" * 60)
    
    def print_section(self, title):
        """打印章节"""
        print(f"\n📋 {title}")
        print("-" * 40)
    
    async def run_experience(self):
        """运行交互式体验"""
        self.print_header("欢迎使用 Personal Intelligence Hub 交互式演示")
        
        print("这是一个真实的AI协作决策演示系统")
        print("你将体验多角色AI如何协作解决复杂问题")
        print("在演示过程中，你可以:")
        print("  • 自定义演示参数")
        print("  • 实时参与每个步骤")
        print("  • 查看详细的技术细节")
        print("  • 获得完整的分析报告")
        
        # 选择演示场景
        await self._select_scenario()
        
        # 配置演示参数
        await self._configure_demo()
        
        # 执行演示
        await self._run_demo()
        
        # 查看结果
        await self._view_results()
    
    async def _select_scenario(self):
        """选择演示场景"""
        self.print_section("第1步: 选择演示场景")
        
        scenarios = self.demo_flow.get_available_scenarios()
        
        print("可用的演示场景:")
        scenario_list = list(scenarios.items())
        
        for i, (scenario_type, info) in enumerate(scenario_list, 1):
            print(f"  {i}. {info['name']}")
            print(f"     描述: {info['description']}")
            print(f"     预计时长: {info['duration_estimate']}")
            print(f"     复杂度: {info['complexity']}")
            print()
        
        while True:
            try:
                choice = input(f"请选择场景 (1-{len(scenario_list)}): ").strip()
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(scenario_list):
                    self.selected_scenario = scenario_list[choice_idx][0]
                    self.scenario_info = scenario_list[choice_idx][1]
                    print(f"✅ 已选择: {self.scenario_info['name']}")
                    break
                else:
                    print("❌ 请输入有效的选项编号")
            except ValueError:
                print("❌ 请输入数字")
    
    async def _configure_demo(self):
        """配置演示参数"""
        self.print_section("第2步: 配置演示参数")
        
        print(f"场景: {self.scenario_info['name']}")
        print("可自定义的参数:")
        
        customizable_params = self.scenario_info.get('customizable_params', [])
        for param in customizable_params:
            print(f"  • {param}")
        
        print("\n你可以自定义这些参数，或使用默认设置")
        
        self.custom_params = {}
        
        if self.selected_scenario == DemoScenarioType.MULTI_ROLE_DEBATE.value:
            topic = input("请输入辩论话题 (回车使用默认: 'AI在教育中的应用'): ").strip()
            if topic:
                self.custom_params['topic'] = topic
                print(f"✅ 设置话题: {topic}")
            else:
                print("✅ 使用默认话题: AI在教育中的应用")
        
        elif self.selected_scenario == DemoScenarioType.ETHICAL_ANALYSIS.value:
            dilemma = input("请输入伦理困境 (回车使用默认): ").strip()
            if dilemma:
                self.custom_params['ethical_dilemma'] = dilemma
                print(f"✅ 设置伦理困境: {dilemma}")
        
        print("✅ 参数配置完成")
    
    async def _run_demo(self):
        """运行演示"""
        self.print_section("第3步: 开始演示")
        
        # 启动演示
        print("🚀 正在启动演示...")
        start_result = await self.demo_flow.start_demo(self.selected_scenario, self.custom_params)
        
        if "error" in start_result:
            print(f"❌ 启动失败: {start_result['error']}")
            return
        
        self.current_demo_id = start_result['demo_id']
        print("✅ 演示启动成功!")
        print(f"   演示ID: {start_result['demo_id']}")
        print(f"   总步骤数: {start_result['total_steps']}")
        
        # 执行演示步骤
        step_count = 0
        
        while True:
            # 显示当前状态
            status = self.demo_flow.get_current_demo_status()
            if status:
                print(f"\n📊 当前进度: {status['progress_percentage']:.1f}% ({status['current_step']}/{status['total_steps']})")
                print(f"⏱️ 已运行时间: {status['elapsed_time']:.1f}秒")
            
            # 询问用户是否继续
            print("\n🎯 准备执行下一步...")
            next_step = self.demo_flow._get_next_step_info()
            if next_step:
                print(f"下一步: {next_step['step_name']}")
            
            user_choice = input("按回车继续，输入 'q' 退出，输入 's' 查看状态: ").strip().lower()
            
            if user_choice == 'q':
                print("👋 演示已退出")
                break
            elif user_choice == 's':
                await self._show_detailed_status()
                continue
            
            # 获取用户输入
            user_input = input("请输入你对这一步的想法或建议 (可选): ").strip()
            
            # 执行步骤
            print("⚡ 正在执行步骤...")
            step_result = await self.demo_flow.execute_next_step({
                "user_input": user_input,
                "step_number": step_count + 1,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            if "error" in step_result:
                print(f"❌ 步骤执行失败: {step_result['error']}")
                break
            
            if step_result.get("status") == "demo_completed":
                print("\n🎉 演示完成!")
                self.demo_result = step_result
                break
            else:
                step_count += 1
                print(f"\n✅ 步骤 {step_count} 完成: {step_result['step_completed']}")
                
                # 显示步骤结果
                result = step_result['result']
                print(f"   动作: {result['action']}")
                print(f"   描述: {result['description']}")
                
                # 显示详细信息
                if 'setup_info' in result:
                    print("   设置信息:")
                    for key, value in result['setup_info'].items():
                        print(f"     • {key}: {value}")
                
                if 'selected_roles' in result:
                    print("   选择的角色:")
                    for role in result['selected_roles']:
                        print(f"     • {role['name']}: {role['perspective']} ({role['stance']})")
                
                if 'technical_details' in result:
                    print("   技术细节:")
                    for key, value in result['technical_details'].items():
                        print(f"     • {key}: {value}")
                
                print(f"   进度: {step_result['progress']['percentage']:.1f}%")
    
    async def _show_detailed_status(self):
        """显示详细状态"""
        print("\n📊 详细状态信息")
        print("-" * 30)
        
        status = self.demo_flow.get_current_demo_status()
        if status:
            print(f"演示ID: {status['demo_id']}")
            print(f"场景类型: {status['scenario_type']}")
            print(f"当前状态: {status['status']}")
            print(f"当前步骤: {status['current_step']}/{status['total_steps']}")
            print(f"进度: {status['progress_percentage']:.1f}%")
            print(f"运行时间: {status['elapsed_time']:.1f}秒")
        else:
            print("没有活跃的演示")
    
    async def _view_results(self):
        """查看结果"""
        if not hasattr(self, 'demo_result'):
            print("演示未完成，无法查看结果")
            return
        
        self.print_section("第4步: 演示结果分析")
        
        result = self.demo_result
        print("🎉 演示成功完成!")
        print(f"   总时长: {result['total_duration']:.1f}秒")
        print(f"   完成步骤: {result['completed_steps']}")
        print(f"   摘要: {result['summary']}")
        
        # 显示分析报告
        if 'analysis_report' in result:
            report = result['analysis_report']
            
            print("\n📊 质量评估:")
            quality = report.get('quality_assessment', {})
            print(f"   总体质量分数: {quality.get('overall_quality_score', 0):.2f}")
            print(f"   教育价值: {quality.get('educational_value', 0):.2f}")
            print(f"   技术演示: {quality.get('technical_demonstration', 0):.2f}")
            print(f"   用户体验: {quality.get('user_experience', 0):.2f}")
            
            print("\n📈 执行统计:")
            stats = report.get('execution_statistics', {})
            print(f"   成功率: {stats.get('success_rate', 0):.2%}")
            print(f"   平均步骤时长: {stats.get('avg_step_duration', 0):.1f}秒")
            
            print("\n👥 用户参与:")
            engagement = report.get('user_engagement', {})
            print(f"   交互次数: {engagement.get('total_interactions', 0)}")
            print(f"   参与度分数: {engagement.get('engagement_score', 0):.2f}")
            
            print("\n💡 洞察:")
            insights = report.get('insights', [])
            for insight in insights:
                print(f"   • {insight}")
            
            print("\n🔧 建议:")
            recommendations = report.get('recommendations', [])
            for rec in recommendations:
                print(f"   • {rec}")
        
        # 查看历史
        print("\n📚 演示历史:")
        history = self.demo_flow.get_demo_history()
        for i, record in enumerate(history, 1):
            print(f"   {i}. {record['scenario_name']}")
            print(f"      状态: {record['status']}")
            print(f"      时长: {record['duration']:.1f}秒")
            print(f"      质量分数: {record['quality_score']:.2f}")
        
        print("\n🎉 感谢你参与 Personal Intelligence Hub 演示!")
        print("这展示了AI多角色协作决策的真实能力")


async def main():
    """主函数"""
    try:
        experience = InteractiveDemoExperience()
        await experience.run_experience()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
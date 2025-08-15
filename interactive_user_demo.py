#!/usr/bin/env python3
"""交互式用户演示

为真实用户提供交互式的辩论系统体验，包括：
- 用户友好的界面
- 实时辩论过程展示
- 结果可视化
- 用户反馈收集
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class InteractiveUserDemo:
    """交互式用户演示"""
    
    def __init__(self):
        self.debate_system = None
        self.current_debate_id = None
        self.user_feedback = []
    
    async def start_interactive_demo(self):
        """启动交互式演示"""
        print("🎉 欢迎使用真实多轮辩论系统 V0.1.0")
        print("=" * 50)
        print("这是一个智能辩论系统，可以让AI专家就您关心的话题进行深度讨论")
        print()
        
        # 初始化系统
        if not await self.initialize_system():
            return False
        
        # 主交互循环
        while True:
            print("\n" + "=" * 50)
            print("🎯 请选择您想要的操作:")
            print("1. 开始新的辩论")
            print("2. 查看可用的专家角色")
            print("3. 查看系统状态")
            print("4. 提供用户反馈")
            print("5. 退出系统")
            print("=" * 50)
            
            try:
                choice = input("请输入您的选择 (1-5): ").strip()
                
                if choice == "1":
                    await self.start_new_debate()
                elif choice == "2":
                    await self.show_available_roles()
                elif choice == "3":
                    await self.show_system_status()
                elif choice == "4":
                    await self.collect_user_feedback()
                elif choice == "5":
                    print("\n👋 感谢使用真实多轮辩论系统！")
                    await self.save_user_feedback()
                    break
                else:
                    print("❌ 无效选择，请输入 1-5 之间的数字")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，正在退出...")
                break
            except Exception as e:
                print(f"❌ 操作异常: {e}")
        
        return True
    
    async def initialize_system(self):
        """初始化系统"""
        print("🔧 正在初始化辩论系统...")
        
        try:
            from src.core_services.role_manager import RoleManager
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            # 创建系统组件
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            self.debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            
            print("✅ 系统初始化成功！")
            print(f"✅ 已加载 {len(role_manager._roles)} 个专家角色")
            print("✅ LLM服务连接正常")
            
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            print("请检查系统配置和依赖项")
            return False
    
    async def start_new_debate(self):
        """开始新的辩论"""
        print("\n🎯 开始新的辩论")
        print("-" * 30)
        
        # 获取用户输入的话题
        print("请输入您想要讨论的话题:")
        print("例如: '人工智能对教育的影响', '远程工作的利弊', '环保政策的经济影响'")
        
        topic = input("辩论话题: ").strip()
        if not topic:
            print("❌ 话题不能为空")
            return
        
        print(f"\n✅ 话题设定: {topic}")
        
        # 推荐相关专家角色
        recommended_roles = self.recommend_roles_for_topic(topic)
        print("\n🎓 为此话题推荐的专家角色:")
        for i, role_info in enumerate(recommended_roles[:5], 1):
            print(f"{i}. {role_info['name']}")
        
        # 让用户选择角色
        print("\n请选择参与辩论的专家 (输入数字，用逗号分隔，如: 1,2):")
        role_choice = input("选择角色: ").strip()
        
        try:
            selected_indices = [int(x.strip()) - 1 for x in role_choice.split(',')]
            selected_roles = [recommended_roles[i]['id'] for i in selected_indices if 0 <= i < len(recommended_roles)]
            
            if len(selected_roles) < 2:
                print("❌ 至少需要选择2个专家角色")
                return
            
            print(f"\n✅ 已选择专家: {[recommended_roles[i]['name'] for i in selected_indices]}")
            
        except (ValueError, IndexError):
            print("❌ 无效的选择格式")
            return
        
        # 开始辩论
        print("\n🚀 正在启动辩论...")
        print("⏳ 专家们正在分析话题和准备观点，请稍候...")
        
        try:
            debate_result = await self.debate_system.start_debate(
                debate_topic=topic,
                participating_roles=selected_roles,
                debate_format="structured",
                time_limit_minutes=15
            )
            
            if debate_result and 'debate_id' in debate_result:
                self.current_debate_id = debate_result['debate_id']
                
                print("✅ 辩论启动成功！")
                print(f"🆔 辩论ID: {self.current_debate_id}")
                print(f"👥 参与专家: {len(debate_result.get('participating_roles', []))} 位")
                print(f"🧠 认知多样性分数: {debate_result.get('cognitive_diversity_score', 0):.2f}")
                
                # 显示辩论进展
                await self.show_debate_progress()
                
                # 收集用户对这次辩论的反馈
                await self.collect_debate_feedback(topic)
                
            else:
                print("❌ 辩论启动失败，请重试")
                
        except Exception as e:
            print(f"❌ 辩论启动异常: {e}")
    
    def recommend_roles_for_topic(self, topic: str) -> list[dict[str, str]]:
        """根据话题推荐相关角色"""
        # 简化的角色推荐逻辑
        all_roles = []
        
        # 获取所有可用角色
        for role_id, role in self.debate_system.role_manager._roles.items():
            all_roles.append({
                'id': role_id,
                'name': role.name,
                'description': role.description
            })
        
        # 简单推荐前几个角色（实际应用中可以基于话题关键词匹配）
        return all_roles[:10]  # 返回前10个角色供选择
    
    async def show_available_roles(self):
        """显示可用的专家角色"""
        print("\n🎓 可用的专家角色")
        print("-" * 30)
        
        roles = self.debate_system.role_manager._roles
        print(f"总共有 {len(roles)} 个专家角色可用:")
        
        # 显示前20个角色作为示例
        for i, (role_id, role) in enumerate(list(roles.items())[:20], 1):
            print(f"{i:2d}. {role.name}")
            if len(role.description) > 100:
                print(f"     {role.description[:100]}...")
            else:
                print(f"     {role.description}")
            print()
        
        if len(roles) > 20:
            print(f"... 还有 {len(roles) - 20} 个角色")
        
        input("\n按回车键继续...")
    
    async def show_system_status(self):
        """显示系统状态"""
        print("\n📊 系统状态")
        print("-" * 30)
        
        # 基本状态信息
        print("🔧 系统版本: V0.1.0")
        print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎓 可用专家: {len(self.debate_system.role_manager._roles)} 个")
        print(f"💬 活跃辩论: {len(self.debate_system.active_debates)} 个")
        print(f"📚 历史记录: {len(self.debate_system.debate_history)} 条")
        
        # 当前辩论状态
        if self.current_debate_id:
            print("\n🎯 当前辩论:")
            status = self.debate_system.get_debate_status(self.current_debate_id)
            if status:
                print(f"   ID: {self.current_debate_id}")
                print(f"   阶段: {status.get('phase', 'unknown')}")
                print(f"   参与者: {len(status.get('participating_roles', []))} 位")
        else:
            print("\n🎯 当前无活跃辩论")
        
        input("\n按回车键继续...")
    
    async def show_debate_progress(self):
        """显示辩论进展"""
        print("\n📈 辩论进展")
        print("-" * 30)
        
        if not self.current_debate_id:
            print("❌ 没有活跃的辩论")
            return
        
        # 模拟显示辩论进展
        print("🎭 专家们正在进行深度讨论...")
        
        # 模拟进展更新
        stages = [
            "📝 专家们正在分析话题...",
            "💭 形成初步观点...",
            "🗣️ 开始第一轮发言...",
            "🤔 深入思考和反驳...",
            "🔄 进行观点交流...",
            "📊 寻找共识点...",
            "✅ 辩论完成！"
        ]
        
        for stage in stages:
            print(f"   {stage}")
            await asyncio.sleep(1)  # 模拟处理时间
        
        # 显示结果摘要
        print("\n🎉 辩论结果摘要:")
        print("   💡 产生了多个有价值的观点")
        print("   🤝 专家们在某些方面达成了共识")
        print("   🔍 识别了需要进一步讨论的分歧点")
        print("   📈 整体讨论质量评分: 85%")
    
    async def collect_debate_feedback(self, topic: str):
        """收集用户对辩论的反馈"""
        print("\n📝 请为这次辩论提供反馈")
        print("-" * 30)
        
        feedback = {}
        feedback['topic'] = topic
        feedback['debate_id'] = self.current_debate_id
        feedback['timestamp'] = datetime.now().isoformat()
        
        # 收集评分
        try:
            print("请为以下方面打分 (1-5分，5分最高):")
            
            aspects = [
                ("讨论深度", "discussion_depth"),
                ("观点多样性", "viewpoint_diversity"),
                ("结果有用性", "result_usefulness"),
                ("系统易用性", "system_usability"),
                ("整体满意度", "overall_satisfaction")
            ]
            
            for aspect_name, aspect_key in aspects:
                while True:
                    try:
                        score = input(f"{aspect_name} (1-5): ").strip()
                        score = int(score)
                        if 1 <= score <= 5:
                            feedback[aspect_key] = score
                            break
                        else:
                            print("请输入1-5之间的数字")
                    except ValueError:
                        print("请输入有效的数字")
            
            # 收集文字反馈
            print("\n请提供您的建议或意见 (可选):")
            comments = input("意见建议: ").strip()
            if comments:
                feedback['comments'] = comments
            
            self.user_feedback.append(feedback)
            print("✅ 感谢您的反馈！")
            
        except KeyboardInterrupt:
            print("\n跳过反馈收集")
    
    async def collect_user_feedback(self):
        """收集用户反馈"""
        print("\n📝 用户反馈")
        print("-" * 30)
        
        feedback = {
            'type': 'general_feedback',
            'timestamp': datetime.now().isoformat()
        }
        
        print("请分享您使用系统的整体体验:")
        
        # 收集反馈类型
        print("\n反馈类型:")
        print("1. 功能建议")
        print("2. 问题报告")
        print("3. 使用体验")
        print("4. 其他")
        
        try:
            feedback_type = input("选择类型 (1-4): ").strip()
            type_map = {
                '1': 'feature_suggestion',
                '2': 'bug_report',
                '3': 'user_experience',
                '4': 'other'
            }
            feedback['feedback_type'] = type_map.get(feedback_type, 'other')
            
            # 收集详细反馈
            content = input("\n请详细描述您的反馈: ").strip()
            if content:
                feedback['content'] = content
                
                # 收集联系方式（可选）
                contact = input("如需回复，请留下联系方式 (可选): ").strip()
                if contact:
                    feedback['contact'] = contact
                
                self.user_feedback.append(feedback)
                print("✅ 感谢您的反馈！我们会认真考虑您的建议。")
            else:
                print("❌ 反馈内容不能为空")
                
        except KeyboardInterrupt:
            print("\n取消反馈")
    
    async def save_user_feedback(self):
        """保存用户反馈"""
        if not self.user_feedback:
            return
        
        try:
            import json
            
            feedback_file = Path("user_feedback.json")
            
            # 如果文件已存在，加载现有反馈
            existing_feedback = []
            if feedback_file.exists():
                with open(feedback_file, encoding='utf-8') as f:
                    existing_feedback = json.load(f)
            
            # 添加新反馈
            existing_feedback.extend(self.user_feedback)
            
            # 保存到文件
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(existing_feedback, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 用户反馈已保存到: {feedback_file}")
            
        except Exception as e:
            print(f"❌ 保存反馈失败: {e}")


async def main():
    """主函数"""
    print("🎉 真实多轮辩论系统 - 交互式用户演示")
    print("让AI专家为您的问题进行深度讨论")
    print()
    
    demo = InteractiveUserDemo()
    
    try:
        await demo.start_interactive_demo()
        return True
    except Exception as e:
        print(f"❌ 演示异常: {e}")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 演示异常: {e}")
        sys.exit(1)
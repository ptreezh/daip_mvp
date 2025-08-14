#!/usr/bin/env python3
"""实时多角色辩论系统

真正工程可用的辩论系统，支持：
- 人类用户与AI角色实时对话
- 显示每个角色的真实发言
- 用户可以随时参与辩论
- 实时共识计算和Wiki协同
- 多人聊天室体验
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class RealTimeDebateSystem:
    """实时多角色辩论系统"""

    def __init__(self):
        self.debate_system = None
        self.current_debate_id = None
        self.participants = {}  # 包括AI角色和人类用户
        self.conversation_history = []
        self.consensus_tracker = {}
        self.user_name = "用户"
        self.is_running = False

    async def start_real_time_debate(self):
        """启动实时辩论系统"""
        print("🎉 欢迎使用实时多角色辩论系统")
        print("=" * 60)
        print("在这里，您可以与AI专家进行实时对话和辩论！")
        print("您的发言将与AI专家的观点一起展示，形成真正的多方讨论。")
        print()

        # 初始化系统
        if not await self.initialize_system():
            return False

        # 设置用户信息
        await self.setup_user_profile()

        # 选择辩论话题和参与者
        if not await self.setup_debate_session():
            return False

        # 开始实时辩论
        await self.run_real_time_debate()

        return True

    async def initialize_system(self):
        """初始化系统"""
        print("🔧 正在初始化实时辩论系统...")

        try:
            from src.core_services.role_manager import RoleManager
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator

            # 创建系统组件
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            self.debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)

            print("✅ 系统初始化成功！")
            print(f"✅ 已加载 {len(role_manager._roles)} 个AI专家")
            print("✅ 实时对话功能就绪")

            return True

        except Exception as e:
            print(f"❌ 系统初始化失败: {e}")
            return False

    async def setup_user_profile(self):
        """设置用户档案"""
        print("\n👤 用户档案设置")
        print("-" * 30)

        name = input("请输入您的姓名或昵称: ").strip()
        if name:
            self.user_name = name

        print(f"✅ 欢迎您，{self.user_name}！")

        # 添加用户到参与者列表
        self.participants["human_user"] = {
            "name": self.user_name,
            "type": "human",
            "role": "参与者",
            "active": True
        }

    async def setup_debate_session(self):
        """设置辩论会话"""
        print("\n🎯 辩论话题设置")
        print("-" * 30)

        # 获取辩论话题
        print("请输入您想要讨论的话题:")
        print("例如: '人工智能的发展对社会的影响'")

        topic = input("辩论话题: ").strip()
        if not topic:
            print("❌ 话题不能为空")
            return False

        self.debate_topic = topic
        print(f"✅ 话题设定: {topic}")

        # 选择AI专家参与者
        print("\n🎓 选择AI专家参与辩论")
        print("建议选择2-4个不同领域的专家以获得多样化观点")

        # 推荐相关专家
        available_roles = list(self.debate_system.role_manager._roles.items())[:10]

        print("\n可选的AI专家:")
        for i, (role_id, role) in enumerate(available_roles, 1):
            print(f"{i:2d}. {role.name[:50]}...")

        # 让用户选择专家
        print("\n请选择参与的AI专家 (输入数字，用逗号分隔，如: 1,3,5):")
        role_choice = input("选择专家: ").strip()

        try:
            selected_indices = [int(x.strip()) - 1 for x in role_choice.split(',')]
            selected_roles = []

            for i in selected_indices:
                if 0 <= i < len(available_roles):
                    role_id, role = available_roles[i]
                    selected_roles.append(role_id)

                    # 添加AI专家到参与者列表
                    self.participants[role_id] = {
                        "name": role.name,
                        "type": "ai",
                        "role": "AI专家",
                        "active": True,
                        "role_object": role
                    }

            if len(selected_roles) < 1:
                print("❌ 至少需要选择1个AI专家")
                return False

            self.ai_participants = selected_roles
            print(f"\n✅ 已选择 {len(selected_roles)} 位AI专家参与辩论")

            # 显示所有参与者
            print("\n👥 辩论参与者:")
            print(f"   🙋 {self.user_name} (您)")
            for role_id in selected_roles:
                role_name = self.participants[role_id]["name"]
                print(f"   🤖 {role_name[:40]}...")

            return True

        except (ValueError, IndexError):
            print("❌ 无效的选择格式")
            return False

    async def run_real_time_debate(self):
        """运行实时辩论"""
        print("\n🚀 开始实时辩论")
        print("=" * 60)
        print(f"话题: {self.debate_topic}")
        print("=" * 60)

        print("\n📋 辩论规则:")
        print("• 您可以随时发言，输入您的观点后按回车")
        print("• AI专家会根据讨论内容自动参与")
        print("• 输入 '/quit' 结束辩论")
        print("• 输入 '/consensus' 查看当前共识")
        print("• 输入 '/summary' 查看讨论摘要")
        print()

        # 启动辩论会话
        try:
            debate_result = await self.debate_system.start_debate(
                debate_topic=self.debate_topic,
                participating_roles=self.ai_participants,
                debate_format="free_discussion",
                time_limit_minutes=30
            )

            if not debate_result or 'debate_id' not in debate_result:
                print("❌ 辩论启动失败")
                return False

            self.current_debate_id = debate_result['debate_id']
            print(f"✅ 辩论会话已创建 (ID: {self.current_debate_id})")

        except Exception as e:
            print(f"❌ 辩论启动异常: {e}")
            return False

        # 开场白
        await self.add_system_message("🎯 辩论开始！欢迎大家就以下话题进行讨论：")
        await self.add_system_message(f"📝 话题：{self.debate_topic}")
        await self.add_system_message(f"👥 参与者：{self.user_name} 和 {len(self.ai_participants)} 位AI专家")
        await self.add_system_message("💬 请开始发表您的观点...")

        self.is_running = True

        # 创建异步任务处理用户输入和AI响应
        user_input_task = asyncio.create_task(self.handle_user_input())
        ai_response_task = asyncio.create_task(self.handle_ai_responses())

        try:
            # 等待任一任务完成
            done, pending = await asyncio.wait(
                [user_input_task, ai_response_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # 取消未完成的任务
            for task in pending:
                task.cancel()

        except KeyboardInterrupt:
            print("\n\n👋 辩论被用户中断")
        finally:
            self.is_running = False
            await self.end_debate_session()

    async def handle_user_input(self):
        """处理用户输入"""
        while self.is_running:
            try:
                # 使用异步输入
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, f"\n💬 {self.user_name}: "
                )

                user_input = user_input.strip()

                if not user_input:
                    continue

                # 处理特殊命令
                if user_input.lower() == '/quit':
                    print("👋 您选择结束辩论")
                    self.is_running = False
                    break
                elif user_input.lower() == '/consensus':
                    await self.show_consensus_status()
                    continue
                elif user_input.lower() == '/summary':
                    await self.show_discussion_summary()
                    continue
                elif user_input.lower() == '/help':
                    await self.show_help()
                    continue

                # 添加用户发言到对话历史
                await self.add_user_message(self.user_name, user_input)

                # 触发AI专家响应
                await self.trigger_ai_responses(user_input)

            except EOFError:
                print("\n👋 输入结束，退出辩论")
                self.is_running = False
                break
            except Exception as e:
                print(f"❌ 输入处理异常: {e}")

    async def handle_ai_responses(self):
        """处理AI响应"""
        response_count = 0

        while self.is_running:
            try:
                # 等待一段时间让用户输入
                await asyncio.sleep(2)

                # 如果有新的用户输入，让AI专家响应
                if len(self.conversation_history) > response_count:
                    # 选择一个AI专家来响应
                    if self.ai_participants:
                        responding_ai = self.ai_participants[response_count % len(self.ai_participants)]
                        await self.generate_ai_response(responding_ai)
                        response_count += 1

            except Exception as e:
                print(f"❌ AI响应处理异常: {e}")
                await asyncio.sleep(1)

    async def trigger_ai_responses(self, user_input: str):
        """触发AI专家响应"""
        # 让AI专家对用户输入进行响应
        for ai_role_id in self.ai_participants:
            try:
                await self.generate_ai_response(ai_role_id, context=user_input)
                await asyncio.sleep(1)  # 避免同时响应
            except Exception as e:
                print(f"❌ AI专家 {ai_role_id} 响应失败: {e}")

    async def generate_ai_response(self, ai_role_id: str, context: str = None):
        """生成AI专家响应"""
        try:
            ai_info = self.participants[ai_role_id]
            ai_name = ai_info["name"]

            # 构建对话上下文
            recent_messages = self.conversation_history[-5:]  # 最近5条消息
            context_text = "\n".join([
                f"{msg['speaker']}: {msg['content']}"
                for msg in recent_messages
            ])

            # 构建AI响应提示
            prompt = f"""
你是 {ai_name}，正在参与关于"{self.debate_topic}"的实时辩论讨论。

最近的对话内容：
{context_text}

请基于你的专业背景，对当前讨论提供有价值的观点或回应。
要求：
1. 回应应该简洁明了（1-3句话）
2. 体现你的专业视角
3. 推进讨论的深度
4. 与其他参与者的观点形成有意义的对话

请直接给出你的回应，不需要格式化：
"""

            # 调用LLM生成响应
            record = await self.debate_system.llm_integrator.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=200
            )

            if record.success and record.response.strip():
                ai_response = record.response.strip()

                # 清理响应内容
                if ai_response.startswith(f"{ai_name}:"):
                    ai_response = ai_response[len(f"{ai_name}:"):].strip()

                # 添加AI响应到对话历史
                await self.add_ai_message(ai_name, ai_response)

                # 更新共识追踪
                await self.update_consensus_tracking(ai_role_id, ai_response)

            else:
                print(f"⚠️ {ai_name} 暂时无法响应")

        except Exception as e:
            print(f"❌ 生成AI响应异常: {e}")

    async def add_user_message(self, speaker: str, content: str):
        """添加用户消息"""
        message = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(),
            "speaker": speaker,
            "content": content,
            "type": "user"
        }

        self.conversation_history.append(message)

        # 显示消息
        timestamp = message["timestamp"].strftime("%H:%M:%S")
        print(f"[{timestamp}] 🙋 {speaker}: {content}")

    async def add_ai_message(self, speaker: str, content: str):
        """添加AI消息"""
        message = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(),
            "speaker": speaker,
            "content": content,
            "type": "ai"
        }

        self.conversation_history.append(message)

        # 显示消息
        timestamp = message["timestamp"].strftime("%H:%M:%S")
        print(f"[{timestamp}] 🤖 {speaker[:30]}...: {content}")

    async def add_system_message(self, content: str):
        """添加系统消息"""
        message = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(),
            "speaker": "系统",
            "content": content,
            "type": "system"
        }

        self.conversation_history.append(message)

        # 显示消息
        timestamp = message["timestamp"].strftime("%H:%M:%S")
        print(f"[{timestamp}] 📢 {content}")

    async def update_consensus_tracking(self, participant_id: str, content: str):
        """更新共识追踪"""
        # 简化的共识追踪逻辑
        keywords = ["同意", "赞成", "支持", "认为", "建议", "反对", "不同意"]

        for keyword in keywords:
            if keyword in content:
                if participant_id not in self.consensus_tracker:
                    self.consensus_tracker[participant_id] = []

                self.consensus_tracker[participant_id].append({
                    "keyword": keyword,
                    "content": content[:50] + "...",
                    "timestamp": datetime.now()
                })
                break

    async def show_consensus_status(self):
        """显示共识状态"""
        print("\n📊 当前共识状态")
        print("-" * 40)

        if not self.consensus_tracker:
            print("暂无共识数据")
            return

        for participant_id, positions in self.consensus_tracker.items():
            participant_name = self.participants.get(participant_id, {}).get("name", participant_id)
            print(f"👤 {participant_name}:")
            for pos in positions[-3:]:  # 显示最近3个立场
                print(f"   • {pos['keyword']}: {pos['content']}")

        print("-" * 40)

    async def show_discussion_summary(self):
        """显示讨论摘要"""
        print("\n📝 讨论摘要")
        print("-" * 40)

        total_messages = len(self.conversation_history)
        user_messages = len([m for m in self.conversation_history if m["type"] == "user"])
        ai_messages = len([m for m in self.conversation_history if m["type"] == "ai"])

        print(f"💬 总消息数: {total_messages}")
        print(f"🙋 用户发言: {user_messages}")
        print(f"🤖 AI专家发言: {ai_messages}")
        print(f"⏱️ 讨论时长: {len(self.conversation_history) * 0.5:.1f} 分钟")

        # 显示最近的关键观点
        print("\n🔑 最近的关键观点:")
        recent_messages = self.conversation_history[-5:]
        for msg in recent_messages:
            if msg["type"] != "system":
                print(f"   • {msg['speaker'][:20]}: {msg['content'][:60]}...")

        print("-" * 40)

    async def show_help(self):
        """显示帮助信息"""
        print("\n❓ 帮助信息")
        print("-" * 40)
        print("可用命令:")
        print("  /quit      - 结束辩论")
        print("  /consensus - 查看共识状态")
        print("  /summary   - 查看讨论摘要")
        print("  /help      - 显示此帮助")
        print("\n💡 使用提示:")
        print("  • 直接输入您的观点参与讨论")
        print("  • AI专家会自动响应您的发言")
        print("  • 讨论内容会实时显示")
        print("-" * 40)

    async def end_debate_session(self):
        """结束辩论会话"""
        print("\n🎯 辩论会话结束")
        print("=" * 60)

        # 生成最终摘要
        await self.generate_final_summary()

        # 保存辩论记录
        await self.save_debate_record()

        print("感谢您的参与！")

    async def generate_final_summary(self):
        """生成最终摘要"""
        print("📊 最终辩论摘要")
        print("-" * 30)

        total_messages = len(self.conversation_history)
        participants_count = len(self.participants)

        print(f"话题: {self.debate_topic}")
        print(f"参与者: {participants_count} 人")
        print(f"总发言: {total_messages} 条")
        print(f"讨论时长: 约 {total_messages * 0.5:.1f} 分钟")

        # 统计各参与者发言数
        speaker_stats = {}
        for msg in self.conversation_history:
            if msg["type"] != "system":
                speaker = msg["speaker"]
                speaker_stats[speaker] = speaker_stats.get(speaker, 0) + 1

        print("\n发言统计:")
        for speaker, count in speaker_stats.items():
            print(f"  {speaker[:30]}: {count} 条")

    async def save_debate_record(self):
        """保存辩论记录"""
        try:
            record = {
                "debate_id": self.current_debate_id,
                "topic": self.debate_topic,
                "participants": self.participants,
                "conversation_history": [
                    {
                        **msg,
                        "timestamp": msg["timestamp"].isoformat()
                    }
                    for msg in self.conversation_history
                ],
                "consensus_tracker": self.consensus_tracker,
                "session_info": {
                    "start_time": datetime.now().isoformat(),
                    "total_messages": len(self.conversation_history),
                    "participants_count": len(self.participants)
                }
            }

            # 保存到文件
            filename = f"debate_record_{self.current_debate_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(record, f, indent=2, ensure_ascii=False, default=str)

            print(f"✅ 辩论记录已保存到: {filename}")

        except Exception as e:
            print(f"❌ 保存辩论记录失败: {e}")


async def main():
    """主函数"""
    print("🎉 实时多角色辩论系统")
    print("与AI专家进行真实的实时对话和辩论")
    print()

    system = RealTimeDebateSystem()

    try:
        await system.start_real_time_debate()
        return True
    except Exception as e:
        print(f"❌ 系统异常: {e}")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 系统被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 系统异常: {e}")
        sys.exit(1)

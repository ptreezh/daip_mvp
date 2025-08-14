#!/usr/bin/env python3
"""多轮辩论系统Web应用程序

基于Lona框架的完整Web应用程序，集成了多角色对话引擎、
状态管理、WebSocket实时通信等功能。

运行方式：
python app.py

访问地址：
http://localhost:8080
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

# Lona框架导入
try:
    from lona import App, Route
    from lona.html import H1, HTML, Div, P
    from lona.view import LonaView
except ImportError:
    print("❌ 未安装Lona框架，请运行: pip install lona")
    sys.exit(1)

# 导入辩论系统组件
from debate_state_manager import DebateStateManager
from multi_role_dialogue_engine import MultiRoleDialogueEngine
from web_interface import DebateWebInterface
from websocket_manager import debate_websocket_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debate_system.log')
    ]
)

logger = logging.getLogger(__name__)


class DebateSystemView(LonaView):
    """多轮辩论系统主视图"""

    def __init__(self):
        super().__init__()
        self.debate_interface = None
        self.dialogue_engine = None
        self.state_manager = None

    async def handle_request(self, request):
        """处理HTTP请求"""
        try:
            # 初始化组件（如果尚未初始化）
            if not self.debate_interface:
                await self._initialize_components()

            # 返回主界面
            return self.debate_interface.render()

        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return self._render_error_page(str(e))

    async def _initialize_components(self):
        """初始化系统组件"""
        try:
            logger.info("正在初始化辩论系统组件...")

            # 创建模拟的依赖组件
            mock_cognitive_agent = MockCognitiveAgent()
            mock_role_manager = MockRoleManager()
            mock_llm_manager = MockLLMManager()
            mock_memory_agent = MockMemoryAgent()
            mock_participant_manager = MockParticipantManager()

            # 创建多角色对话引擎
            self.dialogue_engine = MultiRoleDialogueEngine(
                cognitive_agent=mock_cognitive_agent,
                role_manager=mock_role_manager,
                llm_manager=mock_llm_manager,
                memory_agent=mock_memory_agent,
                participant_manager=mock_participant_manager
            )

            # 创建状态管理器
            self.state_manager = DebateStateManager()

            # 创建Web界面
            self.debate_interface = DebateWebInterface(
                dialogue_engine=self.dialogue_engine,
                state_manager=self.state_manager
            )

            logger.info("✅ 辩论系统组件初始化完成")

        except Exception as e:
            logger.error(f"初始化组件失败: {e}")
            raise

    def _render_error_page(self, error_message: str) -> HTML:
        """渲染错误页面"""
        return HTML(
            Div(
                H1("🚨 系统错误", style="color: #dc3545; text-align: center; margin-top: 50px;"),
                P(f"错误信息: {error_message}", style="text-align: center; color: #6c757d;"),
                P("请刷新页面重试，或联系系统管理员。", style="text-align: center; color: #6c757d;"),
                style="max-width: 600px; margin: 0 auto; padding: 20px;"
            )
        )


class HealthCheckView(LonaView):
    """健康检查视图"""

    async def handle_request(self, request):
        """处理健康检查请求"""
        try:
            # 检查系统状态
            status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "websocket_connections": len(debate_websocket_manager.connections),
                "total_messages": debate_websocket_manager.total_messages_sent + debate_websocket_manager.total_messages_received
            }

            return HTML(
                Div(
                    H1("🟢 系统健康状态", style="color: #28a745; text-align: center;"),
                    P(f"状态: {status['status']}", style="text-align: center;"),
                    P(f"时间: {status['timestamp']}", style="text-align: center;"),
                    P(f"WebSocket连接: {status['websocket_connections']}", style="text-align: center;"),
                    P(f"消息总数: {status['total_messages']}", style="text-align: center;"),
                    style="max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #28a745; border-radius: 8px;"
                )
            )

        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return HTML(
                Div(
                    H1("🔴 系统异常", style="color: #dc3545; text-align: center;"),
                    P(f"错误: {str(e)}", style="text-align: center; color: #6c757d;"),
                    style="max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #dc3545; border-radius: 8px;"
                )
            )


# 模拟组件类（用于演示）
class MockCognitiveAgent:
    """模拟认知代理"""

    pass

class MockRoleManager:
    """模拟角色管理器"""

    async def get_available_roles(self):
        """获取可用角色"""
        return {
            "ai_expert": {
                "name": "AI专家",
                "expertise_areas": ["人工智能", "机器学习", "深度学习"],
                "speaking_style": "technical",
                "description": "专注于人工智能技术研究"
            },
            "ethicist": {
                "name": "伦理学家",
                "expertise_areas": ["伦理学", "哲学", "社会影响"],
                "speaking_style": "philosophical",
                "description": "关注技术的伦理和社会影响"
            },
            "economist": {
                "name": "经济学家",
                "expertise_areas": ["经济学", "市场分析", "产业发展"],
                "speaking_style": "analytical",
                "description": "分析技术的经济影响"
            },
            "sociologist": {
                "name": "社会学家",
                "expertise_areas": ["社会学", "人类行为", "社会变迁"],
                "speaking_style": "observational",
                "description": "研究技术对社会的影响"
            }
        }

class MockLLMManager:
    """模拟LLM管理器"""

    async def generate_response(self, prompt: str, model_preference: str = "gpt-4", timeout: int = 30):
        """生成响应"""
        # 模拟LLM响应
        await asyncio.sleep(1)  # 模拟处理时间

        responses = [
            "这是一个非常有趣的观点。从我的专业角度来看，我认为这个问题需要从多个维度来分析。",
            "我同意前面专家的部分观点，但我想补充一些不同的视角。",
            "基于我的研究经验，我认为这个问题的核心在于如何平衡不同利益相关者的需求。",
            "让我从另一个角度来看这个问题。我们需要考虑长期和短期的影响。",
            "这确实是一个复杂的问题。我建议我们可以从以下几个方面来深入讨论。"
        ]

        import random
        return random.choice(responses)

class MockMemoryAgent:
    """模拟记忆代理"""

    async def store_memory(self, key: str, content: Any, memory_type: str = "general"):
        """存储记忆"""
        pass

    async def retrieve_memory(self, key: str):
        """检索记忆"""
        return None

class MockParticipantManager:
    """模拟参与者管理器"""

    pass


def create_app() -> App:
    """创建Lona应用程序"""
    app = App(__name__)

    # 配置静态文件
    static_dir = current_dir / "static"
    if static_dir.exists():
        app.add_static_file_handler("/static/", static_dir)

    # 添加路由
    app.add_route(Route("/", DebateSystemView))
    app.add_route(Route("/health", HealthCheckView))

    return app


async def setup_websocket_server():
    """设置WebSocket服务器"""
    try:
        # 启动WebSocket管理器
        await debate_websocket_manager.start()
        logger.info("✅ WebSocket服务器已启动")
    except Exception as e:
        logger.error(f"启动WebSocket服务器失败: {e}")


async def main():
    """主函数"""
    try:
        logger.info("🚀 启动多轮辩论系统...")

        # 设置WebSocket服务器
        await setup_websocket_server()

        # 创建Lona应用
        app = create_app()

        # 启动应用
        logger.info("🌐 Web服务器启动中...")
        logger.info("📱 访问地址: http://localhost:8080")
        logger.info("🏥 健康检查: http://localhost:8080/health")

        # 运行应用
        app.run(
            host="0.0.0.0",
            port=8080,
            debug=True
        )

    except KeyboardInterrupt:
        logger.info("👋 用户中断，正在关闭系统...")
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        sys.exit(1)
    finally:
        # 清理资源
        try:
            await debate_websocket_manager.stop()
            logger.info("✅ 系统已安全关闭")
        except Exception as e:
            logger.error(f"关闭系统时出错: {e}")


if __name__ == "__main__":
    try:
        # 检查Python版本
        if sys.version_info < (3, 8):
            print("❌ 需要Python 3.8或更高版本")
            sys.exit(1)

        # 检查依赖
        try:
            import lona
            print(f"✅ Lona框架版本: {lona.__version__}")
        except ImportError:
            print("❌ 未安装Lona框架，请运行: pip install lona")
            sys.exit(1)

        # 运行应用
        asyncio.run(main())

    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        sys.exit(1)

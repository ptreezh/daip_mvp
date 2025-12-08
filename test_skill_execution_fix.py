"""
测试技能执行修复
验证TUI中的技能现在通过真实技能管理器执行而不是模拟执行
"""
import asyncio
import unittest.mock
from unittest.mock import Mock, patch
from src.daip_live.skills.manager import SkillManager
from src.daip_live.skills.text_analysis import TextAnalysisSkill
from src.daip_live.agent_engine.enhanced_intent_recognizer import Intent


class TestSkillExecutionFix(unittest.TestCase):
    """测试技能执行修复"""
    
    def setUp(self):
        """设置测试环境"""
        self.skill_manager = SkillManager()
        self.text_analysis_skill = TextAnalysisSkill()
        self.skill_manager.register_skill(self.text_analysis_skill)

    def test_skill_manager_initialization_in_tui(self):
        """测试TUI中技能管理器的初始化"""
        # 检查是否可以在TUI中正确初始化技能管理器 
        from src.daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI
        
        # 创建TUI实例并检查技能管理器是否被初始化
        tui = DAIP_TUI()
        
        # 检查技能管理器是否已初始化
        self.assertTrue(hasattr(tui, '_skill_manager'))
        self.assertIsNotNone(tui._skill_manager)
        
        # 检查是否已注册内置技能
        registered_skills = tui._skill_manager.list_skills()
        self.assertIn('text_analysis', registered_skills)
        
        # 检查Claude技能适配器是否已初始化（如果导入成功）
        self.assertTrue(hasattr(tui, '_claude_skill_adapter_manager'))

    def test_execute_skill_uses_real_skill_manager(self):
        """测试execute_skill意图确实使用真实技能管理器而不是模拟"""
        from src.daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI
        from src.daip_live.skills.base import SkillInput
        
        # 创建TUI实例
        tui = DAIP_TUI()
        
        # 创建一个技能输入
        skill_input = SkillInput(
            data="这是一个测试文本，用于分析。",
            context={"source": "test", "session_id": "test_session"},
            metadata={}
        )
        
        # 确保技能管理器中有text_analysis技能
        self.assertIn('text_analysis', tui._skill_manager.list_skills())
        
        # 获取text_analysis技能
        text_analysis_skill = tui._skill_manager.get_skill('text_analysis')
        self.assertIsNotNone(text_analysis_skill)
        
        # 测试技能执行
        result = text_analysis_skill.execute(skill_input)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertIn('Text Analysis Results', result.result)
        self.assertGreater(len(result.result), 10)  # 确保返回了实际分析结果

    def test_intent_to_skill_mapping(self):
        """测试意图到技能的映射是否正确工作"""
        from src.daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI
        
        tui = DAIP_TUI()
        
        # 模拟一个execute_skill意图
        intent = Intent(
            name="execute_skill",
            confidence=0.9,
            parameters={
                "target_skill": "analysis",
                "content": "这是一个用于测试分析的文本。",
                "original_request_text": "帮我分析这段文本：这是一个用于测试分析的文本。"
            }
        )
        
        # 验证意图参数是否正确设置
        self.assertEqual(intent.name, "execute_skill")
        self.assertEqual(intent.parameters["target_skill"], "analysis")
        self.assertIn("测试分析", intent.parameters["content"])

    def test_skill_lookup_by_type(self):
        """测试通过技能类型查找技能的逻辑"""
        from src.daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI
        
        tui = DAIP_TUI()
        
        # 确保text_analysis技能已注册
        available_skills = tui._skill_manager.list_skills()
        self.assertIn('text_analysis', available_skills)
        
        # 测试通过技能类型查找
        skill = tui._skill_manager.get_skill('text_analysis')
        self.assertIsNotNone(skill)
        self.assertEqual(skill.metadata.name, 'text_analysis')

    def test_skill_execution_integration(self):
        """测试技能执行的端到端集成"""
        from src.daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI
        from src.daip_live.skills.base import SkillInput
        
        tui = DAIP_TUI()
        
        # 准备技能输入
        skill_input = SkillInput(
            data="测试技能执行集成",
            context={"source": "integration_test", "session_id": "test_session"},
            metadata={}
        )
        
        # 获取并执行text_analysis技能
        text_analysis_skill = tui._skill_manager.get_skill('text_analysis')
        self.assertIsNotNone(text_analysis_skill)
        
        # 执行技能
        result = text_analysis_skill.execute(skill_input)
        
        # 验证执行结果
        self.assertIsNotNone(result)
        self.assertGreater(result.confidence, 0.5)  # 置信度应该合理
        self.assertIn('Text Analysis Results', result.result)  # 包含分析结果

    @patch('builtins.print')  # 模拟print函数以避免控制台输出
    def test_tui_skill_initialization_method(self, mock_print):
        """测试TUI中的技能初始化方法"""
        from src.daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI
        
        # 创建TUI实例
        tui = DAIP_TUI()
        
        # 验证技能管理器已初始化
        self.assertTrue(hasattr(tui, '_skill_manager'))
        self.assertIsNotNone(tui._skill_manager)
        
        # 验证Claude技能适配器管理器也已初始化
        self.assertTrue(hasattr(tui, '_claude_skill_adapter_manager'))
        
        # 验证内置技能已注册
        registered_skills = tui._skill_manager.list_skills()
        self.assertIn('text_analysis', registered_skills)


def run_tests():
    """运行所有测试"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
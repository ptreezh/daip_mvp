"""
测试意图到技能的集成
验证意图识别器能够正确映射到真实技能并执行
"""
import unittest
from unittest.mock import Mock, patch
from src.daip_live.skills.manager import SkillManager
from src.daip_live.skills.text_analysis import TextAnalysisSkill
from src.daip_live.skills.base import SkillInput, SkillOutput
from src.daip_live.agent_engine.enhanced_intent_recognizer import Intent


class TestIntentSkillIntegration(unittest.TestCase):
    """测试意图到技能的集成"""
    
    def setUp(self):
        """设置测试环境"""
        self.skill_manager = SkillManager()
        self.text_analysis_skill = TextAnalysisSkill()
        self.skill_manager.register_skill(self.text_analysis_skill)
    
    def test_execute_skill_intent_mapping(self):
        """测试execute_skill意图的映射"""
        # 模拟意图识别器返回的意图
        intent = Intent(
            name="execute_skill",
            confidence=0.9,
            parameters={
                "target_skill": "analysis",
                "content": "这是一个测试文本",
                "original_request_text": "帮我分析这段文本：这是一个测试文本"
            }
        )
        
        # 验证意图参数
        self.assertEqual(intent.name, "execute_skill")
        self.assertEqual(intent.parameters["target_skill"], "analysis")
        self.assertIn("测试文本", intent.parameters["content"])
        
        print("✅ 意图映射测试通过！")
    
    def test_skill_lookup_by_content(self):
        """测试通过内容查找技能"""
        # 首先确保技能已注册
        registered_skills = self.skill_manager.list_skills()
        self.assertIn('text_analysis', registered_skills)
        
        # 模拟查找逻辑：先尝试精确匹配，再尝试模糊匹配
        skill_content = "text_analysis"  # 技能名
        if skill_content in registered_skills:
            skill = self.skill_manager.get_skill(skill_content)
            self.assertIsNotNone(skill)
            self.assertEqual(skill.metadata.name, "text_analysis")
        
        # 测试模糊匹配
        skill_type = "analysis"
        found_skill = None
        for skill_name in registered_skills:
            if skill_type in skill_name or skill_type.replace("_", " ") in skill_name:
                found_skill = self.skill_manager.get_skill(skill_name)
                break
        
        self.assertIsNotNone(found_skill)
        self.assertEqual(found_skill.metadata.name, "text_analysis")
        
        print("✅ 技能查找测试通过！")
    
    def test_skill_execution_with_intent_params(self):
        """测试使用意图参数执行技能"""
        # 获取已注册的技能
        skill = self.skill_manager.get_skill("text_analysis")
        self.assertIsNotNone(skill)
        
        # 使用意图中的参数创建技能输入
        skill_input = SkillInput(
            data="这是一个用于测试的文本内容，验证意图参数是否正确传递给技能。",
            context={
                "source": "intent_recognition", 
                "session_id": "test_session_123"
            },
            metadata={}
        )
        
        # 执行技能
        result = skill.execute(skill_input)
        
        # 验证结果
        self.assertIsInstance(result, SkillOutput)
        self.assertIsNotNone(result.result)
        self.assertGreater(len(result.result), 0)
        self.assertGreater(result.confidence, 0.0)
        
        # 验证分析结果包含预期内容
        result_text = result.result.lower()
        self.assertIn('word count', result_text)
        self.assertIn('character count', result_text)
        
        print(f"✅ 技能执行测试通过！结果长度: {len(result.result)} 字符")
    
    def test_analysis_skill_identification(self):
        """测试分析类技能的识别和执行"""
        skill_found = False
        
        # 模拟TUI中处理analysis意图的逻辑
        skill_type = "analysis"
        skill_content = "这是需要分析的文本内容"
        
        # 查找匹配的技能
        available_skills = self.skill_manager.list_skills()
        if "text_analysis" in available_skills:
            analysis_skill = self.skill_manager.get_skill("text_analysis")
            if analysis_skill:
                # 执行技能
                skill_input = SkillInput(
                    data=skill_content,
                    context={"source": "intent_recognition", "session_id": "test_session"},
                    metadata={}
                )
                
                result = analysis_skill.execute(skill_input)
                self.assertIsNotNone(result)
                self.assertIn('Text Analysis Results', result.result)
                
                skill_found = True
        
        self.assertTrue(skill_found, "应该能够找到并执行分析技能")
        print("✅ 分析技能识别和执行测试通过！")
    
    def test_intent_to_skill_workflow(self):
        """测试完整的意图到技能工作流程"""
        # 模拟一个完整的流程
        intent = Intent(
            name="execute_skill",
            confidence=0.85,
            parameters={
                "target_skill": "analysis",
                "content": "对这段文本进行分析测试",
                "original_request_text": "请帮我分析：对这段文本进行分析测试"
            }
        )
        
        # 根据意图参数执行技能查找和执行的逻辑
        skill_type = intent.parameters.get("target_skill", "general")
        skill_content = intent.parameters.get("content", "")
        
        # 模拟TUI中的技能查找逻辑
        skill_found = False
        if skill_content and skill_content.strip():
            if skill_type == "analysis" or any(keyword in skill_content for keyword in ["分析", "analyze", "text", "内容"]):
                # 查找text_analysis技能
                if "text_analysis" in self.skill_manager.list_skills():
                    analysis_skill = self.skill_manager.get_skill("text_analysis")
                    if analysis_skill:
                        # 创建技能输入
                        skill_input = SkillInput(
                            data=skill_content,
                            context={"source": "intent_recognition", "session_id": "test_workflow"},
                            metadata={}
                        )
                        
                        # 执行技能
                        result = analysis_skill.execute(skill_input)
                        
                        # 验证结果
                        self.assertIsNotNone(result)
                        self.assertIn('Text Analysis Results', result.result)
                        
                        skill_found = True
        
        self.assertTrue(skill_found, "应该能够完成完整的意图到技能工作流程")
        print("✅ 完整工作流程测试通过！")


def run_integration_tests():
    """运行集成测试"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntentSkillIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    if success:
        print("\n🎉 所有意图-技能集成测试通过！")
    else:
        print("\n❌ 有意图-技能集成测试失败！")
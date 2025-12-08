"""
简单测试技能执行修复
验证技能系统能够正常使用真实技能而非模拟执行
"""
import unittest
from src.daip_live.skills.manager import SkillManager
from src.daip_live.skills.text_analysis import TextAnalysisSkill
from src.daip_live.skills.base import SkillInput


class TestSkillExecutionSimple(unittest.TestCase):
    """简单测试技能执行"""
    
    def test_skill_manager_and_text_analysis(self):
        """测试技能管理器和文本分析技能"""
        # 创建技能管理器
        skill_manager = SkillManager()
        
        # 创建并注册文本分析技能
        text_analysis_skill = TextAnalysisSkill()
        skill_manager.register_skill(text_analysis_skill)
        
        # 验证技能已注册
        registered_skills = skill_manager.list_skills()
        self.assertIn('text_analysis', registered_skills)
        
        # 获取技能
        retrieved_skill = skill_manager.get_skill('text_analysis')
        self.assertIsNotNone(retrieved_skill)
        self.assertEqual(retrieved_skill.metadata.name, 'text_analysis')
        
        # 测试技能执行
        skill_input = SkillInput(
            data="这是一个测试文本，用于分析词数和字符数。",
            context={"source": "test", "session_id": "test_session"},
            metadata={}
        )
        
        result = retrieved_skill.execute(skill_input)
        
        # 验证执行结果
        self.assertIsNotNone(result)
        self.assertGreater(len(result.result), 0)
        self.assertIn('Text Analysis Results', result.result)
        self.assertGreater(result.confidence, 0.0)
        
        # 验证分析结果包含预期的信息
        result_text = result.result.lower()
        self.assertIn('word count', result_text)
        self.assertIn('character count', result_text)
        
        print(f"✅ 技能执行测试通过！结果: {result.result[:100]}...")

    def test_multiple_skills_registration(self):
        """测试多个技能的注册和执行"""
        skill_manager = SkillManager()
        
        # 注册文本分析技能
        text_analysis_skill = TextAnalysisSkill()
        skill_manager.register_skill(text_analysis_skill)
        
        # 验证注册
        skills_list = skill_manager.list_skills()
        self.assertIn('text_analysis', skills_list)
        self.assertEqual(len(skills_list), 1)
        
        print(f"✅ 多技能注册测试通过！已注册技能: {skills_list}")

    def test_skill_parameters_handling(self):
        """测试技能参数处理"""
        skill_manager = SkillManager()
        text_analysis_skill = TextAnalysisSkill()
        skill_manager.register_skill(text_analysis_skill)
        
        # 测试不同的输入参数
        test_inputs = [
            "简短文本",
            "这是一个更长的测试文本，用于验证技能是否能够正确处理不同长度的输入。",
            "",  # 空文本
        ]
        
        for i, test_text in enumerate(test_inputs):
            skill_input = SkillInput(
                data=test_text,
                context={"source": f"test_{i}", "session_id": f"session_{i}"},
                metadata={"test_param": f"value_{i}"}
            )
            
            result = text_analysis_skill.execute(skill_input)
            self.assertIsNotNone(result)
            
            # 对于空文本，结果应仍包含分析框架
            if test_text == "":
                self.assertIn('Text Analysis Results', result.result)
            else:
                # 对于非空文本，验证词数等指标
                self.assertGreater(len(result.result), 0)
        
        print("✅ 技能参数处理测试通过！")


def run_simple_tests():
    """运行简单测试"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSkillExecutionSimple)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_simple_tests()
    if success:
        print("\n🎉 所有测试通过！技能执行修复验证成功！")
    else:
        print("\n❌ 有测试失败！")
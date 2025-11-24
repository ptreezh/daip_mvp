"""
TDD测试2: 语义匹配功能测试
文件: test_semantic_matching.py
按照TDD原则：先写测试，再实现功能
"""
import unittest
import sys
sys.path.insert(0, './src')

from daip_live.multi_agent_collab.hybrid_intent_collaboration_engine import HybridIntentRecognizer


class TestSemanticMatching(unittest.TestCase):
    """测试语义匹配功能"""
    
    def setUp(self):
        self.recognizer = HybridIntentRecognizer()
    
    def test_semantic_wiki_matching(self):
        """测试维基语义匹配 - 检测同义表达"""
        semantic_wiki_tests = [
            ("协同创建关于AI的百科", "create_wiki", "协同-创建维基的同义表达"),
            ("一起写个知识条目 量子计算", "create_wiki", "一起写-创建维基的同义表达"),
            ("合作构建维基页面 机器学习", "create_wiki", "合作构建-创建维基的同义表达"),
        ]
        
        success_count = 0
        for test_input, expected_intent, description in semantic_wiki_tests:
            intent = self.recognizer.recognize_intent(test_input)
            if intent and expected_intent in intent.name:
                print(f"    ✅ {description}: '{test_input}' -> {intent.name}")
                success_count += 1
            else:
                print(f"    ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'}")
        
        self.assertGreaterEqual(success_count, 2, f"至少需要2个语义匹配成功，实际: {success_count}")
    
    def test_semantic_debate_matching(self):
        """测试辩论语义匹配 - 检测同义表达"""
        semantic_debate_tests = [
            ("多个AI一起讨论人工智能伦理", "start_debate", "多AI讨论-辩论的同义表达"),
            ("多智能体辩论 AI未来", "start_debate", "多智能体-多模型辩论的同义表达"),
            ("协作辩论 量子计算挑战", "start_debate", "协作辩论-辩论的同义表达"),
        ]
        
        success_count = 0
        for test_input, expected_intent, description in semantic_debate_tests:
            intent = self.recognizer.recognize_intent(test_input)
            if intent and expected_intent in intent.name:
                print(f"    ✅ {description}: '{test_input}' -> {intent.name}")
                success_count += 1
            else:
                print(f"    ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'}")
        
        self.assertGreaterEqual(success_count, 2, f"至少需要2个语义匹配成功，实际: {success_count}")
    
    def test_fuzzy_content_extraction(self):
        """测试模糊内容提取功能"""
        fuzzy_tests = [
            ("帮我解析以下内容：人工智能的发展趋势", "execute_skill", "帮助解析模糊内容"),
            ("请帮我对这段话进行分析：机器学习的进步", "execute_skill", "请求帮助分析模糊内容"),
            ("维基协作编写 深度学习基础", "create_wiki", "协作编写维基模糊内容"),
        ]
        
        success_count = 0
        for test_input, expected_intent, description in fuzzy_tests:
            intent = self.recognizer.recognize_intent(test_input)
            if intent and expected_intent in intent.name:
                print(f"    ✅ {description}: '{test_input}' -> {intent.name}")
                success_count += 1
            else:
                print(f"    ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'}")
        
        self.assertGreaterEqual(success_count, 2, f"至少需要2个模糊内容提取成功，实际: {success_count}")


class TestCollaborationFeatures(unittest.TestCase):
    """测试协作功能"""
    
    def setUp(self):
        from daip_live.multi_agent_collab.real_collaboration_engine import MultiRoleWikiCollaborator
        self.collaborator = MultiRoleWikiCollaborator()
    
    def test_collaborative_wiki_session(self):
        """测试协作维基会话创建"""
        import asyncio
        
        async def run_test():
            await self.collaborator.start_collaboration(
                title="测试协作词条",
                participants=["Researcher_Agent", "Writer_Agent", "Editor_Agent"],
                initial_content="这是一个测试协作的维基词条。"
            )
            
            # 验证会话创建
            self.assertEqual(self.collaborator.title, "测试协作词条")
            self.assertIn("Researcher_Agent", self.collaborator.participants)
            self.assertIn("Writer_Agent", self.collaborator.participants)
            self.assertIn("Editor_Agent", self.collaborator.participants)
            
            # 测试多角色贡献
            contributions = await self.collaborator.run_collaborative_editing_round(["overview"])
            self.assertGreaterEqual(len(contributions), 3, f"至少应有3个贡献，实际: {len(contributions)}")
            
            content = await self.collaborator.get_current_content()
            self.assertIn("overview", content)
            
            return True
        
        result = asyncio.run(run_test())
        self.assertTrue(result, "协作维基会话测试应成功")


if __name__ == '__main__':
    print("="*70)
    print("🔍 TDD测试: 语义匹配和协作功能")
    print("这些测试在语义匹配功能实现前会失败")
    print("="*70)
    
    unittest.main(verbosity=2)
"""
TDD测试套件 - 第一阶段：修复现有问题
测试文件: test_intent_recognition_phase1.py
按照TDD原则：先写测试，再实现功能
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer


class TestWikiParameterExtraction(unittest.TestCase):
    """测试维基参数提取功能"""
    
    def setUp(self):
        self.recognizer = EnhancedIntentRecognizer()
    
    def test_extract_wiki_title_with_space(self):
        """测试带空格的维基标题提取 - 这个应该会失败，因为当前实现有问题"""
        text = "创建维基 项目计划"
        intent = self.recognizer.recognize_intent(text)
        
        # 根据需求，期望title应该是"项目计划"，不是空字符串
        if intent and intent.name == "create_wiki":
            self.assertEqual(intent.parameters["title"], "项目计划", 
                           f"期望title='项目计划'，实际得到='{intent.parameters['title']}'")
        else:
            self.fail(f"期望create_wiki意图，实际得到={intent.name if intent else 'None'}")
    
    def test_extract_wiki_title_without_space(self):
        """测试不带空格的维基标题提取"""
        text = "写个维基人工智能"
        intent = self.recognizer.recognize_intent(text)
        
        if intent and intent.name == "create_wiki":
            self.assertIn("人工智能", intent.parameters["title"])
        else:
            self.fail(f"期望create_wiki意图，实际得到={intent.name if intent else 'None'}")
    
    def test_extract_empty_wiki_title(self):
        """测试空维基标题提取"""
        text = "创建维基"
        intent = self.recognizer.recognize_intent(text)
        
        if intent and intent.name == "create_wiki":
            # 这个情况应该被标记为需要澄清
            self.assertTrue(intent.requires_clarification)
        else:
            self.fail(f"期望create_wiki意图，实际得到={intent.name if intent else 'None'}")


class TestSkillParameterExtraction(unittest.TestCase):
    """测试技能参数提取功能"""
    
    def setUp(self):
        self.recognizer = EnhancedIntentRecognizer()
    
    def test_extract_skill_content(self):
        """测试技能内容提取"""
        text = "帮我分析这段文本内容"
        intent = self.recognizer.recognize_intent(text)
        
        # 这个测试会失败，因为当前实现将"帮我分析这段文本内容"识别为question而不是execute_skill
        if intent and intent.name == "execute_skill":
            # 检查是否提取到了内容
            content = intent.parameters.get("content", "")
            original_request = intent.parameters.get("original_request_text", "")
            
            # 期望参数中包含原始文本或部分文本内容
            self.assertTrue(content or original_request)
        else:
            self.fail(f"期望execute_skill意图，实际得到={intent.name if intent else 'None'}")
    
    def test_extract_skill_content_empty(self):
        """测试空技能内容提取"""
        text = "帮我"
        intent = self.recognizer.recognize_intent(text)
        
        if intent and intent.name == "execute_skill":
            # 这个应该需要澄清
            self.assertTrue(intent.requires_clarification)
        else:
            self.fail(f"期望execute_skill意图，实际得到={intent.name if intent else 'None'}")


class TestIntentPriority(unittest.TestCase):
    """测试意图优先级"""
    
    def setUp(self):
        self.recognizer = EnhancedIntentRecognizer()
    
    def test_personal_assistant_priority(self):
        """测试个人助手意图优先级 - '个人助手帮我分析'应识别为personal_assistant而非question"""
        text = "个人助手帮我分析"
        intent = self.recognizer.recognize_intent(text)
        
        # 根据需求，这个应该被识别为personal_assistant，而不是question
        self.assertEqual(intent.name if intent else "None", "personal_assistant",
                        f"期望personal_assistant意图，实际得到={intent.name if intent else 'None'}")
    
    def test_skill_execution_priority(self):
        """测试技能执行意图优先级 - '帮我分析这段文本'应识别为execute_skill而非question"""
        text = "帮我分析这段文本"
        intent = self.recognizer.recognize_intent(text)
        
        self.assertEqual(intent.name if intent else "None", "execute_skill",
                        f"期望execute_skill意图，实际得到={intent.name if intent else 'None'}")
    
    def test_knowledge_search_priority(self):
        """测试知识库搜索意图优先级 - '本地知识查找'应识别为knowledge_search而非search_papers"""
        text = "本地知识查找"
        intent = self.recognizer.recognize_intent(text)
        
        self.assertIn("knowledge", intent.name if intent else "",
                     f"期望包含'knowledge'的意图，实际得到={intent.name if intent else 'None'}")


class TestClarificationDetection(unittest.TestCase):
    """测试澄清检测功能"""
    
    def setUp(self):
        self.recognizer = EnhancedIntentRecognizer()
    
    def test_help_needs_clarification(self):
        """测试'帮我'需要澄清"""
        text = "帮我"
        intent = self.recognizer.recognize_intent(text)
        
        # 这个应该被标记为需要澄清
        self.assertTrue(intent.requires_clarification if intent else False,
                       f"期望requires_clarification=True，实际得到={intent.requires_clarification if intent else 'None'}")
    
    def test_wiki_creation_needs_clarification(self):
        """测试'创建维基'需要澄清"""
        text = "创建维基"
        intent = self.recognizer.recognize_intent(text)
        
        self.assertTrue(intent.requires_clarification if intent else False,
                       f"期望requires_clarification=True，实际得到={intent.requires_clarification if intent else 'None'}")
    
    def test_debate_start_needs_clarification(self):
        """测试'开始辩论'需要澄清"""
        text = "开始辩论"
        intent = self.recognizer.recognize_intent(text)
        
        self.assertTrue(intent.requires_clarification if intent else False,
                       f"期望requires_clarification=True，实际得到={intent.requires_clarification if intent else 'None'}")


if __name__ == '__main__':
    # 运行所有测试
    print("🔍 运行第一阶段TDD测试套件...")
    print("根据TDD原则，这些测试当前应该会失败，因为功能还未实现")
    
    unittest.main(verbosity=2)
"""
测试参数提取和预填充功能
"""

import unittest
from src.intent_recognition.context_aware_intent_recognizer import ContextAwareIntentRecognizer
from src.intent_recognition.context_manager import ContextManager
from src.intent_recognition.enhanced_parameter_extraction import ParameterExtractor


class TestParameterExtraction(unittest.TestCase):
    """参数提取功能测试"""
    
    def setUp(self):
        self.extractor = ParameterExtractor()
    
    def test_paper_topic_extraction(self):
        """测试论文主题提取"""
        # 测试包含明确主题的输入
        result = self.extractor.extract_from_input("下载 意图识别与上下文管理相关的论文", "paper")
        self.assertIsNotNone(result.topic)
        self.assertIn("意图识别", result.topic)
        
        # 测试更复杂的输入
        result = self.extractor.extract_from_input("下载论文 意识识别 意图识别 上下文管理", "paper")
        self.assertIsNotNone(result.topic)
        self.assertIn("意识识别", result.topic) or self.assertIn("意图识别", result.topic)
    
    def test_wiki_title_extraction(self):
        """测试Wiki标题提取"""
        result = self.extractor.extract_from_input("你给我编写一个  中美贸易战的词条", "wiki")
        self.assertIsNotNone(result.title)
        self.assertIn("中美贸易战", result.title)
        
        result = self.extractor.extract_from_input("编写词条 中美贸易战", "wiki")
        self.assertIsNotNone(result.title)
        self.assertIn("中美贸易战", result.title)
    
    def test_arxiv_id_extraction(self):
        """测试arXiv ID提取"""
        result = self.extractor.extract_from_input("下载论文 1234.5678", "paper")
        self.assertIsNotNone(result.arxiv_id)
        self.assertEqual(result.arxiv_id, "1234.5678")


class TestEnhancedContextAwareRecognizer(unittest.TestCase):
    """增强版上下文感知识别器测试"""
    
    def setUp(self):
        self.context_manager = ContextManager()
        self.base_recognizer = None  # 使用None，因为我们只测试上下文相关的功能
        self.recognizer = ContextAwareIntentRecognizer(
            context_manager=self.context_manager,
            base_intent_recognizer=self.base_recognizer
        )
        self.session_id = "test_enhanced_001"
    
    def test_paper_download_with_topic_extraction(self):
        """测试论文下载时的主题提取"""
        # 设置论文下载上下文
        context_data = {
            'task_type': 'download_paper',
            'required_params': ['topic']
        }
        self.context_manager.set_context(self.session_id, context_data)
        
        # 用户输入包含明确主题
        result = self.recognizer.recognize_intent(self.session_id, "下载 意图识别与上下文管理相关的论文")
        
        # 验证是否提取了主题
        self.assertIn("extracted_params", result)
        if result["extracted_params"]:
            extracted_topic = result["extracted_params"].get("topic")
            if extracted_topic:
                self.assertIn("意图识别", extracted_topic)
        
        # 验证参数是否被填充
        self.assertTrue(len(result["filled_params"]) > 0)
    
    def test_wiki_creation_with_title_extraction(self):
        """测试Wiki创建时的标题提取"""
        # 设置Wiki创建上下文
        context_data = {
            'task_type': 'create_wiki',
            'required_params': ['title']
        }
        self.context_manager.set_context(self.session_id, context_data)
        
        # 用户输入包含明确标题
        result = self.recognizer.recognize_intent(self.session_id, "编写词条 中美贸易战")
        
        # 验证是否提取了标题
        self.assertIn("extracted_params", result)
        if result["extracted_params"]:
            extracted_title = result["extracted_params"].get("title")
            if extracted_title:
                self.assertIn("中美贸易战", extracted_title)
        
        # 验证参数是否被填充
        self.assertTrue(len(result["filled_params"]) > 0)
    
    def test_multiple_params_extraction(self):
        """测试多个参数的提取"""
        # 设置需要多个参数的上下文
        context_data = {
            'task_type': 'download_paper',
            'required_params': ['topic', 'keywords']
        }
        self.context_manager.set_context(self.session_id, context_data)
        
        result = self.recognizer.recognize_intent(self.session_id, "下载 关于大语言模型训练技术的论文")
        
        # 应该提取到主题
        self.assertIn("extracted_params", result)
        self.assertTrue(len(result["filled_params"]) > 0)


def run_demo():
    """运行演示"""
    print("=== 参数提取和预填充功能演示 ===\n")
    
    extractor = ParameterExtractor()
    
    print("1. 论文主题提取测试:")
    inputs_to_test = [
        "下载 意图识别与上下文管理相关的论文",
        "下载论文 意识识别 意图识别 上下文管理",
        "下载论文 1234.5678"
    ]
    
    for test_input in inputs_to_test:
        result = extractor.extract_from_input(test_input, "paper")
        print(f"   输入: {test_input}")
        print(f"   提取结果: topic={result.topic}, arxiv_id={result.arxiv_id}")
        print()
    
    print("2. Wiki标题提取测试:")
    wiki_inputs = [
        "你给我编写一个  中美贸易战的词条",
        "编写词条 中美贸易战",
        "创建关于Python编程的百科页面"
    ]
    
    for test_input in wiki_inputs:
        result = extractor.extract_from_input(test_input, "wiki")
        print(f"   输入: {test_input}")
        print(f"   提取结果: title={result.title}")
        print()
    
    print("3. 上下文感知参数填充测试:")
    context_manager = ContextManager()
    recognizer = ContextAwareIntentRecognizer(context_manager, None)
    session_id = "demo_001"
    
    # 测试论文下载上下文
    print("   设置论文下载上下文...")
    context_manager.set_context(session_id, {
        'task_type': 'download_paper',
        'required_params': ['topic']
    })
    
    result = recognizer.recognize_intent(session_id, "下载 意图识别与上下文管理相关的论文")
    print(f"   输入: 下载 意图识别与上下文管理相关的论文")
    print(f"   填充的参数: {result.get('filled_params', [])}")
    print(f"   提取的参数: {result.get('extracted_params', {})}")
    print()
    
    # 清理上下文
    context_manager.clear_context(session_id)
    
    # 测试Wiki创建上下文
    print("   设置Wiki创建上下文...")
    context_manager.set_context(session_id, {
        'task_type': 'create_wiki',
        'required_params': ['title']
    })
    
    result = recognizer.recognize_intent(session_id, "编写词条 中美贸易战")
    print(f"   输入: 编写词条 中美贸易战")
    print(f"   填充的参数: {result.get('filled_params', [])}")
    print(f"   提取的参数: {result.get('extracted_params', {})}")
    print()
    
    print("✅ 参数提取和预填充功能演示完成！")


if __name__ == '__main__':
    # 运行单元测试
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "="*50)
    # 运行演示
    run_demo()
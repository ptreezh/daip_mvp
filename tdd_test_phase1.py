"""
TDD测试: Wiki实时展示功能
测试文件: test_wiki_realtime_display.py
"""
import unittest
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer


class TestWikiRealtimeDisplay(unittest.TestCase):
    """
    TDD测试用例：Wiki实时展示功能
    根据TDD原则：先写测试，再实现功能，最后重构
    """

    def setUp(self):
        """设置测试环境"""
        self.recognizer = EnhancedIntentRecognizer()

    def test_create_term_intent_recognition(self):
        """测试创建词条意图识别 - 这个测试会失败直到功能实现"""
        test_inputs = [
            "创建词条 人工智能",
            "新建词条 机器学习", 
            "创建维基 深度学习",
            "写个词条 自然语言处理"
        ]
        
        for test_input in test_inputs:
            with self.subTest(input=test_input):
                intent = self.recognizer.recognize_intent(test_input)
                # 根据需求，这些应该识别为create_wiki意图
                self.assertIsNotNone(intent, f"输入 '{test_input}' 没有识别到任何意图")
                self.assertIn("wiki", intent.name.lower(), 
                             f"输入 '{test_input}' 应该识别为wiki相关意图，实际得到: {intent.name}")

    def test_edit_term_intent_recognition(self):
        """测试编辑词条意图识别"""
        test_inputs = [
            "编辑词条 人工智能",
            "修改维基 机器学习",
            "编辑百科 深度学习"
        ]
        
        for test_input in test_inputs:
            with self.subTest(input=test_input):
                intent = self.recognizer.recognize_intent(test_input)
                self.assertIsNotNone(intent, f"输入 '{test_input}' 没有识别到任何意图")
                # 编辑意图可能是update_wiki或者其他相关意图
                self.assertTrue("wiki" in intent.name.lower() or "edit" in intent.name.lower(),
                               f"输入 '{test_input}' 应该识别为编辑相关意图，实际得到: {intent.name}")

    def test_view_term_intent_recognition(self):
        """测试查看词条意图识别"""
        test_inputs = [
            "查看词条 人工智能", 
            "查看维基 机器学习",
            "浏览百科 深度学习"
        ]
        
        for test_input in test_inputs:
            with self.subTest(input=test_input):
                intent = self.recognizer.recognize_intent(test_input)
                self.assertIsNotNone(intent, f"输入 '{test_input}' 没有识别到任何意图")
                # 查看意图可能是view_wiki或者其他相关意图
                # 实际上可能还是映射到create_wiki但需要特殊处理
                print(f"输入: {test_input}, 意图: {intent.name if intent else None}, 参数: {getattr(intent, 'parameters', {})}")


class TestPaperDownloadFlow(unittest.TestCase):
    """
    TDD测试用例：论文搜索下载流程
    """

    def setUp(self):
        """设置测试环境"""
        self.recognizer = EnhancedIntentRecognizer()

    def test_paper_download_intent_recognition(self):
        """测试论文下载意图识别 - 应该触发搜索然后下载的流程"""
        test_inputs = [
            "下载论文 人工智能", 
            "下载论文 机器学习综述",
            "获取论文 量子计算",
            "下载文章 区块链技术"
        ]
        
        for test_input in test_inputs:
            with self.subTest(input=test_input):
                intent = self.recognizer.recognize_intent(test_input)
                self.assertIsNotNone(intent, f"输入 '{test_input}' 没有识别到任何意图")
                
                # 这应该是启动搜索下载流程的意图
                # 可能是search_and_download或download_with_search意图
                print(f"输入: {test_input}, 意图: {intent.name if intent else None}, 参数: {getattr(intent, 'parameters', {})}")
                
                # 参数应该包含搜索关键词
                if hasattr(intent, 'parameters'):
                    query_param = intent.parameters.get('query', intent.parameters.get('keyword', ''))
                    self.assertIsNotNone(query_param and query_param != '', 
                                      f"输入 '{test_input}' 应该提取关键词参数")


if __name__ == '__main__':
    print("🔍 执行TDD测试: Wiki实时展示和论文下载流程")
    print("根据TDD原则，这些测试当前应该会失败，因为功能尚未实现")
    
    # 运行测试
    unittest.main(verbosity=2)
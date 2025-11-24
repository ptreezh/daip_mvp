"""
TDD测试5: 论文搜索下载连续流程测试
文件: test_paper_search_download_flow.py
按照TDD原则: 先写测试，再实现功能
"""
import unittest
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer


class TestPaperSearchDownloadFlow(unittest.TestCase):
    """测试论文搜索下载连续流程"""
    
    def setUp(self):
        """设置测试环境"""
        self.recognizer = EnhancedIntentRecognizer()
    
    def test_search_then_download_flow(self):
        """测试搜索然后下载的连续流程 - 这个应该失败直到实现连续流程"""
        # 模拟用户输入"下载论文 人工智能"
        # 期望: 系统应该首先搜索"人工智能"相关的论文，然后提供下载选项
        
        input_text = "下载论文 人工智能"
        intent = self.recognizer.recognize_intent(input_text)
        
        # 根据需求，这应该触发一个连续流程而不是直接下载
        if intent:
            print(f"识别到意图: {intent.name}")
            print(f"参数: {intent.parameters}")
            
            # 期望触发搜索流程或连续流程
            expected_behavior = (
                "search_and_download" in intent.name or
                "download_with_search" in intent.name or
                "find_and_download" in intent.name or
                ("download" in intent.name and intent.requires_clarification)  # 如果需要用户选择具体论文
            )
            
            self.assertTrue(expected_behavior, 
                           f"期望触发搜索-下载连续流程，实际得到: {intent.name}, "
                           f"参数: {intent.parameters}, "
                           f"需要澄清: {getattr(intent, 'requires_clarification', 'N/A')}")
        else:
            self.fail(f"未能识别意图: {input_text}")
    
    def test_download_paper_with_id(self):
        """测试带ID的论文下载 - 应该直接下载"""
        input_text = "下载论文 1234.5678"
        intent = self.recognizer.recognize_intent(input_text)
        
        if intent:
            # 这应该直接识别为下载意图且有ID参数
            self.assertIn("download", intent.name.lower(), 
                         f"期望包含'download'的意图，实际得到: {intent.name}")
            
            paper_id = intent.parameters.get("paper_id") or intent.parameters.get("arxiv_id")
            self.assertIsNotNone(paper_id, "应该提取论文ID")
            self.assertIn("1234.5678", str(paper_id), "应该正确提取论文ID")
        else:
            self.fail(f"未能识别意图: {input_text}")
    
    def test_search_only_flow(self):
        """测试仅搜索功能 - 应该只搜索不下载"""
        input_text = "搜索论文 机器学习"
        intent = self.recognizer.recognize_intent(input_text)
        
        if intent:
            self.assertIn("search", intent.name.lower(), 
                         f"期望包含'search'的意图，实际得到: {intent.name}")
            
            query = intent.parameters.get("query")
            self.assertIsNotNone(query, "应该提取搜索查询")
            self.assertIn("机器学习", query, "应该正确提取搜索关键词")
        else:
            self.fail(f"未能识别意图: {input_text}")


class TestIntegratedWorkflow(unittest.TestCase):
    """测试集成工作流"""
    
    def setUp(self):
        """设置测试环境"""
        self.recognizer = EnhancedIntentRecognizer()
        
    def test_search_download_workflow_integrated(self):
        """测试搜索下载工作流集成 - 模拟完整交互流程"""
        # 模拟典型的用户交互序列
        user_inputs = [
            "下载论文 人工智能发展趋势",  # 用户想要下载关于这个主题的论文
            "搜索深度学习最新研究",      # 用户想要搜索相关论文
            "查看机器学习综述论文",      # 用户想要查看特定论文
        ]
        
        for user_input in user_inputs:
            with self.subTest(input=user_input):
                intent = self.recognizer.recognize_intent(user_input)
                
                if intent:
                    print(f"   输入: '{user_input}' -> 意图: {intent.name}")
                    print(f"     参数: {intent.parameters}")
                    
                    # 验证关键参数提取
                    if "download" in intent.name.lower():
                        # 下载意图可能需要搜索关键词或论文ID
                        has_search_query = "query" in intent.parameters or "keyword" in intent.parameters
                        has_paper_id = "paper_id" in intent.parameters or "arxiv_id" in intent.parameters
                        
                        # 应该要么有具体ID直接下载，要么有搜索查询先搜索
                        self.assertTrue(has_search_query or has_paper_id or getattr(intent, 'requires_clarification', False),
                                       f"下载意图应包含搜索查询或论文ID或需要澄清: {intent.parameters}")
                    
                    elif "search" in intent.name.lower():
                        # 搜索意图必须有查询参数
                        query = intent.parameters.get("query") or intent.parameters.get("keyword")
                        self.assertIsNotNone(query, f"搜索意图应包含查询参数: {intent.parameters}")
                else:
                    self.fail(f"未能识别意图: {user_input}")


if __name__ == '__main__':
    print("="*70)
    print("🔧 TDD测试: 论文搜索下载连续流程")
    print("根据TDD原则，这些测试现在应该失败，因为连续流程尚未实现")
    print("="*70)
    
    unittest.main(verbosity=2)
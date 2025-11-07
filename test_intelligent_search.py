#!/usr/bin/env python3
"""
测试优化后的论文搜索功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daip_live.doc.paper_downloader import PaperDownloader

def test_intelligent_search():
    """测试智能搜索功能"""
    from pathlib import Path
    download_dir = Path("test_downloads")
    download_dir.mkdir(exist_ok=True)
    downloader = PaperDownloader(download_dir)
    
    print("=== 测试智能论文搜索功能 ===\n")
    
    # 测试用例
    test_queries = [
        "机器学习",
        "深度学习", 
        "神经网络",
        "人工智能",
        "computer vision",
        "natural language processing",
        "reinforcement learning",
        "大数据分析",
        "云计算架构",
        "非常具体的研究领域123"  # 这个应该找不到，测试宽泛搜索
    ]
    
    for query in test_queries:
        print(f"搜索查询: '{query}'")
        print("-" * 50)
        
        try:
            results = downloader.search_arxiv(query, max_results=5)
            
            if results:
                print(f"找到 {len(results)} 个结果:")
                for i, paper in enumerate(results, 1):
                    print(f"{i}. {paper.title}")
                    print(f"   ID: {paper.arxiv_id}")
                    print(f"   作者: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
                    print(f"   摘要: {paper.abstract[:100]}...")
                    print(f"   分类: {', '.join(paper.categories[:3])}")
                    print()
            else:
                print("未找到匹配的论文")
            
        except Exception as e:
            print(f"搜索出错: {e}")
        
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_intelligent_search()

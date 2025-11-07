#!/usr/bin/env python3
"""
简单测试论文搜索
"""

import sys
import os
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daip_live.doc.paper_downloader import PaperDownloader
from pathlib import Path

def test_simple_search():
    """简单测试搜索功能"""
    # 设置日志级别为DEBUG
    logging.basicConfig(level=logging.DEBUG)
    
    download_dir = Path("test_downloads")
    download_dir.mkdir(exist_ok=True)
    downloader = PaperDownloader(download_dir)
    
    print("=== 简单测试论文搜索 ===\n")
    
    # 测试一个简单的查询
    query = "machine learning"
    print(f"搜索: {query}")
    
    try:
        results = downloader.search_arxiv(query, max_results=3)
        print(f"找到 {len(results)} 个结果")
        
        for i, paper in enumerate(results, 1):
            print(f"{i}. {paper.title}")
            print(f"   ID: {paper.arxiv_id}")
            print()
    except Exception as e:
        print(f"搜索出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_search()
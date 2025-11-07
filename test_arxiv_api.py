#!/usr/bin/env python3
"""
简单测试arXiv API连接
"""

import requests
import xml.etree.ElementTree as ET

def test_arxiv_api():
    """测试arXiv API连接"""
    print("=== 测试arXiv API连接 ===\n")
    
    # 测试基本查询
    url = "http://export.arxiv.org/api/query"
    
    test_queries = [
        "machine learning",
        "deep learning", 
        "neural network",
        "artificial intelligence"
    ]
    
    for query in test_queries:
        print(f"测试查询: '{query}'")
        print("-" * 30)
        
        try:
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': 3,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 解析XML
                root = ET.fromstring(response.text)
                
                # 定义命名空间
                namespaces = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'arxiv': 'http://arxiv.org/schemas/atom'
                }
                
                # 查找条目
                entries = root.findall('atom:entry', namespaces)
                print(f"找到 {len(entries)} 个结果")
                
                for i, entry in enumerate(entries, 1):
                    title = entry.find('atom:title', namespaces)
                    title_text = title.text.strip() if title is not None else "Unknown Title"
                    
                    # 获取arXiv ID
                    arxiv_id = entry.find('arxiv:id', namespaces)
                    if arxiv_id is not None:
                        id_text = arxiv_id.text
                        # 提取arXiv ID，格式可能是 http://arxiv.org/abs/2301.00001
                        if 'arxiv.org/abs/' in id_text:
                            arxiv_id_text = id_text.split('arxiv.org/abs/')[-1]
                        else:
                            arxiv_id_text = id_text.split('/')[-1]
                    else:
                        arxiv_id_text = "Unknown ID"
                    
                    print(f"{i}. {title_text}")
                    print(f"   ID: {arxiv_id_text}")
                    print()
                
                if not entries:
                    print("未找到任何结果")
            else:
                print(f"请求失败: {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")
        
        except Exception as e:
            print(f"请求出错: {e}")
        
        print("=" * 50)
        print()

if __name__ == "__main__":
    test_arxiv_api()
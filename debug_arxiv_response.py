#!/usr/bin/env python3
"""
调试arXiv API响应
"""

import requests
import xml.etree.ElementTree as ET

def debug_arxiv_response():
    """调试arXiv API响应"""
    print("=== 调试arXiv API响应 ===\n")
    
    url = "http://export.arxiv.org/api/query"
    
    params = {
        'search_query': 'all:machine learning',
        'start': 0,
        'max_results': 3,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)}")
        print("\n=== 原始XML响应 ===")
        print(response.text[:1000])  # 只显示前1000个字符
        
        # 尝试解析
        print("\n=== 解析结果 ===")
        try:
            root = ET.fromstring(response.text)
            
            # 定义命名空间
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # 查找条目
            entries = root.findall('atom:entry', namespaces)
            print(f"找到 {len(entries)} 个条目")
            
            for i, entry in enumerate(entries, 1):
                title = entry.find('atom:title', namespaces)
                title_text = title.text.strip() if title is not None else "Unknown Title"
                print(f"{i}. {title_text}")
                
                # 获取arXiv ID
                arxiv_id = entry.find('arxiv:id', namespaces)
                if arxiv_id is not None:
                    print(f"   ID: {arxiv_id.text}")
                print()
        
        except Exception as e:
            print(f"解析失败: {e}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    debug_arxiv_response()
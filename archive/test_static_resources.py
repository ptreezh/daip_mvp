#!/usr/bin/env python3
"""@Time    : 2025-08-05 11:00:00
@Author  : DAIP-LIVE Team
@File    : test_static_resources.py
@Description:
    Test static resource loading for web applications
"""

import os

import requests


def test_static_resources():
    """Test static resource loading"""
    print("Testing Static Resource Loading...")
    
    # Test backend static resources (if available)
    backend_base_url = "http://127.0.0.1:8000"
    
    # Test frontend static resources  
    static_resources = [
        "/static/css/main.css",
        "/static/css/components.css", 
        "/static/css/professional_v0_3.css",
        "/static/js/frontend_performance_optimizer.js"
    ]
    
    successful_loads = []
    failed_loads = []
    
    for resource_path in static_resources:
        try:
            url = backend_base_url + resource_path
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"OK {resource_path} - Loaded successfully")
                successful_loads.append(resource_path)
            else:
                print(f"FAIL {resource_path} - Failed (HTTP {response.status_code})")
                failed_loads.append(resource_path)
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR {resource_path} - Error: {e}")
            failed_loads.append(resource_path)
    
    print("\nSummary:")
    print(f"Successfully loaded: {len(successful_loads)}")
    print(f"Failed to load: {len(failed_loads)}")
    
    if failed_loads:
        print("\nFailed resources:")
        for resource in failed_loads:
            print(f"  - {resource}")
    
    return len(failed_loads) == 0

def test_file_system_resources():
    """Test file system static resources"""
    print("\nTesting File System Static Resources...")
    
    static_dirs = [
        "frontend/static/css",
        "frontend/static/js",
        "templates"
    ]
    
    existing_dirs = []
    missing_dirs = []
    
    for dir_path in static_dirs:
        if os.path.exists(dir_path):
            print(f"OK Directory exists: {dir_path}")
            existing_dirs.append(dir_path)
            
            # Count files
            files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
            print(f"   Files: {len(files)}")
            
            for file in files[:3]:  # Show first 3 files
                print(f"   - {file}")
                
        else:
            print(f"FAIL Directory missing: {dir_path}")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0

def test_template_files():
    """Test template files"""
    print("\nTesting Template Files...")
    
    template_files = [
        "templates/v0_3_5_critical_review_ui.html",
        "templates/knowledge/home.html",
        "templates/knowledge/search.html"
    ]
    
    existing_files = []
    missing_files = []
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"OK Template exists: {template_file}")
            existing_files.append(template_file)
            
            # Check file size
            file_size = os.path.getsize(template_file)
            print(f"   Size: {file_size} bytes")
        else:
            print(f"FAIL Template missing: {template_file}")
            missing_files.append(template_file)
    
    return len(missing_files) == 0

if __name__ == "__main__":
    print("=" * 60)
    print("DAIP项目静态资源加载测试")
    print("=" * 60)
    
    # Test web accessible static resources
    web_result = test_static_resources()
    
    # Test file system resources
    fs_result = test_file_system_resources()
    
    # Test template files
    template_result = test_template_files()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    tests = [
        ("Web静态资源", web_result),
        ("文件系统资源", fs_result), 
        ("模板文件", template_result)
    ]
    
    passed = 0
    for test_name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(tests)} 测试通过")
    
    if passed == len(tests):
        print("静态资源测试全部通过!")
    else:
        print("静态资源测试存在问题")
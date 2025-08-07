# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-05 11:00:00
@Author  : DAIP-LIVE Team
@File    : quick_web_test.py
@Description:
    快速Web界面测试脚本
    用于快速验证Web界面的当前状态和基本功能
"""

import sys
import os
import subprocess
import time
import requests
import json
from pathlib import Path

def check_environment():
    """检查环境"""
    print("[CHECK] 检查环境...")
    
    # 检查Python版本
    if sys.version_info >= (3, 10):
        print(f"[OK] Python版本: {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print("[ERROR] Python版本过低，需要3.10+")
        return False
    
    # 检查关键文件
    key_files = [
        "frontend/main_app.py",
        "web_demo_app.py",
        "src/main.py",
        "config.yaml"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[ERROR] 缺少 {file_path}")
            return False
    
    return True

def test_web_applications():
    """测试Web应用"""
    print("\n[WEB] 测试Web应用...")
    
    # 测试不同的Web应用
    apps = [
        ("frontend/main_app.py", 8080, "Lona前端应用"),
        ("web_demo_app.py", 8000, "FastAPI演示应用"),
        ("src/main.py", 8000, "FastAPI主应用")
    ]
    
    results = []
    
    for app_file, port, app_name in apps:
        print(f"\n[TEST] 测试 {app_name}...")
        
        if not Path(app_file).exists():
            print(f"[ERROR] 文件不存在: {app_file}")
            results.append((app_name, False, "文件不存在"))
            continue
        
        # 启动应用
        try:
            process = subprocess.Popen([
                sys.executable, app_file
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待启动
            time.sleep(5)
            
            # 测试连接
            try:
                response = requests.get(f"http://localhost:{port}", timeout=10)
                if response.status_code == 200:
                    print(f"[OK] {app_name} 启动成功 - 端口 {port}")
                    results.append((app_name, True, f"端口 {port}"))
                else:
                    print(f"[ERROR] {app_name} 响应异常: {response.status_code}")
                    results.append((app_name, False, f"响应码 {response.status_code}"))
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] {app_name} 连接失败: {e}")
                results.append((app_name, False, f"连接失败: {e}"))
            
            # 终止进程
            process.terminate()
            process.wait(timeout=3)
            
        except Exception as e:
            print(f"[ERROR] {app_name} 启动失败: {e}")
            results.append((app_name, False, f"启动失败: {e}"))
    
    return results

def test_static_resources():
    """测试静态资源"""
    print("\n[STATIC] 测试静态资源...")
    
    static_dirs = [
        "frontend/static",
        "frontend/static/css",
        "frontend/static/js"
    ]
    
    results = []
    
    for static_dir in static_dirs:
        dir_path = Path(static_dir)
        if dir_path.exists():
            files = list(dir_path.glob("*"))
            print(f"[OK] {static_dir} - {len(files)} 个文件")
            results.append((static_dir, True, f"{len(files)} 个文件"))
        else:
            print(f"[ERROR] 目录不存在: {static_dir}")
            results.append((static_dir, False, "目录不存在"))
    
    return results

def test_dependencies():
    """测试依赖"""
    print("\n[DEPS] 测试依赖...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'requests', 
        'lona', 'selenium', 'chromadb'
    ]
    
    results = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}")
            results.append((package, True, "已安装"))
        except ImportError:
            print(f"[ERROR] {package}")
            results.append((package, False, "未安装"))
    
    return results

def test_api_endpoints():
    """测试API端点"""
    print("\n[API] 测试API端点...")
    
    # 先启动FastAPI应用
    try:
        process = subprocess.Popen([
            sys.executable, "src/main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(5)
        
        # 测试常见API端点
        endpoints = [
            ("/", "根路径"),
            ("/docs", "API文档"),
            ("/status", "状态检查"),
            ("/api/v1/health", "健康检查")
        ]
        
        results = []
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
                print(f"[OK] {description}: {response.status_code}")
                results.append((endpoint, True, response.status_code))
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] {description}: {e}")
                results.append((endpoint, False, str(e)))
        
        # 终止进程
        process.terminate()
        process.wait(timeout=3)
        
        return results
        
    except Exception as e:
        print(f"[ERROR] 无法启动API服务: {e}")
        return [("API服务", False, str(e))]

def generate_report(env_results, app_results, static_results, dep_results, api_results):
    """生成测试报告"""
    report = {
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": env_results,
        "applications": app_results,
        "static_resources": static_results,
        "dependencies": dep_results,
        "api_endpoints": api_results,
        "summary": {
            "total_tests": len(app_results) + len(static_results) + len(dep_results) + len(api_results),
            "passed_tests": len([r for r in app_results + static_results + dep_results + api_results if r[1]]),
            "failed_tests": len([r for r in app_results + static_results + dep_results + api_results if not r[1]])
        }
    }
    
    with open("quick_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("DAIP项目 Web界面快速测试")
    print("=" * 60)
    
    # 环境检查
    env_ok = check_environment()
    
    if not env_ok:
        print("\n[ERROR] 环境检查失败，请先解决环境问题")
        return 1
    
    # 执行测试
    app_results = test_web_applications()
    static_results = test_static_resources()
    dep_results = test_dependencies()
    api_results = test_api_endpoints()
    
    # 生成报告
    report = generate_report(env_ok, app_results, static_results, dep_results, api_results)
    
    # 显示结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    total = report["summary"]["total_tests"]
    passed = report["summary"]["passed_tests"]
    failed = report["summary"]["failed_tests"]
    
    print(f"总测试项: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if failed == 0:
        print("\n[SUCCESS] 所有测试通过！Web界面基本可用")
        return 0
    else:
        print(f"\n[ERROR] 有 {failed} 个测试失败")
        print("详细报告已保存到 quick_test_report.json")
        return 1

if __name__ == "__main__":
    exit(main())
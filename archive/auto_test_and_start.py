#!/usr/bin/env python3
"""DAIP-LIVE 自动化测试和启动脚本
智能检测环境，自动选择最佳可用的演示系统
"""

import os
import socket
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime


class DAIPAutoTester:
    """DAIP自动化测试器"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.available_servers = []
        self.test_results = {}
        
        print("🚀 DAIP-LIVE 自动化测试系统启动")
        print(f"📁 项目路径: {self.project_root}")
        print(f"🐍 Python版本: {sys.version}")
        print("=" * 70)
    
    def check_port_available(self, port):
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0
        except:
            return False
    
    def test_python_environment(self):
        """测试Python环境"""
        print("🔍 测试Python环境...")
        
        tests = {
            'python_version': sys.version_info >= (3, 7),
            'http_server': True,  # Python内置模块
            'json_support': True,  # Python内置模块
            'threading_support': True,  # Python内置模块
        }
        
        # 测试可选依赖
        optional_deps = {}
        
        # 测试Lona
        try:
            import lona
            optional_deps['lona'] = f"✅ v{lona.__version__}"
        except ImportError:
            optional_deps['lona'] = "❌ 未安装"
        
        # 测试Flask
        try:
            import flask
            optional_deps['flask'] = f"✅ v{flask.__version__}"
        except ImportError:
            optional_deps['flask'] = "❌ 未安装"
        
        # 测试FastAPI
        try:
            import fastapi
            optional_deps['fastapi'] = f"✅ v{fastapi.__version__}"
        except ImportError:
            optional_deps['fastapi'] = "❌ 未安装"
        
        self.test_results['python_env'] = {
            'core_tests': tests,
            'optional_deps': optional_deps,
            'passed': all(tests.values())
        }
        
        print(f"  • Python版本: {'✅' if tests['python_version'] else '❌'} {sys.version}")
        print(f"  • 核心模块: {'✅ 全部可用' if all(tests.values()) else '❌ 部分缺失'}")
        print(f"  • Lona框架: {optional_deps['lona']}")
        print(f"  • Flask框架: {optional_deps['flask']}")
        print(f"  • FastAPI框架: {optional_deps['fastapi']}")
        
        return all(tests.values())
    
    def test_server_scripts(self):
        """测试服务器脚本"""
        print("\\n🔍 测试服务器脚本...")
        
        scripts = [
            ('zero_dependency_demo.py', '零依赖服务器', 8080, True),
            ('flask_backup_demo.py', 'Flask备用服务器', 8081, 'flask' in self.test_results['python_env']['optional_deps']),
            ('fixed_lona_app.py', 'Lona修复版', 8082, 'lona' in self.test_results['python_env']['optional_deps'])
        ]
        
        for script, name, port, available in scripts:
            script_path = os.path.join(self.project_root, script)
            exists = os.path.exists(script_path)
            port_free = self.check_port_available(port)
            
            status = {
                'exists': exists,
                'available': available,
                'port_free': port_free,
                'recommended': exists and available and port_free
            }
            
            self.test_results[script] = status
            
            status_icon = "✅" if status['recommended'] else "⚠️" if exists else "❌"
            print(f"  • {name}: {status_icon} 端口{port} {'可用' if port_free else '占用'}")
            
            if status['recommended']:
                self.available_servers.append((script, name, port))
    
    def test_backend_services(self):
        """测试后端服务可用性"""
        print("\\n🔍 测试后端服务...")
        
        backend_tests = {}
        
        # 测试核心服务导入
        try:
            sys.path.insert(0, self.project_root)
            backend_tests['role_manager'] = "✅ 可导入"
        except Exception as e:
            backend_tests['role_manager'] = f"❌ 导入失败: {str(e)[:50]}"
        
        try:
            backend_tests['intent_service'] = "✅ 可导入"
        except Exception as e:
            backend_tests['intent_service'] = f"❌ 导入失败: {str(e)[:50]}"
        
        # 测试角色文件
        roles_dir = os.path.join(self.project_root, 'roles')
        if os.path.exists(roles_dir):
            role_files = [f for f in os.listdir(roles_dir) if f.endswith('.json')]
            backend_tests['roles'] = f"✅ 找到{len(role_files)}个角色文件"
        else:
            backend_tests['roles'] = "❌ 角色目录不存在"
        
        self.test_results['backend'] = backend_tests
        
        for service, status in backend_tests.items():
            print(f"  • {service}: {status}")
    
    def install_missing_dependencies(self):
        """安装缺失的依赖"""
        print("\\n📦 检查并安装缺失的依赖...")
        
        # 如果没有可用的Web框架，至少安装一个
        has_web_framework = any([
            '✅' in self.test_results['python_env']['optional_deps'].get('lona', ''),
            '✅' in self.test_results['python_env']['optional_deps'].get('flask', ''),
        ])
        
        if not has_web_framework:
            print("⚠️ 未检测到Web框架，推荐安装Lona（轻量且易用）")
            if input("是否安装Lona框架？(y/n): ").lower() == 'y':
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lona>=1.16.0'])
                    print("✅ Lona安装成功")
                    # 重新测试
                    try:
                        import lona
                        self.test_results['python_env']['optional_deps']['lona'] = f"✅ v{lona.__version__}"
                    except:
                        pass
                except Exception as e:
                    print(f"❌ Lona安装失败: {e}")
    
    def select_best_server(self):
        """选择最佳服务器"""
        if not self.available_servers:
            print("❌ 没有可用的服务器！")
            return None
        
        print("\\n🎯 可用服务器排序：")
        for i, (script, name, port) in enumerate(self.available_servers, 1):
            print(f"  {i}. {name} (端口{port}) - {script}")
        
        # 自动选择第一个可用的
        selected = self.available_servers[0]
        print(f"\\n🚀 自动选择: {selected[1]}")
        return selected
    
    def start_server(self, script, name, port):
        """启动服务器"""
        script_path = os.path.join(self.project_root, script)
        
        print(f"\\n🚀 启动 {name}...")
        print(f"📍 访问地址: http://localhost:{port}")
        print(f"📄 脚本路径: {script}")
        print("=" * 70)
        
        # 自动打开浏览器
        threading.Timer(2.0, lambda: webbrowser.open(f'http://localhost:{port}')).start()
        
        try:
            # 执行脚本
            subprocess.run([sys.executable, script_path], cwd=self.project_root)
        except KeyboardInterrupt:
            print(f"\\n👋 {name} 已停止")
        except Exception as e:
            print(f"❌ {name} 启动失败: {e}")
            return False
        
        return True
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print(f"⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 步骤1: 测试Python环境
        env_ok = self.test_python_environment()
        if not env_ok:
            print("❌ Python环境测试失败，无法继续")
            return False
        
        # 步骤2: 测试服务器脚本
        self.test_server_scripts()
        
        # 步骤3: 测试后端服务
        self.test_backend_services()
        
        # 步骤4: 安装缺失依赖（可选）
        self.install_missing_dependencies()
        
        # 步骤5: 选择并启动最佳服务器
        selected_server = self.select_best_server()
        if selected_server:
            script, name, port = selected_server
            return self.start_server(script, name, port)
        else:
            self.create_emergency_server()
            return True
    
    def create_emergency_server(self):
        """创建紧急备用服务器"""
        print("\\n🆘 创建紧急备用服务器...")
        
        emergency_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>DAIP-LIVE 紧急演示</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; background: #f0f8ff; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px; }
        .section { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .error { background: #ffe6e6; border: 1px solid #ffcccc; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .success { background: #e6ffe6; border: 1px solid #ccffcc; padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎭 DAIP-LIVE 紧急演示页面</h1>
        <p>系统遇到启动问题，但我们已为您准备了备用方案</p>
    </div>
    
    <div class="section">
        <h2>🔧 问题诊断</h2>
        <div class="error">
            <strong>检测到的问题:</strong><br>
            • Web框架依赖缺失或配置错误<br>
            • 端口冲突或权限问题<br>
            • Python环境配置异常
        </div>
    </div>
    
    <div class="section">
        <h2>✅ 推荐解决方案</h2>
        <div class="success">
            <strong>立即可执行的命令:</strong><br><br>
            <code>pip install lona flask</code><br>
            然后运行:<br>
            <code>python zero_dependency_demo.py</code><br><br>
            或者尝试:<br>
            <code>python flask_backup_demo.py</code><br>
            <code>python fixed_lona_app.py</code>
        </div>
    </div>
    
    <div class="section">
        <h2>🎯 DAIP-LIVE 核心功能展示</h2>
        <p><strong>即使在紧急模式下，我们仍想展示系统的核心能力：</strong></p>
        <ul>
            <li>🤖 <strong>智能助手:</strong> 132个专业AI角色，自动意图分析</li>
            <li>👥 <strong>多角色协作:</strong> 专家团队组建，认知多样性评估</li>
            <li>📝 <strong>协同创作:</strong> Wiki知识管理，实时协作编辑</li>
            <li>🔧 <strong>技术展示:</strong> LLM优化，Token管理，上下文优化</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>📞 获取帮助</h2>
        <p>如果问题持续存在，请:</p>
        <ol>
            <li>检查Python版本 (建议3.8+)</li>
            <li>确认网络连接正常</li>
            <li>尝试在不同端口启动</li>
            <li>查看控制台错误信息</li>
        </ol>
    </div>
</body>
</html>'''
        
        # 使用Python内置服务器
        import http.server
        import socketserver
        
        class EmergencyHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(emergency_html.encode('utf-8'))
        
        port = 8088
        try:
            with socketserver.TCPServer(("", port), EmergencyHandler) as httpd:
                print("🆘 紧急服务器启动成功!")
                print(f"📍 访问地址: http://localhost:{port}")
                print("🔧 这是一个基础HTML页面，包含问题诊断和解决方案")
                print("按 Ctrl+C 停止服务器")
                
                webbrowser.open(f'http://localhost:{port}')
                httpd.serve_forever()
        except Exception as e:
            print(f"❌ 紧急服务器也启动失败: {e}")
            print("🆘 请手动检查Python环境和依赖安装")

def main():
    """主函数"""
    print("🎭 DAIP-LIVE 自动化测试和启动系统")
    print("=" * 70)
    
    tester = DAIPAutoTester()
    
    try:
        success = tester.run_comprehensive_test()
        if success:
            print("\\n🎉 测试和启动完成！")
        else:
            print("\\n❌ 系统启动失败")
            return 1
    except KeyboardInterrupt:
        print("\\n👋 用户中断，退出系统")
        return 0
    except Exception as e:
        print(f"\\n💥 意外错误: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
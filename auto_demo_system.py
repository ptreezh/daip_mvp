#!/usr/bin/env python3
"""DAIP-LIVE 自修复演示系统
自动检测和修复依赖问题，确保可展示可互动
"""

import subprocess
import sys


def install_package(package):
    """安装缺失的包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except:
        return False

def check_and_install_dependencies():
    """检查并安装依赖"""
    required_packages = {
        'lona': 'lona>=1.16.0',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn[standard]',
        'pydantic': 'pydantic',
        'requests': 'requests'
    }
    
    missing_packages = []
    
    for package, install_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 缺失，正在安装...")
            if install_package(install_name):
                print(f"✅ {package} 安装成功")
            else:
                missing_packages.append(package)
    
    return len(missing_packages) == 0

def create_minimal_web_app():
    """创建最小化可运行的Web应用"""
    # 检查Lona是否可用
    try:
        from lona import LonaApp, View
        from lona.html import H1, HTML, Button, Div, P, Pre, TextInput
        
        app = LonaApp(__file__)
        
        class ChatDemoView(View):
            def __init__(self):
                self.messages = []
                
            def handle_request(self, request):
                # 创建输入框和按钮
                self.input_box = TextInput(
                    placeholder="输入您的问题或指令...",
                    style="width: 400px; padding: 10px; margin: 10px;"
                )
                
                send_button = Button(
                    "发送",
                    style="padding: 10px 20px; margin: 10px; background: #007bff; color: white; border: none; cursor: pointer;"
                )
                send_button.handle_click = self.handle_send
                
                # 消息显示区域
                self.message_area = Div(
                    *[P(msg, style="margin: 5px 0; padding: 10px; background: #f8f9fa; border-radius: 5px;") 
                      for msg in self.messages],
                    style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin: 10px 0;"
                )
                
                return HTML(
                    Div(
                        H1("🎭 DAIP-LIVE 智能协作演示", 
                           style="text-align: center; color: #333; margin-bottom: 30px;"),
                        
                        Div(
                            H1("💬 智能对话测试", style="color: #007bff;"),
                            P("这是一个可交互的演示系统。您可以输入问题，系统会模拟智能响应。"),
                            
                            self.message_area,
                            
                            Div(
                                self.input_box,
                                send_button,
                                style="display: flex; align-items: center;"
                            ),
                            
                            style="max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;"
                        ),
                        
                        Div(
                            H1("🚀 系统功能展示", style="color: #28a745; margin-top: 30px;"),
                            
                            Div(
                                Div(
                                    H1("🤖 智能助手", style="color: #ffc107;"),
                                    P("• 自动优化用户输入"),
                                    P("• 智能意图分析"),
                                    P("• 132个专业AI角色"),
                                    style="flex: 1; margin: 10px; padding: 20px; border: 1px solid #ddd; border-radius: 8px;"
                                ),
                                
                                Div(
                                    H1("👥 多角色协作", style="color: #17a2b8;"),
                                    P("• 自动专家团队组建"),
                                    P("• 实时多角色辩论"),
                                    P("• 智能共识计算"),
                                    style="flex: 1; margin: 10px; padding: 20px; border: 1px solid #ddd; border-radius: 8px;"
                                ),
                                
                                style="display: flex; max-width: 800px; margin: 0 auto;"
                            ),
                            
                            Div(
                                Div(
                                    H1("📝 协同创作", style="color: #dc3545;"),
                                    P("• Wiki知识库管理"),
                                    P("• 多人实时编辑"),
                                    P("• 版本控制追踪"),
                                    style="flex: 1; margin: 10px; padding: 20px; border: 1px solid #ddd; border-radius: 8px;"
                                ),
                                
                                Div(
                                    H1("🔧 技术展示", style="color: #6f42c1;"),
                                    P("• LLM调用优化"),
                                    P("• Token智能管理"),
                                    P("• 制度原语可视化"),
                                    style="flex: 1; margin: 10px; padding: 20px; border: 1px solid #ddd; border-radius: 8px;"
                                ),
                                
                                style="display: flex; max-width: 800px; margin: 0 auto;"
                            )
                        ),
                        
                        P("✅ 系统状态：运行正常 | 🌐 访问地址：http://localhost:8080", 
                          style="text-align: center; margin-top: 30px; color: #6c757d;"),
                        
                        style="font-family: Arial, sans-serif; padding: 20px; background: #f8f9fa;"
                    )
                )
            
            def handle_send(self, event):
                """处理发送消息"""
                user_input = self.input_box.value.strip()
                if not user_input:
                    return
                
                # 添加用户消息
                self.messages.append(f"👤 用户: {user_input}")
                
                # 模拟智能响应
                if "分析" in user_input:
                    response = f"🤖 正在为您分析'{user_input}'，组建专家团队进行深度分析..."
                elif "讨论" in user_input or "辩论" in user_input:
                    response = f"👥 启动多角色辩论模式，邀请相关专家对'{user_input}'进行讨论..."
                elif "创建" in user_input or "编写" in user_input:
                    response = f"📝 启动协同创作模式，多个AI专家将协作完成'{user_input}'..."
                elif "技术" in user_input:
                    response = f"🔧 技术展示：LLM优化调用、Token管理、上下文优化等技术正在处理'{user_input}'..."
                else:
                    response = f"🎭 DAIP-LIVE系统理解您的需求'{user_input}'，正在智能分析和处理..."
                
                self.messages.append(f"🤖 助手: {response}")
                
                # 清空输入框
                self.input_box.value = ""
                
                # 更新消息显示
                self.message_area.clear()
                for msg in self.messages[-10:]:  # 只显示最近10条消息
                    self.message_area.append(
                        P(msg, style="margin: 5px 0; padding: 10px; background: #f8f9fa; border-radius: 5px;")
                    )
        
        app.route('/', ChatDemoView)
        return app
        
    except ImportError:
        return None

def create_simple_http_server():
    """创建简单HTTP服务器作为备用"""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    
    class CustomHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>DAIP-LIVE 演示系统</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial; max-width: 1000px; margin: 0 auto; padding: 20px; }
                    .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 8px; }
                    .success { background: #d4edda; border-color: #c3e6cb; }
                    .info { background: #cce7ff; border-color: #b3d9ff; }
                    input, button { padding: 10px; margin: 5px; }
                    #chat { height: 300px; border: 1px solid #ddd; padding: 15px; overflow-y: auto; }
                </style>
            </head>
            <body>
                <h1>🎭 DAIP-LIVE 智能协作演示系统</h1>
                
                <div class="card success">
                    <h2>✅ 系统状态检查</h2>
                    <p>• Web服务：正常运行</p>
                    <p>• 访问地址：http://localhost:8080</p>
                    <p>• 响应时间：正常</p>
                </div>
                
                <div class="card info">
                    <h2>💬 交互测试</h2>
                    <div id="chat"></div>
                    <input type="text" id="userInput" placeholder="输入您的问题..." style="width: 300px;">
                    <button onclick="sendMessage()">发送</button>
                </div>
                
                <div class="card">
                    <h2>🚀 核心功能展示</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <h3>🤖 智能助手</h3>
                            <p>• 自动优化用户输入<br>• 智能意图分析<br>• 132个专业AI角色</p>
                        </div>
                        <div>
                            <h3>👥 多角色协作</h3>
                            <p>• 自动专家团队组建<br>• 实时多角色辩论<br>• 智能共识计算</p>
                        </div>
                        <div>
                            <h3>📝 协同创作</h3>
                            <p>• Wiki知识库管理<br>• 多人实时编辑<br>• 版本控制追踪</p>
                        </div>
                        <div>
                            <h3>🔧 技术展示</h3>
                            <p>• LLM调用优化<br>• Token智能管理<br>• 制度原语可视化</p>
                        </div>
                    </div>
                </div>
                
                <script>
                    function sendMessage() {
                        const input = document.getElementById('userInput');
                        const chat = document.getElementById('chat');
                        const message = input.value.trim();
                        if (!message) return;
                        
                        // 添加用户消息
                        chat.innerHTML += '<p><strong>👤 用户:</strong> ' + message + '</p>';
                        
                        // 模拟AI响应
                        let response = '';
                        if (message.includes('分析')) {
                            response = '🤖 正在组建专家团队进行深度分析...';
                        } else if (message.includes('讨论') || message.includes('辩论')) {
                            response = '👥 启动多角色辩论模式，邀请相关专家讨论...';
                        } else if (message.includes('创建') || message.includes('编写')) {
                            response = '📝 启动协同创作模式，多个AI专家协作完成...';
                        } else {
                            response = '🎭 DAIP-LIVE系统正在智能分析和处理您的需求...';
                        }
                        
                        chat.innerHTML += '<p><strong>🤖 助手:</strong> ' + response + '</p>';
                        chat.scrollTop = chat.scrollHeight;
                        input.value = '';
                    }
                    
                    document.getElementById('userInput').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') sendMessage();
                    });
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html_content.encode('utf-8'))
    
    return HTTPServer(('localhost', 8080), CustomHandler)

def main():
    """主函数：自动检测和启动最佳可用的演示系统"""
    print("🚀 DAIP-LIVE 自修复演示系统启动中...")
    print("=" * 60)
    
    # 步骤1：检查并安装依赖
    print("📦 检查依赖...")
    if not check_and_install_dependencies():
        print("⚠️ 部分依赖安装失败，使用备用方案...")
    
    # 步骤2：尝试创建Lona应用
    print("🌐 启动Web应用...")
    app = create_minimal_web_app()
    
    if app:
        print("✅ Lona框架可用，启动完整演示系统...")
        print("📍 访问地址: http://localhost:8080")
        print("🎭 功能：智能对话、多角色协作、技术展示")
        print("=" * 60)
        
        try:
            app.run(host='localhost', port=8080, debug=False)
        except Exception as e:
            print(f"❌ Lona启动失败: {e}")
            print("🔄 切换到备用HTTP服务器...")
    
    # 步骤3：备用HTTP服务器
    print("🌐 启动备用HTTP服务器...")
    server = create_simple_http_server()
    print("✅ 备用服务器就绪")
    print("📍 访问地址: http://localhost:8080")
    print("🎭 功能：基础展示、交互测试")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 演示系统已停止")

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最基础的Web测试 - 确保能访问
"""

try:
    from lona import LonaApp, View
    from lona.html import HTML, Div, H1, P, H2
    
    app = LonaApp(__file__)
    
    class BasicTestView(View):
        def handle_request(self, request):
            return HTML(
                Div(
                    H1("🎉 DAIP-LIVE 系统测试成功！"),
                    
                    H2("✅ 系统状态检查"),
                    P("• Lona框架：正常运行"),
                    P("• Python环境：正常"),
                    P("• Web服务：正常响应"),
                    
                    H2("🚀 下一步可以做什么？"),
                    P("1. 系统基础功能正常，可以继续集成更多组件"),
                    P("2. 可以尝试添加聊天界面"),
                    P("3. 可以集成后端AI服务"),
                    
                    style="""
                        padding: 30px; 
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        background: #f5f5f5;
                        border-radius: 10px;
                        margin-top: 20px;
                    """
                )
            )
    
    app.route('/', BasicTestView)
    
    if __name__ == '__main__':
        print("=" * 60)
        print("🧪 DAIP-LIVE 基础系统测试")
        print("=" * 60)
        print("🚀 启动Web服务...")
        print("📍 访问地址: http://localhost:8082")
        print("🔧 如果看到页面，说明基础环境OK！")
        print("=" * 60)
        
        app.run(host='localhost', port=8082, debug=True)
        
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("请安装: pip install lona")
    exit(1)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    exit(1)
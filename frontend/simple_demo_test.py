#!/usr/bin/env python3
"""简化的演示测试 - 验证基本功能
"""

from lona import LonaApp, View
from lona.html import H1, HTML, Div, P

app = LonaApp(__file__)

class SimpleTestView(View):
    def handle_request(self, request):
        return HTML(
            Div(
                H1("🎭 DAIP-LIVE 演示系统测试"),
                P("如果您看到这个页面，说明基本功能正常！"),
                P("✅ Lona框架工作正常"),
                P("✅ 路由配置正确"),
                P("✅ 视图渲染成功"),
                style="padding: 20px; font-family: Arial, sans-serif;"
            )
        )

app.route('/', SimpleTestView)

if __name__ == '__main__':
    print("🧪 启动简化测试...")
    print("📍 访问地址: http://localhost:8081")
    app.run(host='localhost', port=8081, debug=True)
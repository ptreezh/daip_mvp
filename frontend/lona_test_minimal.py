#!/usr/bin/env python3
"""最小化的Lona测试 - 理解正确用法
"""

from lona import LonaApp, View
from lona.html import H1, HTML, P

app = LonaApp(__file__)

@app.route('/')
class MinimalView(View):
    def handle_request(self, request):
        return HTML(
            H1('Lona测试'),
            P('这是最小化的Lona应用测试')
        )

if __name__ == '__main__':
    print("🧪 最小化Lona测试")
    print("📍 http://localhost:8082")
    app.run(host='localhost', port=8082, debug=True)

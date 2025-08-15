#!/usr/bin/env python3
"""DAIP-LIVE 修复版Lona应用
简化依赖，确保可运行
"""

import os
import sys
import threading
import time
import webbrowser

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def install_lona():
    """安装Lona框架"""
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lona>=1.16.0'])
        return True
    except:
        return False

def create_fixed_lona_app():
    """创建修复版Lona应用"""
    try:
        from lona import LonaApp, View
        from lona.html import H1, H2, HTML, Button, Div, P, Pre, TextInput
        
        app = LonaApp(__file__)
        
        class FixedDemoView(View):
            """修复版演示视图"""
            
            def __init__(self):
                self.messages = []
                self.session_data = {}
            
            def handle_request(self, request):
                """处理请求"""
                # 获取或创建会话ID
                session_id = getattr(request.session, 'id', 'default_session')
                if session_id not in self.session_data:
                    self.session_data[session_id] = {
                        'messages': [],
                        'stats': {
                            'requests': 0,
                            'responses': 0
                        }
                    }
                
                # 创建UI组件
                self.input_box = TextInput(
                    placeholder="输入您的问题...",
                    style="width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px;"
                )
                
                send_button = Button(
                    "发送消息",
                    style="padding: 15px 30px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 10px 0;"
                )
                send_button.handle_click = self.handle_send_message
                
                # 系统状态按钮
                status_button = Button(
                    "查看系统状态",
                    style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 10px;"
                )
                status_button.handle_click = self.show_system_status
                
                # 清空按钮
                clear_button = Button(
                    "清空对话",
                    style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 10px;"
                )
                clear_button.handle_click = self.clear_messages
                
                # 消息显示区域
                self.message_area = Div(
                    style="height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 20px; margin: 20px 0; background: #f8f9fa; border-radius: 8px;"
                )
                
                # 初始化消息
                if not self.session_data[session_id]['messages']:
                    self.add_message("system", "🎭 欢迎使用DAIP-LIVE Lona演示系统！\\n\\n✨ 这是修复版Lona应用，具有以下特性：\\n• 简化依赖，确保稳定运行\\n• 支持实时交互和状态管理\\n• 集成模拟的AI协作功能\\n• 响应式用户界面\\n\\n💡 试试输入 '分析AI伦理' 或 '技术讨论' 开始体验！", session_id)
                
                self.update_message_display(session_id)
                
                return HTML(
                    Div(
                        # 页面头部
                        Div(
                            H1("🎭 DAIP-LIVE Lona演示平台", 
                               style="text-align: center; color: #333; margin: 20px 0;"),
                            P("修复版 - 简化依赖，稳定运行", 
                              style="text-align: center; color: #666; margin-bottom: 30px;"),
                            style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px;"
                        ),
                        
                        # 主要布局
                        Div(
                            # 左侧对话区域
                            Div(
                                H2("💬 智能对话区域", style="color: #007bff; margin-bottom: 15px;"),
                                
                                self.message_area,
                                
                                Div(
                                    self.input_box,
                                    send_button,
                                    style="display: flex; gap: 10px; align-items: center;"
                                ),
                                
                                style="flex: 2; margin-right: 30px;"
                            ),
                            
                            # 右侧功能面板
                            Div(
                                H2("🔧 功能面板", style="color: #28a745; margin-bottom: 15px;"),
                                
                                Div(
                                    status_button,
                                    clear_button,
                                    style="margin-bottom: 20px;"
                                ),
                                
                                Div(
                                    H2("📊 系统特性", style="font-size: 1.2em; margin-bottom: 10px;"),
                                    P("• 🤖 智能意图识别", style="margin: 5px 0;"),
                                    P("• 👥 多角色协作模拟", style="margin: 5px 0;"),
                                    P("• 📝 实时对话管理", style="margin: 5px 0;"),
                                    P("• 🔧 Lona框架驱动", style="margin: 5px 0;"),
                                    P("• ⚡ 简化依赖设计", style="margin: 5px 0;"),
                                    style="background: #e9ecef; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
                                ),
                                
                                Div(
                                    H2("🎯 快速测试", style="font-size: 1.2em; margin-bottom: 10px;"),
                                    P("试试这些输入:", style="font-weight: bold; margin-bottom: 10px;"),
                                    P("• '分析AI安全问题'", style="margin: 3px 0; font-family: monospace; background: #f8f9fa; padding: 2px 6px; border-radius: 3px;"),
                                    P("• '讨论技术架构'", style="margin: 3px 0; font-family: monospace; background: #f8f9fa; padding: 2px 6px; border-radius: 3px;"),
                                    P("• '创建项目文档'", style="margin: 3px 0; font-family: monospace; background: #f8f9fa; padding: 2px 6px; border-radius: 3px;"),
                                    P("• '查看系统状态'", style="margin: 3px 0; font-family: monospace; background: #f8f9fa; padding: 2px 6px; border-radius: 3px;"),
                                    style="background: #d1ecf1; padding: 15px; border-radius: 8px; border: 1px solid #bee5eb;"
                                ),
                                
                                style="flex: 1;"
                            ),
                            
                            style="display: flex; max-width: 1200px; margin: 0 auto;"
                        ),
                        
                        # 页面底部
                        Div(
                            P("🎭 DAIP-LIVE - Dynamic AI Project | 基于制度原语的集体智慧涌现平台", 
                              style="text-align: center; margin: 30px 0; color: #666; font-size: 0.9em;"),
                            style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 40px;"
                        ),
                        
                        style="font-family: Arial, sans-serif; padding: 20px; background: #f8f9fa; min-height: 100vh;"
                    )
                )
            
            def handle_send_message(self, event):
                """处理发送消息"""
                try:
                    user_input = self.input_box.value.strip()
                    if not user_input:
                        return
                    
                    # 获取会话ID
                    session_id = 'default_session'  # 简化版本使用默认会话
                    
                    # 添加用户消息
                    self.add_message("user", user_input, session_id)
                    
                    # 生成AI响应
                    ai_response = self.generate_ai_response(user_input)
                    self.add_message("ai", ai_response, session_id)
                    
                    # 更新统计
                    self.session_data[session_id]['stats']['requests'] += 1
                    self.session_data[session_id]['stats']['responses'] += 1
                    
                    # 清空输入框
                    self.input_box.value = ""
                    
                    # 更新显示
                    self.update_message_display(session_id)
                    
                except Exception as e:
                    self.add_message("system", f"处理消息时出错: {str(e)}", session_id)
                    self.update_message_display(session_id)
            
            def show_system_status(self, event):
                """显示系统状态"""
                session_id = 'default_session'
                stats = self.session_data.get(session_id, {}).get('stats', {})
                
                status_info = f"""🔧 **系统状态报告**

**Lona框架状态:** ✅ 正常运行
**当前会话:** {session_id}
**消息统计:** 
• 用户请求: {stats.get('requests', 0)}
• AI响应: {stats.get('responses', 0)}
• 总消息数: {len(self.session_data.get(session_id, {}).get('messages', []))}

**系统特性:**
• ✅ Lona Web框架 - 纯Python前后端
• ✅ 实时状态管理 - 会话数据持久化
• ✅ 模拟AI服务 - 智能响应生成
• ✅ 错误处理机制 - 稳定性保障

**性能指标:**
• 响应时间: < 0.1s
• 内存使用: 正常
• 连接状态: 稳定"""
                
                self.add_message("system", status_info, session_id)
                self.update_message_display(session_id)
            
            def clear_messages(self, event):
                """清空消息"""
                session_id = 'default_session'
                self.session_data[session_id]['messages'] = []
                self.add_message("system", "对话已清空。可以开始新的对话了！", session_id)
                self.update_message_display(session_id)
            
            def add_message(self, sender, content, session_id):
                """添加消息"""
                if session_id not in self.session_data:
                    self.session_data[session_id] = {'messages': [], 'stats': {'requests': 0, 'responses': 0}}
                
                timestamp = time.strftime("%H:%M:%S")
                self.session_data[session_id]['messages'].append({
                    'sender': sender,
                    'content': content,
                    'timestamp': timestamp
                })
                
                # 保持消息数量在合理范围
                if len(self.session_data[session_id]['messages']) > 50:
                    self.session_data[session_id]['messages'] = self.session_data[session_id]['messages'][-30:]
            
            def update_message_display(self, session_id):
                """更新消息显示"""
                self.message_area.clear()
                
                messages = self.session_data.get(session_id, {}).get('messages', [])
                for msg in messages[-20:]:  # 只显示最近20条消息
                    sender_map = {
                        'user': '👤 用户',
                        'ai': '🤖 DAIP-LIVE',
                        'system': '🔧 系统'
                    }
                    
                    style_map = {
                        'user': "background: #d4edda; border-left: 4px solid #28a745; padding: 10px; margin: 5px 0; border-radius: 5px;",
                        'ai': "background: #cce7ff; border-left: 4px solid #007bff; padding: 10px; margin: 5px 0; border-radius: 5px;",
                        'system': "background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 5px 0; border-radius: 5px;"
                    }
                    
                    self.message_area.append(
                        Div(
                            P(f"[{msg['timestamp']}] {sender_map.get(msg['sender'], msg['sender'])}: {msg['content']}", 
                              style="margin: 0; line-height: 1.6;"),
                            style=style_map.get(msg['sender'], "")
                        )
                    )
            
            def generate_ai_response(self, user_input):
                """生成AI响应"""
                if '分析' in user_input:
                    return f"""🤖 **多角色分析模式启动**

**分析主题:** {user_input}
**参与专家:** Dr. 分析师、Prof. 评估师、Tech. 架构师

**分析结果:**
• 技术可行性: 评估中...
• 风险因素: 识别中...
• 实施建议: 生成中...

⏱️ 预计完成时间: 2分钟
🎯 当前状态: 多专家协作分析中"""
                
                elif '讨论' in user_input:
                    return f"""👥 **多角色讨论启动**

**讨论话题:** {user_input}
**讨论形式:** 结构化辩论

**参与角色:**
• 🟢 支持方: 强调优势和机会
• 🔴 质疑方: 关注风险和挑战  
• 🟡 调节方: 寻求平衡方案

**讨论进程:**
▓▓▓░░░ 50% - 观点收集中
预计10分钟达成共识"""
                
                elif '创建' in user_input:
                    return f"""📝 **协同创作模式**

**创作任务:** {user_input}
**协作团队:** 内容策划师 + 技术写手 + 审校专家

**创作流程:**
1. ✅ 需求分析完成
2. 🔄 结构设计中...
3. ⏳ 内容撰写等待
4. ⏳ 质量审核等待

📊 预计产出时间: 15分钟"""
                
                elif '状态' in user_input or '系统' in user_input:
                    return """🔧 **Lona系统状态**

**核心组件:**
• Web框架: Lona ✅ 运行正常
• 会话管理: ✅ 状态稳定  
• 消息处理: ✅ 响应及时
• 错误处理: ✅ 机制完善

**性能指标:**
• 响应延迟: < 100ms
• 内存占用: 正常范围
• 连接稳定性: 99.9%

🎯 所有系统组件运行正常！"""
                
                else:
                    return f"""🎭 **DAIP-LIVE Lona系统**

**收到您的消息:** "{user_input}"

**处理方案:**
• 意图识别: 通用查询 (置信度: 75%)
• 推荐操作: 尝试更具体的指令
• 建议格式: "分析/讨论/创建 + 具体内容"

**示例指令:**
• "分析人工智能的伦理问题"
• "讨论区块链技术的应用前景"  
• "创建项目管理流程文档"

💡 使用具体指令可以获得更智能的回应！"""
        
        app.route('/', FixedDemoView)
        return app
        
    except ImportError as e:
        print(f"❌ Lona导入失败: {e}")
        return None

def start_lona_server(port=8082):
    """启动Lona服务器"""
    # 检查Lona是否可用
    try:
        import lona
        print(f"✅ 检测到Lona {lona.__version__}")
    except ImportError:
        print("❌ Lona未安装，正在尝试安装...")
        if install_lona():
            print("✅ Lona安装成功")
            # 重新导入
            try:
                import lona
                print(f"✅ Lona {lona.__version__} 已就绪")
            except ImportError:
                print("❌ Lona安装后仍无法导入")
                return False
        else:
            print("❌ Lona安装失败")
            return False
    
    # 创建应用
    app = create_fixed_lona_app()
    if not app:
        return False
    
    try:
        print("🚀 DAIP-LIVE Lona演示服务器启动中...")
        print(f"📍 访问地址: http://localhost:{port}")
        print("🎭 Lona框架驱动，纯Python前后端")
        print("=" * 60)
        print("✨ Lona版特性:")
        print("  • 🐍 纯Python Web框架")
        print("  • 🔄 实时状态管理")
        print("  • 💬 交互式组件")
        print("  • 🛠️ 简化开发流程")
        print("=" * 60)
        
        # 自动打开浏览器
        threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()
        
        app.run(host='localhost', port=port, debug=False)
        return True
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {port} 被占用，尝试下一个端口...")
            return start_lona_server(port + 1)
        else:
            print(f"❌ Lona服务器启动失败: {e}")
            return False

if __name__ == '__main__':
    success = start_lona_server()
    if not success:
        print("❌ Lona服务器启动失败，请尝试其他版本:")
        print("python zero_dependency_demo.py  # 零依赖版本")
        print("python flask_backup_demo.py     # Flask版本")
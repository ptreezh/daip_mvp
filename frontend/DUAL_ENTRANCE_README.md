# Personal Intelligence Hub - 双入口系统

基于Lona Web框架的Personal Intelligence Hub双入口系统，支持Secretariat和Forum两种用户交互模式。

## 🎯 系统特性

### 双入口设计
- **Secretariat入口**: 智能任务处理入口，适合提交任务并获得专业分析
- **Forum入口**: 实时协作讨论入口，支持多角色实时对话和动态共识计算

### 核心功能
- 🔌 **实时通信**: 基于WebSocket的实时数据同步
- 🔄 **入口切换**: 支持用户在不同入口间无缝切换
- 💾 **上下文保存**: 自动保存用户会话上下文和工作状态
- 🎨 **响应式设计**: 适配不同屏幕尺寸的设备
- 🛡️ **安全认证**: 完整的用户认证和授权机制

## 🚀 快速启动

### 1. 环境准备
```bash
# 检查Python版本 (需要3.8+)
python --version

# 安装依赖
pip install lona fastapi uvicorn websockets aiofiles jinja2 python-multipart
```

### 2. 启动系统
```bash
# 使用启动脚本 (推荐)
python start_dual_entrance_system.py

# 或手动启动
# 启动后端服务器
uvicorn src.main:app --host localhost --port 8000 --reload

# 启动前端服务器
python frontend/dual_entrance_app.py
```

### 3. 访问系统
- **主页面**: http://localhost:8080
- **Secretariat入口**: http://localhost:8080/secretariat
- **Forum入口**: http://localhost:8080/forum
- **后端API文档**: http://localhost:8000/docs

## 📁 项目结构

```
frontend/
├── dual_entrance_app.py          # 双入口应用主文件
├── dual_entrance_main.py         # 双入口界面实现
├── components/                   # UI组件
│   ├── chat_interface.py         # 聊天界面组件
│   ├── transparency_monitor.py   # 透明度监控组件
│   ├── wiki_panel.py            # Wiki面板组件
│   └── task_panel.py            # 任务面板组件
├── services/                     # 服务层
│   ├── dual_entrance_websocket_manager.py  # 双入口WebSocket管理器
│   ├── entrance_manager.py       # 入口管理器
│   ├── personal_assistant.py    # 个人助手服务
│   ├── backend_connector.py     # 后端连接器
│   └── websocket_manager.py      # WebSocket管理器
└── static/css/                   # 样式文件
    ├── entrance.css             # 入口选择页面样式
    ├── secretariat.css          # Secretariat入口样式
    └── forum.css                # Forum入口样式
```

## 🎨 界面展示

### 入口选择页面
- 提供Secretariat和Forum两种入口的详细介绍
- 用户可以设置个人信息和偏好
- 响应式设计，支持移动设备

### Secretariat入口
- 智能任务处理界面
- 实时任务状态监控
- 透明度数据展示
- 任务管理和历史记录

### Forum入口
- 实时协作讨论界面
- 多角色对话支持
- 共识状态监控
- 用户直接参与控制

## 🔧 技术架构

### 前端技术栈
- **Lona**: Python Web框架，提供统一的Python前后端解决方案
- **HTML/CSS**: 响应式用户界面
- **WebSocket**: 实时数据通信
- **AsyncIO**: 异步编程支持

### 后端技术栈
- **FastAPI**: 高性能Web框架
- **WebSocket**: 实时通信支持
- **Pydantic**: 数据验证和序列化
- **SQLAlchemy**: 数据库ORM (可选)

### 核心组件

#### 1. 双入口WebSocket管理器
- 支持Secretariat和Forum两种消息类型
- 统一的连接管理和消息路由
- 自动重连和错误处理

#### 2. 入口管理器
- 用户上下文管理
- 会话状态保存
- 入口切换和上下文迁移

#### 3. UI组件
- 模块化设计，支持复用
- 统一的样式和交互
- 实时数据更新

## 📡 API接口

### WebSocket消息类型

#### 通用消息
- `CHAT_MESSAGE`: 聊天消息
- `SYSTEM_STATUS`: 系统状态
- `ERROR`: 错误消息

#### Secretariat消息
- `SECRETARIAT_TASK`: 任务提交
- `TASK_STATUS`: 任务状态更新
- `SECRETARIAT_RESULT`: 任务结果
- `TRANSPARENCY_DATA`: 透明度数据

#### Forum消息
- `CREATE_FORUM_SESSION`: 创建论坛会话
- `USER_INTERVENTION`: 用户干预
- `AGENT_MESSAGE`: 代理消息
- `CONSENSUS_UPDATE`: 共识更新

### REST API端点
- `GET /`: 入口选择页面
- `GET /secretariat`: Secretariat入口
- `GET /forum`: Forum入口
- `GET /switch`: 入口切换

## 🔧 配置选项

### 环境变量
```bash
# 后端服务器配置
BACKEND_HOST=localhost
BACKEND_PORT=8000

# 前端服务器配置
FRONTEND_HOST=localhost
FRONTEND_PORT=8080

# WebSocket配置
WS_URL=ws://localhost:8000/ws

# 日志配置
LOG_LEVEL=INFO
```

### 配置文件
系统支持通过`config.yaml`文件进行详细配置：

```yaml
# 服务器配置
server:
  host: localhost
  port: 8080
  debug: true

# WebSocket配置
websocket:
  url: ws://localhost:8000/ws
  max_retries: 5
  retry_delay: 5

# 入口配置
entrances:
  secretariat:
    enabled: true
    max_sessions: 100
  forum:
    enabled: true
    max_sessions: 50

# 用户配置
user:
  session_timeout: 3600
  max_concurrent_sessions: 3
```

## 🧪 测试

### 单元测试
```bash
# 运行组件测试
python -m pytest tests/components/

# 运行服务测试
python -m pytest tests/services/

# 运行集成测试
python -m pytest tests/integration/
```

### 手动测试
1. 访问 http://localhost:8080
2. 选择入口类型并填写用户信息
3. 测试基本功能（消息发送、任务提交等）
4. 测试入口切换功能
5. 检查WebSocket连接状态

## 🚀 部署

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python", "start_dual_entrance_system.py"]
```

### 生产环境配置
1. 使用Gunicorn或uWSGI部署后端
2. 配置Nginx反向代理
3. 启用HTTPS和SSL证书
4. 配置日志轮转和监控

## 📊 监控和日志

### 系统监控
- WebSocket连接状态
- 会话数量和活跃度
- 消息吞吐量
- 错误率和响应时间

### 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dual_entrance.log'),
        logging.StreamHandler()
    ]
)
```

## 🔍 故障排除

### 常见问题

#### 1. WebSocket连接失败
- 检查后端服务器是否启动
- 确认WebSocket URL配置正确
- 检查防火墙和网络连接

#### 2. 页面无法加载
- 确认前端服务器启动正常
- 检查静态文件路径配置
- 查看浏览器控制台错误

#### 3. 入口切换失败
- 检查用户会话状态
- 确认上下文保存功能正常
- 查看入口管理器日志

### 调试模式
```bash
# 启用调试模式
python frontend/dual_entrance_app.py --debug

# 查看详细日志
LOG_LEVEL=DEBUG python start_dual_entrance_system.py
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 📞 联系我们

- 项目主页: https://github.com/your-repo/dual-entrance-system
- 问题反馈: https://github.com/your-repo/dual-entrance-system/issues
- 邮箱: your-email@example.com

---

**Personal Intelligence Hub - 基于制度原语的集体智慧涌现平台**
# Personal Intelligence Hub - Frontend

基于Lona Web框架的Personal Intelligence Hub前端应用，提供统一的Python前后端解决方案。

## 功能特性

- 🎭 **统一对话界面**: 中央聊天对话，支持自然语言交互
- 🔍 **实时透明度监控**: 显示系统内部运作过程和代理状态
- 📚 **智能知识库**: Wiki面板，支持实时知识更新
- 📋 **任务管理**: 任务面板，支持任务分解和跟踪
- 🎨 **现代化UI**: 响应式设计，支持多设备访问

## 技术栈

- **Lona Web Framework**: Python前后端统一框架
- **WebSocket**: 实时通信支持
- **Markdown**: 富文本内容渲染
- **CSS3**: 现代化样式和动画

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python run.py
```

或者直接运行主应用：

```bash
python main_app.py
```

### 3. 访问应用

打开浏览器访问: http://localhost:8080

## 项目结构

```
frontend/
├── main_app.py              # Lona应用入口点
├── run.py                   # 启动脚本
├── requirements.txt         # Python依赖
├── components/              # UI组件
│   ├── __init__.py
│   ├── base_components.py   # 基础组件库
│   ├── chat_interface.py    # 聊天界面组件
│   ├── transparency_monitor.py  # 透明度监控组件
│   ├── wiki_panel.py        # Wiki面板组件
│   └── task_panel.py        # 任务面板组件
├── services/                # 服务层
│   ├── __init__.py
│   ├── backend_connector.py # 后端连接器
│   └── personal_assistant.py   # 个人助手服务
└── static/                  # 静态资源
    └── css/
        ├── main.css         # 主样式文件
        └── components.css   # 组件样式文件
```

## 组件说明

### ChatInterface (聊天界面)
- 支持实时消息发送和接收
- 消息历史记录
- 特殊命令处理（如 `/consensus now`）

### TransparencyMonitor (透明度监控)
- 显示活跃代理状态
- LLM调用监控
- Token使用统计
- 系统性能指标

### WikiPanel (Wiki面板)
- 知识库搜索和浏览
- 实时知识更新
- 质量评分显示
- 版本历史管理

### TaskPanel (任务面板)
- 任务层次结构显示
- 实时状态更新
- 进度跟踪
- 代理分配管理

## 开发说明

### 添加新组件

1. 在 `components/` 目录下创建新的组件文件
2. 继承 `lona.Component` 基类
3. 实现 `render()` 方法返回HTML结构
4. 在主视图中导入和使用

### 样式定制

- 修改 `static/css/main.css` 进行全局样式调整
- 修改 `static/css/components.css` 进行组件样式定制
- 支持CSS变量和响应式设计

### 服务集成

- 在 `services/` 目录下添加新的服务类
- 通过 `BackendConnector` 统一管理API调用
- 支持WebSocket实时通信

## 部署说明

### 开发环境
```bash
python run.py
```

### 生产环境
```bash
# 使用gunicorn部署
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:8080 main_app:app
```

## 故障排除

### 常见问题

1. **端口占用**: 修改 `main_app.py` 中的端口号
2. **依赖缺失**: 运行 `pip install -r requirements.txt`
3. **样式不加载**: 检查静态文件路径配置

### 调试模式

应用默认启用调试模式，支持：
- 代码热重载
- 详细错误信息
- 开发者工具集成

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License
# DAIP-LIVE 脚手架系统文档

## 📚 文档目录

本目录包含DAIP-LIVE脚手架系统的完整文档集合。

### 🚀 快速开始
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 快速参考指南，常用命令和配置速查

### 📖 用户文档
- **[USER_MANUAL.md](USER_MANUAL.md)** - 完整的用户手册，涵盖所有功能和最佳实践
- **[USER_SCENARIOS.md](USER_SCENARIOS.md)** - 用户场景故事，实际应用案例和使用体验

### 🔧 技术文档
- **[API_REFERENCE.md](API_REFERENCE.md)** - API参考文档（待完成）
- **[TEMPLATE_DEVELOPMENT.md](TEMPLATE_DEVELOPMENT.md)** - 模板开发指南（待完成）
- **[PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)** - 插件开发指南（待完成）

---

## 🎯 文档导航

### 新用户推荐阅读路径
1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 5分钟快速上手
2. **[USER_SCENARIOS.md](USER_SCENARIOS.md)** - 了解实际应用场景
3. **[USER_MANUAL.md](USER_MANUAL.md)** - 深入学习所有功能

### 开发者推荐阅读路径
1. **[USER_MANUAL.md](USER_MANUAL.md)** - 了解系统架构和API
2. **[TEMPLATE_DEVELOPMENT.md](TEMPLATE_DEVELOPMENT.md)** - 学习模板开发
3. **[PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)** - 扩展系统功能

### 团队管理者推荐阅读路径
1. **[USER_SCENARIOS.md](USER_SCENARIOS.md)** - 了解团队应用案例
2. **[USER_MANUAL.md](USER_MANUAL.md#团队协作)** - 团队协作功能
3. **[USER_MANUAL.md](USER_MANUAL.md#最佳实践)** - 项目标准化最佳实践

---

## 💡 核心特性

### 🏗️ 智能项目生成
- **自然语言理解**: 用简单描述生成完整项目
- **多模板支持**: 涵盖主流技术栈和架构模式
- **AI增强**: 智能推荐最佳实践和架构模式

### 🔧 灵活配置
- **三种项目类型**: 独立项目、DAIP模块、集成项目
- **自定义模板**: 支持团队定制和私有模板
- **插件系统**: 可扩展的插件架构

### 🛡️ 企业级特性
- **标准化**: 统一的项目结构和代码规范
- **安全性**: 内置安全检查和最佳实践
- **可维护性**: 自动文档生成和依赖管理

---

## 🚀 快速体验

### 5分钟创建第一个项目
```bash
# 启动DAIP-LIVE
poetry run daip run

# 在TUI中选择 "Scaffold" -> "New Project"
# 或使用命令行：
poetry run daip project create "我的Web应用" \
  --description "React + Node.js全栈应用" \
  --output ./my_app
```

### 查看效果
```bash
cd my_app
ls -la
# 您将看到一个完整的、可直接运行的项目结构
```

---

## 📋 文档状态

| 文档 | 状态 | 完成度 |
|------|------|--------|
| QUICK_REFERENCE.md | ✅ 已完成 | 100% |
| USER_MANUAL.md | ✅ 已完成 | 100% |
| USER_SCENARIOS.md | ✅ 已完成 | 100% |
| API_REFERENCE.md | 🚧 开发中 | 0% |
| TEMPLATE_DEVELOPMENT.md | 📋 计划中 | 0% |
| PLUGIN_DEVELOPMENT.md | 📋 计划中 | 0% |

---

## 🤝 贡献文档

我们欢迎社区贡献！您可以：

1. **完善现有文档**: 发现错误或不清晰的地方，请提交PR
2. **添加新文档**: 根据实际需求添加新的技术文档
3. **翻译文档**: 帮助翻译文档到其他语言
4. **提供反馈**: 在GitHub Issues中提供文档改进建议

### 文档贡献指南
```bash
# 克隆项目
git clone https://github.com/daip-live/scaffold.git

# 创建文档分支
git checkout -b docs/update-user-manual

# 编辑文档
# 使用Markdown格式，遵循现有文档风格

# 提交更改
git add docs/
git commit -m "docs: 更新用户手册"
git push origin docs/update-user-manual

# 创建Pull Request
```

---

## 🆘 获取帮助

### 在线资源
- **官方网站**: https://daip.live
- **文档网站**: https://docs.daip.live
- **GitHub仓库**: https://github.com/daip-live/scaffold
- **社区论坛**: https://community.daip.live

### 命令行帮助
```bash
# 查看主帮助
daip --help

# 查看脚手架帮助
daip scaffold --help

# 查看项目管理帮助
daip project --help

# 查看模板帮助
daip template --help
```

### 问题报告
- **Bug报告**: https://github.com/daip-live/scaffold/issues
- **功能请求**: https://github.com/daip-live/scaffold/discussions
- **安全问题**: security@daip.live

---

## 📄 许可证

所有文档遵循 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可证。

---

*最后更新: 2024年1月*
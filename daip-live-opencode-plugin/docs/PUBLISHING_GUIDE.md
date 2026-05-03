# debatewiki opencode plugin - 发布指南

## 发布前准备

### 1. 确保包名可用
在发布前，需要确认"debatewiki"包名未被占用：
```bash
npm view debatewiki
```
如果返回404错误，则包名可用；如果有信息返回，则需要选择其他包名。

### 2. 登录npm账户
```bash
npm login
```

### 3. 检查package.json
确保package.json包含所有必要字段：
- name: 必须是唯一的包名
- version: 遵循语义化版本规范
- description: 简洁描述包的功能
- keywords: 包含相关关键词
- repository: 指向代码仓库
- license: 开源许可证

## 发布流程

### 1. 构建项目
```bash
npm run build
```

### 2. 验证包内容
```bash
npm pack
```
这将创建一个.tgz文件，您可以检查其内容是否正确。

### 3. 发布到npm
```bash
npm publish --access public
```

## 替代发布方案

如果无法发布到公共npm注册表，可以考虑以下替代方案：

### 1. 本地安装
```bash
# 构建项目
npm run build

# 本地安装
npm install -g /path/to/your/project
```

### 2. 使用tarball
```bash
# 创建tarball
npm pack

# 从tarball安装
npm install -g debatewiki-1.0.0.tgz
```

### 3. Git仓库安装
```bash
npm install -g git+https://github.com/your-username/debatewiki-opencode-plugin.git
```

## OpenCode插件配置

一旦包发布到npm，用户可以通过以下方式配置OpenCode：

1. 创建或编辑 `~/.config/opencode/opencode.json`:
```json
{
  "plugin": [
    "oh-my-opencode",
    "debatewiki"
  ],
  "$schema": "https://opencode.ai/config.json"
}
```

2. OpenCode将在启动时自动安装并加载debatewiki插件。

## 验证发布

发布后，可以通过以下方式验证：

```bash
# 检查包信息
npm info debatewiki

# 安装包
npm install -g debatewiki

# 验证安装
npm list -g debatewiki
```

## 版本管理

- 遵循语义化版本规范 (SemVer)
- 每次发布前更新package.json中的版本号
- 使用git标签标记发布版本：
```bash
git tag v1.0.1
git push origin v1.0.1
```

## 注意事项

1. **包名冲突**：如果"debatewiki"已被占用，可以选择其他名称如"daip-debatewiki"或"opencode-debatewiki"
2. **访问权限**：使用`--access public`标志确保包是公开的
3. **依赖管理**：确保所有依赖项正确声明在package.json中
4. **文件包含**：使用files字段或.npmignore确保只包含必要的文件

## 回滚发布

如果发布出现问题，可以撤销发布（24小时内）：
```bash
npm unpublish debatewiki@<version>
```

或者发布新版本修复问题。
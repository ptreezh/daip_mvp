# Gemini CLI 配置说明

## 安装完成
Gemini CLI 已成功安装！

## 配置步骤

### 1. 获取 Google API 密钥
- 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
- 登录您的 Google 账户
- 创建新的 API 密钥

### 2. 设置环境变量
在 Windows 中：
```cmd
set GOOGLE_API_KEY=your_actual_api_key_here
```

或者在 PowerShell 中：
```powershell
$env:GOOGLE_API_KEY="your_actual_api_key_here"
```

### 3. 永久设置环境变量（可选）
在 Windows 系统中：
1. 右键点击"此电脑" → "属性" → "高级系统设置"
2. 点击"环境变量"
3. 在"用户变量"中添加：
   - 变量名：`GOOGLE_API_KEY`
   - 变量值：您的 API 密钥

## 使用方法

### 基本命令
```cmd
# 启动交互式对话
gemini

# 直接提问
gemini "你好，请介绍一下你自己"

# 使用特定模型
gemini --model gemini-1.5-pro "解释量子计算"

# 非交互模式
gemini -p "写一个Python函数来计算斐波那契数列"
```

### 高级功能
```cmd
# 列出所有扩展
gemini --list-extensions

# 使用特定扩展
gemini --extensions code,documentation

# 查看版本
gemini --version

# 启用调试模式
gemini --debug
```

## 注意事项
- 确保网络连接正常
- API 有使用限制，请合理使用
- 首次使用可能需要验证 API 密钥

## 故障排除
如果遇到 429 错误（请求过多），请稍后再试。
如果遇到认证问题，请检查 API 密钥是否正确设置。
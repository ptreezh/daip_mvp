# 本地模型角色配置使用指南

## 📋 概述

我已经为您创建了5个专门优化的本地模型角色配置，每个角色都配置了适合其特质的模型参数。

## 🎭 创建的角色

### 1. 技术分析师 (tech_analyst)
- **主模型**: qwen-72b-chat (低温度，适合技术分析)
- **备用模型**: qwen-14b-chat
- **辩论模型**: qwen-32b-chat
- **特点**: 逻辑性强，温度设置较低(0.3-0.5)，适合精确的技术分析

### 2. 创意写作师 (creative_writer)
- **主模型**: deepseek-coder (高温度，适合创意)
- **备用模型**: llama2-70b-chat
- **辩论模型**: deepseek-coder (更高温度0.9)
- **特点**: 创意性强，温度设置较高(0.7-0.9)，适合创作

### 3. 数据科学家 (data_scientist)
- **主模型**: mistral-7b-instruct (极低温度，保证逻辑)
- **备用模型**: mixtral-8x7b-instruct
- **辩论模型**: mixtral-8x7b-instruct
- **特点**: 严谨科学，温度设置很低(0.2-0.4)，适合数据分析

### 4. 产品经理 (product_manager)
- **主模型**: llama2-13b-chat (平衡型)
- **备用模型**: phi-2 (轻量级)
- **辩论模型**: llama2-13b-chat (更高温度0.7)
- **特点**: 平衡实用，温度适中(0.5-0.7)，适合产品规划

### 5. 哲学思辨家 (philosophy_thinker)
- **主模型**: nous-hermes-2-mixtral (深度思考)
- **备用模型**: wizardlm-uncensored
- **辩论模型**: nous-hermes-2-mixtral (更高温度0.8)
- **特点**: 深度思考，温度设置较高(0.6-0.8)，适合哲学讨论

## 🚀 快速开始

### 1. 环境准备
```bash
# 确保Ollama正在运行
ollama serve

# 拉取你需要的模型（示例）
ollama pull qwen-72b-chat
ollama pull deepseek-coder
ollama pull mistral-7b-instruct
```

### 2. 基础测试命令
```bash
# 测试技术分析师
python -m daip_live.cli pa "帮我分析一下这个算法的复杂度" --role tech_analyst

# 测试创意写作师
python -m daip_live.cli pa "帮我写一段关于未来的科幻小说" --role creative_writer

# 测试数据科学家
python -m daip_live.cli pa "如何处理这个数据集中的异常值" --role data_scientist
```

### 3. 辩论测试命令
```bash
# 两角色辩论
python -m daip_live.cli debate "AI是否会取代人类工作" --roles tech_analyst,creative_writer --rounds 3

# 多角色辩论
python -m daip_live.cli debate "技术发展的社会影响" --roles tech_analyst,product_manager,philosophy_thinker --rounds 3
```

## 🔧 模型配置调整

### 根据你的实际模型调整配置

如果你有其他本地模型，可以修改 `roles/` 目录下的配置文件：

```yaml
# 例如，将tech_analyst的主模型改为你的模型
model_configs:
  - model_name: "your-local-model"    # 改为你的模型名称
    provider: "ollama"
    max_tokens: 4000
    temperature: 0.3                # 根据模型特性调整
    is_primary: true
```

### 温度参数建议
- **技术分析**: 0.2-0.4 (低温度，更精确)
- **创意写作**: 0.7-0.9 (高温度，更有创意)
- **平衡角色**: 0.5-0.7 (中等温度)
- **辩论场景**: 比平时高0.1-0.2 (增加表现力)

### 常见本地模型列表
- qwen系列 (通义千问)
- llama2系列 (Meta)
- mistral系列 (Mistral AI)
- deepseek系列 (深度求索)
- phi系列 (Microsoft)
- mixtral系列 (Mistral AI)

## 📊 测试工具

### 完整测试
```bash
python test_role_configs.py
```

### 快速测试
```bash
python quick_test.py
```

## 🐛 常见问题

### 1. 模型未找到
**问题**: 提示模型不存在
**解决**: 
- 确保Ollama正在运行
- 使用 `ollama pull <model_name>` 拉取模型
- 修改配置文件中的模型名称

### 2. 参数不生效
**问题**: 模型参数似乎没有效果
**解决**: 
- 检查模型是否支持参数调整
- 逐步调整参数观察效果
- 不同模型对参数的敏感度不同

### 3. 性能问题
**问题**: 响应速度慢
**解决**: 
- 使用较小的模型 (如7B代替72B)
- 减少 `max_tokens` 设置
- 调整并发设置

## 🎯 最佳实践

### 1. 模型选择
- **技术任务**: 选择逻辑性强的模型 (如qwen, mistral)
- **创意任务**: 选择表达能力强的模型 (如deepseek, llama)
- **资源受限**: 选择轻量级模型 (如phi-2, mistral-7b)

### 2. 参数调优
- 从保守设置开始，逐步调整
- 记录每个参数的效果
- 不同任务可能需要不同的参数组合

### 3. 配置管理
- 为不同场景保存不同的配置
- 定期备份重要的配置文件
- 使用版本控制管理配置变更

## 📈 性能监控

运行测试时观察：
- 响应时间
- 输出质量
- Token使用量
- 内存占用

根据实际情况调整配置以达到最佳效果。

---

## 🎉 开始体验

现在您已经拥有了完整的本地模型角色配置系统！选择一个感兴趣的角色开始测试吧！

```bash
# 启动TUI界面进行全面测试
python -m daip_live.cli run "开始测试多模型角色配置"
```
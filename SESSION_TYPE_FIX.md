# 会话类型限制问题修复说明

## 问题描述
在进行tokens压缩时，系统报错："处理 tokens压缩时出错 会话类型必须是 chat debate workflow"。这表明在创建用于压缩的会话时，会话类型被限制为特定值，但实际需要的"compression"类型不在允许列表中。

## 问题原因
问题出在`src/daip_live/core/models.py`文件中的`Session`模型定义：

```python
class Session(BaseModel):
    session_type: Literal["debate", "chat", "workflow"]
```

而在TUI的`_handle_compact_command`方法中创建压缩会话时使用了：
```python
session = self._session_manager.create_session(
    goal="Context Compression Session",
    session_type="compression",  # 这个值不在Literal限制中
    participant_ids=["user", "assistant"]
)
```

这导致Pydantic验证失败。

## 修复方案
扩展`Session`模型中的`session_type`允许值，添加"compression"类型：

```python
class Session(BaseModel):
    session_type: Literal["debate", "chat", "workflow", "compression"]
```

## 修复效果
修复后的行为：
1. ✅ 可以正常创建"compression"类型的会话
2. ✅ tokens压缩功能可以正常工作
3. ✅ 保持原有的验证机制，拒绝无效类型
4. ✅ 其他会话类型（debate, chat, workflow）仍然正常工作

## 测试验证
通过测试用例验证修复效果：
- 创建"compression"类型会话：✅ 成功
- 创建所有允许的会话类型：✅ 成功
- 创建无效会话类型：✅ 正确拒绝

## 代码变更
文件：`src/daip_live/core/models.py`
变更：扩展`Session`模型的`session_type`字段，添加"compression"到Literal类型中
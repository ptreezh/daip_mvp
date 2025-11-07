# TUI删除键问题修复说明

## 问题描述
在TUI中，当用户输入斜杠指令（如`/role`）后，如果想要删除并重新输入其他指令或直接对话时，发现删除键无法正常工作。具体表现为：
1. 用户输入`/role`后，自动完成会建议`/role list`
2. 当用户尝试删除内容时（如删除到`/ro`），系统会自动将内容补全回`/role list`
3. 用户无法完全删除指令以输入新内容

## 问题原因
问题出在`src/daip_live/tui.py`文件的`on_input_changed`方法中。原始代码逻辑为：
```python
# 只要有一个建议且不是参数建议，就自动完成
if len(suggestions) == 1 and not is_parameter_suggestion:
    clean_suggestion = suggestions[0].split(" - ")[0]
    input_widget = self.query_one(Input)
    # 无条件替换输入内容
    input_widget.value = clean_suggestion
```

这种实现没有考虑用户是在输入还是在删除，导致用户删除内容时也会被自动补全回去。

## 修复方案
修改自动完成逻辑，只在用户输入内容变长时才自动完成，避免在用户删除时自动补全：

```python
# 只有当建议比当前输入长时才自动完成
if len(clean_suggestion) > len(value):
    # 执行自动完成
    if clean_suggestion.startswith(value):
        input_widget.value = clean_suggestion
    # ...
```

## 修复效果
修复后的行为：
1. ✅ 用户输入`/role`时，正常自动完成为`/role list`
2. ✅ 用户删除到`/ro`时，保持`/ro`不变，不会自动补全
3. ✅ 用户完全删除后，可以输入新内容
4. ✅ 正常的自动完成功能仍然有效

## 测试验证
通过测试用例验证修复效果：
- 输入增长时自动完成：`/ro` → `/role list` ✅
- 输入减少时不自动完成：`/role` → `/ro` 保持不变 ✅
- 完全删除后可输入新内容：`/role` → `` → `/help` ✅

## 代码变更
文件：`src/daip_live/tui.py`
方法：`on_input_changed`
变更：添加长度检查条件，只在建议比当前输入长时才自动完成
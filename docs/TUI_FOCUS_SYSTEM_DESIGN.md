# TUI焦点切换与复制粘贴系统设计

## 需求概述
实现TUI界面的焦点切换系统，支持：
- Ctrl+TAB在输出区和输入区之间切换焦点
- 输出屏幕支持鼠标选择和键盘复制粘贴
- 焦点在输出区时，功能快捷键失效
- 焦点在输入区时，功能快捷键恢复
- 支持Ctrl+A全选、Ctrl+C复制等标准快捷键

## 技术架构

### 1. 焦点状态管理
```python
class FocusMode(Enum):
    INPUT = "input"      # 输入区焦点
    OUTPUT = "output"    # 输出区焦点

class DAIP_TUI:
    def __init__(self):
        self.focus_mode = FocusMode.INPUT
        self.output_text_area = None
        self.input_widget = None
```

### 2. 组件设计
- **输出区域**: 使用TextArea替代Static，支持文本选择
- **输入区域**: 保持Input组件，支持命令输入
- **焦点指示器**: 视觉提示当前焦点位置

### 3. 快捷键映射
```python
BINDINGS = [
    Binding("ctrl+tab", "toggle_focus", "切换焦点"),
    Binding("ctrl+a", "select_all", "全选", show=False),
    Binding("ctrl+c", "copy_text", "复制", show=False),
    Binding("ctrl+shift+c", "copy_text", "复制", show=False),
    Binding("escape", "exit_output_mode", "退出输出模式"),
]
```

## 实施步骤

### 阶段1：基础焦点切换 (优先级：高)
- [ ] 替换Static为TextArea作为输出组件
- [ ] 实现Ctrl+TAB焦点切换逻辑
- [ ] 添加焦点视觉指示器

### 阶段2：复制粘贴功能 (优先级：高)
- [ ] 实现TextArea的文本选择功能
- [ ] 添加Ctrl+C复制功能
- [ ] 添加Ctrl+A全选功能
- [ ] 实现右键菜单支持

### 阶段3：焦点模式行为 (优先级：中)
- [ ] 输出模式下禁用命令处理
- [ ] 输入模式下恢复完整功能
- [ ] 添加模式切换动画效果

### 阶段4：鼠标支持 (优先级：低)
- [ ] 鼠标点击切换焦点
- [ ] 鼠标拖拽选择文本
- [ ] 右键上下文菜单

## 代码实现方案

### 1. 组件更新
```python
# 替换输出组件
yield TextArea(
    "Waiting for agent to start...",
    id="output_text_area",
    read_only=True,
    show_line_numbers=False,
    classes="output-mode"
)
```

### 2. 焦点管理
```python
def action_toggle_focus(self) -> None:
    """切换输入/输出焦点"""
    if self.focus_mode == FocusMode.INPUT:
        self.focus_mode = FocusMode.OUTPUT
        self.query_one("#output_text_area").focus()
    else:
        self.focus_mode = FocusMode.INPUT
        self.query_one("#user_input").focus()
```

### 3. 快捷键处理
```python
def on_key(self, event) -> None:
    """处理键盘事件，根据焦点模式决定行为"""
    if self.focus_mode == FocusMode.OUTPUT:
        # 输出模式下只处理复制、全选等操作
        if event.key == "escape":
            self.action_exit_output_mode()
        # 其他键事件由TextArea处理
        return
    
    # 输入模式下处理原有快捷键
    super().on_key(event)
```

## 测试计划

### 单元测试
- [ ] 焦点切换测试
- [ ] 复制粘贴功能测试
- [ ] 模式行为测试

### 集成测试
- [ ] 端到端焦点切换体验
- [ ] 复制粘贴实际效果验证
- [ ] 快捷键冲突测试

## 用户体验优化

### 视觉反馈
- 焦点边框高亮
- 模式状态指示器
- 复制成功提示

### 交互优化
- 平滑的焦点切换动画
- 智能的默认焦点位置
- 上下文相关的帮助提示

## 风险与限制

### 技术限制
- TextArea组件的只读模式限制
- 跨平台剪贴板兼容性
- 大文本性能影响

### 解决方案
- 使用异步剪贴板操作
- 实现文本分页加载
- 提供配置选项关闭高级功能

## 验收标准

1. ✅ Ctrl+TAB成功切换焦点
2. ✅ 输出区域支持文本选择
3. ✅ 支持Ctrl+C复制选中文本
4. ✅ 支持Ctrl+A全选
5. ✅ 焦点模式下快捷键行为正确
6. ✅ 鼠标支持基本选择功能
7. ✅ 用户体验流畅无卡顿
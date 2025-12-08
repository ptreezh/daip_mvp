"""模块化TUI入口文件 - 向后兼容的TUI接口"""

# 导入简化的模块化TUI类
from .tui.simplified_main import SimplifiedTUI as DAIP_TUI

# 为了向后兼容，重新导出原有的类名
__all__ = ['DAIP_TUI']

# 版本信息
VERSION = "2.1.0-modular-simplified"
DESCRIPTION = "DAIP-LIVE TUI - Simplified Modular Architecture"

# 兼容性说明：
# 这个文件作为模块化TUI入口，保持相同的API接口
# 所有使用DAIP_TUI类的代码都不需要修改
# 内部实现已完全模块化，提升了可维护性和扩展性

print(f"🚀 DAIP-LIVE TUI Modular v{VERSION} loaded (Simplified)")
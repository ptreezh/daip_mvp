"""模块化TUI入口文件 - 向后兼容的TUI接口"""

# 版本信息
VERSION = "2.1.0-modular-simplified"
DESCRIPTION = "DAIP-LIVE TUI - Simplified Modular Architecture"


# 导入简化的模块化TUI类 (延迟导入以避免初始化副作用)
def get_daip_tui():
    from .tui.simplified_main import SimplifiedTUI

    return SimplifiedTUI


# 为了向后兼容，重新导出原有的类名
__all__ = ["get_daip_tui", "DAIP_TUI"]

# 兼容性说明：
# 这个文件作为模块化TUI入口，保持相同的API接口
# 所有使用DAIP_TUI类的代码都不需要修改
# 内部实现已完全模块化，提升了可维护性和扩展性


# 创建一个工厂函数而非直接导入类
def DAIP_TUI(*args, **kwargs):
    """工厂函数来创建TUI实例，确保只有在实际需要时才初始化"""
    tui_class = get_daip_tui()
    return tui_class(*args, **kwargs)

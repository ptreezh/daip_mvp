def setup_observability():
    """设置OpenTelemetry可观测性"""


def instrument_fastapi(app):
    """为FastAPI应用添加OpenTelemetry仪表化"""


def instrument_sqlalchemy(engine):
    """为SQLAlchemy添加OpenTelemetry仪表化"""


def instrument_requests():
    """为requests库添加OpenTelemetry仪表化"""


def instrument_logging():
    """为logging添加OpenTelemetry仪表化"""


def create_span(name, attributes=None):
    """创建自定义span的便捷函数"""


def add_event_to_span(span, name, attributes=None):
    """向span添加事件的便捷函数"""


def add_error_to_span(span, exception):
    """向span添加错误的便捷函数"""

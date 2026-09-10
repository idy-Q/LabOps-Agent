"""LabOps-Agent 垂直业务工具集包"""

from app.tools.registry import (
    tool,
    execute_tool,
    get_tool,
    list_tools,
    get_tools_schemas,
    clear_registry,
)

# 自动导入各业务工具模块以触发 @tool 装饰器注册
from app.tools import metric_tools, ticket_tools, asset_tools, regulation_tools

__all__ = [
    "tool",
    "execute_tool",
    "get_tool",
    "list_tools",
    "get_tools_schemas",
    "clear_registry",
    "metric_tools",
    "ticket_tools",
    "asset_tools",
    "regulation_tools",
]

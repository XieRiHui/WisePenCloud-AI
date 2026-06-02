from typing import Any

from chat.application.tools.core.definition import Tool


class ToolScope:
    """一次请求内的工具可见性和可信上下文快照。"""

    def __init__(self, *, tools: dict[str, Tool], context: dict[str, Any] | None) -> None:
        self._tools = dict(tools)
        self._context = dict(context or {})
        self._schemas: list[dict[str, Any]] = [
            tool.definition.llm_spec.to_openai_tool() for tool in self._tools.values()
        ]

    def schemas(self) -> list[dict[str, Any]]:
        return list(self._schemas)

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    @property
    def context(self) -> dict[str, Any]:
        return dict(self._context)

    def __len__(self) -> int:
        return len(self._tools)

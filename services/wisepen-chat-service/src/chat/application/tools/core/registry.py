from collections.abc import Iterable
from typing import Any

from chat.application.tools.core.definition import Tool
from chat.application.tools.core.scope import ToolScope


class ToolRegistry:
    """Global tool registry that derives request-scoped tool views."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.definition.llm_spec.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def schemas(self) -> list[dict[str, Any]]:
        """Return schemas for all globally registered tools.

        This method is intended for diagnostics and tests. Runtime LLM calls
        should use ToolScope.schemas() so reserved/allow/deny filtering is
        applied for the current request.
        """
        return [tool.definition.llm_spec.to_openai_tool() for tool in self._tools.values()]

    def derive(
        self,
        *,
        session_id: str,
        tool_context: dict[str, Any] | None = None,
        runtime_discovered_tools: Iterable[Tool] | None = None,
        expose_tool_name_set: set[str] | None = None,
        allow_tool_name_set: set[str] | None = None,
        deny_tool_name_set: set[str] | None = None,
    ) -> ToolScope:
        expose_tool_name_set = expose_tool_name_set or set()
        deny_tool_name_set = deny_tool_name_set or set()

        tools: dict[str, Tool] = dict(self._tools)
        for tool in runtime_discovered_tools or []:
            tools[tool.definition.llm_spec.name] = tool

        filtered_tools: dict[str, Tool] = {}
        for name, tool in tools.items():
            policy = tool.definition.runtime_policy

            if policy.reserved:
                if name in expose_tool_name_set:
                    filtered_tools[name] = tool
                continue
            if allow_tool_name_set is not None and name not in allow_tool_name_set:
                continue
            if not policy.reserved and name in deny_tool_name_set:
                continue

            filtered_tools[name] = tool

        context = dict(tool_context or {})
        context.setdefault("session_id", session_id)
        return ToolScope(tools=filtered_tools, context=context)

    def __len__(self) -> int:
        return len(self._tools)

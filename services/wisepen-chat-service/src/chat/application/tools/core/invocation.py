import json
from dataclasses import dataclass, field
from typing import Any

from common.logger import log_fail


@dataclass
class ToolCallAccumulator:
    """Accumulates streamed tool call deltas by model-provided index."""

    id: str = ""
    name: str = ""
    arguments: str = ""


@dataclass(frozen=True)
class ToolInvocation:
    call_id: str
    tool_name: str
    input: dict[str, Any]
    iteration: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ToolCallParser:
    def parse(
        self,
        accumulators: dict[int, ToolCallAccumulator],
        *,
        iteration: int | None = None,
    ) -> list[ToolInvocation]:
        invocations: list[ToolInvocation] = []
        for idx in sorted(accumulators.keys()):
            acc = accumulators[idx]
            try:
                args = json.loads(acc.arguments) if acc.arguments else {}
            except json.JSONDecodeError as exc:
                log_fail(
                    "tool_call arguments 解析 JSON 格式非法，降级为空 dict",
                    exc,
                    name=acc.name,
                )
                args = {}
            if not isinstance(args, dict):
                log_fail(
                    "tool_call arguments 解析结果不是对象，降级为空 dict",
                    type(args).__name__,
                    name=acc.name,
                    parsed_type=type(args).__name__,
                )
                args = {}
            invocations.append(
                ToolInvocation(
                    call_id=acc.id,
                    tool_name=acc.name,
                    input=args,
                    iteration=iteration,
                )
            )
        return invocations

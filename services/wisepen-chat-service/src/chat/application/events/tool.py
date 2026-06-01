from dataclasses import dataclass
from typing import Any

from chat.application.events.base import StreamEvent


@dataclass(frozen=True)
class ToolInputStartEvent(StreamEvent):
    """Tool call input streaming started."""

    call_id: str
    tool_name: str


@dataclass(frozen=True)
class ToolInputAvailableEvent(StreamEvent):
    """Tool call input is available."""

    call_id: str
    tool_name: str
    input: dict[str, Any]


@dataclass(frozen=True)
class ToolOutputAvailableEvent(StreamEvent):
    """Tool call output is available."""

    call_id: str
    output: Any

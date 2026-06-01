from dataclasses import dataclass

from chat.application.events.base import StreamEvent


@dataclass(frozen=True)
class ReasoningStartEvent(StreamEvent):
    """A reasoning text stream started."""

    reasoning_id: str


@dataclass(frozen=True)
class ReasoningDeltaEvent(StreamEvent):
    """A reasoning text stream delta."""

    reasoning_id: str
    delta: str


@dataclass(frozen=True)
class ReasoningEndEvent(StreamEvent):
    """A reasoning text stream ended."""

    reasoning_id: str

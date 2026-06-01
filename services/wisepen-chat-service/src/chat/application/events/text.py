from dataclasses import dataclass

from chat.application.events.base import StreamEvent


@dataclass(frozen=True)
class TextStartEvent(StreamEvent):
    """A normal text stream started."""

    text_id: str


@dataclass(frozen=True)
class TextDeltaEvent(StreamEvent):
    """A normal text stream delta."""

    text_id: str
    delta: str


@dataclass(frozen=True)
class TextEndEvent(StreamEvent):
    """A normal text stream ended."""

    text_id: str

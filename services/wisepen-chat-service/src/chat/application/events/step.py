from dataclasses import dataclass

from chat.application.events.base import StreamEvent


@dataclass(frozen=True)
class StepStartEvent(StreamEvent):
    """An agent step started."""

    pass


@dataclass(frozen=True)
class StepFinishEvent(StreamEvent):
    """An agent step finished."""

    pass

from dataclasses import dataclass

from chat.application.events.base import StreamEvent


@dataclass(frozen=True)
class StepStartEvent(StreamEvent):
    """一个 agent step 开始。"""

    pass


@dataclass(frozen=True)
class StepFinishEvent(StreamEvent):
    """一个 agent step 结束。"""

    pass

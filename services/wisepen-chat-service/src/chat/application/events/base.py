from dataclasses import dataclass


@dataclass(frozen=True)
class StreamEvent:
    """应用层流式事件基类。"""

    pass

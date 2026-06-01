from dataclasses import dataclass


@dataclass(frozen=True)
class StreamEvent:
    """Base class for application stream events."""

    pass

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ToolExecutionStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    DENIED = "denied"
    INVALID_INPUT = "invalid_input"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class ToolExecutionError:
    code: str
    message: str
    detail: str | None = None
    retryable: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class ToolBusinessError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: ToolExecutionStatus = ToolExecutionStatus.FAILED,
        detail: str | None = None,
        retryable: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.detail = detail
        self.retryable = retryable
        self.metadata = metadata or {}

    def to_error(self) -> ToolExecutionError:
        return ToolExecutionError(
            code=self.code,
            message=self.message,
            detail=self.detail,
            retryable=self.retryable,
            metadata=self.metadata,
        )


@dataclass(frozen=True)
class ToolExecutionResult:
    call_id: str
    tool_name: str
    status: ToolExecutionStatus
    input: dict[str, Any]
    output: Any | None
    error: ToolExecutionError | None
    started_at: datetime
    finished_at: datetime
    ephemeral: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolBatchResult:
    results: list[ToolExecutionResult]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReducedToolResult:
    result: ToolExecutionResult
    llm_content: str

    @property
    def call_id(self) -> str:
        return self.result.call_id

    @property
    def tool_name(self) -> str:
        return self.result.tool_name

    @property
    def ephemeral(self) -> bool:
        return self.result.ephemeral


@dataclass(frozen=True)
class ReducedToolBatch:
    items: list[ReducedToolResult]
    results: list[ToolExecutionResult]


class ToolResultLLMRenderer:
    def render(self, result: ToolExecutionResult) -> str:
        if result.status == ToolExecutionStatus.SUCCESS:
            return self._stringify(result.output)

        message = result.error.message if result.error else "Tool execution failed."
        return f"[Tool Error: {result.status.value}] {message}"

    @staticmethod
    def _stringify(output: Any) -> str:
        if output is None:
            return ""
        if isinstance(output, str):
            return output
        return str(output)


class ToolBatchReducer:
    def __init__(self, llm_renderer: ToolResultLLMRenderer | None = None) -> None:
        self._llm_renderer = llm_renderer or ToolResultLLMRenderer()

    def reduce(
        self,
        results: list[ToolExecutionResult],
    ) -> ReducedToolBatch:
        items = [
            ReducedToolResult(
                result=result,
                llm_content=self._llm_renderer.render(result),
            )
            for result in results
        ]

        return ReducedToolBatch(
            items=items,
            results=results,
        )


class ToolExecutionRecorder:
    async def record_batch(self, results: list[ToolExecutionResult]) -> None:
        return None

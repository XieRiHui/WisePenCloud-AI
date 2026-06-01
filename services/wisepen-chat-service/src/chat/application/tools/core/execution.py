import asyncio
from datetime import datetime, timezone
from typing import Any

from common.logger import log_fail

from chat.application.tools.core.checkers import (
    InputSizeLimitHook,
    JsonSchemaRequiredHook,
    RequiredContextHook,
    ToolInputHook,
)
from chat.application.tools.core.definition import ToolExecutionRequest
from chat.application.tools.core.invocation import ToolInvocation
from chat.application.tools.core.result import (
    ToolBatchResult,
    ToolBusinessError,
    ToolExecutionError,
    ToolExecutionResult,
    ToolExecutionStatus,
)
from chat.application.tools.core.scope import ToolScope


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ToolExecutor:
    def __init__(
        self,
        tool_scope: ToolScope,
        global_hooks: list[ToolInputHook] | None = None,
    ) -> None:
        self._tool_scope = tool_scope
        self._global_hooks = global_hooks or [
            RequiredContextHook(),
            InputSizeLimitHook(),
            JsonSchemaRequiredHook(),
        ]

    async def execute_one(self, invocation: ToolInvocation) -> ToolExecutionResult:
        started_at = _utc_now()
        tool = self._tool_scope.get(invocation.tool_name)
        if tool is None:
            return self._error_result(
                invocation,
                status=ToolExecutionStatus.DENIED,
                code="tool_not_found",
                message=f"Tool '{invocation.tool_name}' is not available in this scope.",
                started_at=started_at,
            )

        policy = tool.definition.runtime_policy
        context = self._tool_scope.context

        for hook in [*self._global_hooks, *tool.definition.input_hooks]:
            check = await hook.check(invocation, tool, policy, context)
            if not check.ok:
                return self._error_result(
                    invocation,
                    status=check.status or ToolExecutionStatus.INVALID_INPUT,
                    code=check.code or "preflight_failed",
                    message=check.message or "Tool input preflight failed.",
                    started_at=started_at,
                    ephemeral=policy.ephemeral_output,
                    metadata=check.metadata,
                )

        try:
            request = ToolExecutionRequest(
                invocation=invocation,
                context=context,
                policy=policy,
            )
            output = await self._run_with_policy(tool.execute(request), policy.timeout_seconds)
            return ToolExecutionResult(
                call_id=invocation.call_id,
                tool_name=invocation.tool_name,
                status=ToolExecutionStatus.SUCCESS,
                input=invocation.input,
                output=output,
                error=None,
                started_at=started_at,
                finished_at=_utc_now(),
                ephemeral=policy.ephemeral_output,
            )
        except TimeoutError:
            log_fail("工具调用超时", "timeout", name=invocation.tool_name)
            return self._error_result(
                invocation,
                status=ToolExecutionStatus.TIMEOUT,
                code="tool_timeout",
                message=f"Tool '{invocation.tool_name}' timed out.",
                started_at=started_at,
                ephemeral=policy.ephemeral_output,
            )
        except ToolBusinessError as exc:
            return self._error_result(
                invocation,
                status=exc.status,
                code=exc.code,
                message=exc.message,
                started_at=started_at,
                ephemeral=policy.ephemeral_output,
                detail=exc.detail,
                retryable=exc.retryable,
                metadata=exc.metadata,
            )
        except Exception as exc:
            log_fail("工具调用", exc, name=invocation.tool_name)
            return self._error_result(
                invocation,
                status=ToolExecutionStatus.FAILED,
                code="tool_exception",
                message=f"{type(exc).__name__}: {exc}",
                started_at=started_at,
                ephemeral=policy.ephemeral_output,
            )

    async def _run_with_policy(self, awaitable: Any, timeout_seconds: float | None) -> Any:
        if timeout_seconds is None:
            return await awaitable
        try:
            return await asyncio.wait_for(awaitable, timeout=timeout_seconds)
        except asyncio.TimeoutError as exc:
            raise TimeoutError() from exc

    @staticmethod
    def _error_result(
        invocation: ToolInvocation,
        *,
        status: ToolExecutionStatus,
        code: str,
        message: str,
        started_at: datetime,
        ephemeral: bool = False,
        detail: str | None = None,
        retryable: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> ToolExecutionResult:
        return ToolExecutionResult(
            call_id=invocation.call_id,
            tool_name=invocation.tool_name,
            status=status,
            input=invocation.input,
            output=None,
            error=ToolExecutionError(
                code=code,
                message=message,
                detail=detail,
                retryable=retryable,
                metadata=metadata or {},
            ),
            started_at=started_at,
            finished_at=_utc_now(),
            ephemeral=ephemeral,
            metadata=metadata or {},
        )


class ToolDispatcher:
    async def dispatch(
        self,
        invocations: list[ToolInvocation],
        tool_scope: ToolScope,
    ) -> ToolBatchResult:
        executor = ToolExecutor(tool_scope)
        results = await asyncio.gather(
            *[executor.execute_one(invocation) for invocation in invocations],
            return_exceptions=False,
        )
        return ToolBatchResult(results=list(results))

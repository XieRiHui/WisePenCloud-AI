import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from chat.application.tools.core.definition import Tool, ToolRuntimePolicy
from chat.application.tools.core.invocation import ToolInvocation
from chat.application.tools.core.result import ToolExecutionStatus


@dataclass(frozen=True)
class ToolCheckResult:
    ok: bool
    status: ToolExecutionStatus | None = None
    code: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def pass_() -> "ToolCheckResult":
        return ToolCheckResult(ok=True)

    @staticmethod
    def fail(
        status: ToolExecutionStatus,
        code: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> "ToolCheckResult":
        return ToolCheckResult(
            ok=False,
            status=status,
            code=code,
            message=message,
            metadata=metadata or {},
        )


class ToolInputHook(Protocol):
    name: str

    async def check(
        self,
        invocation: ToolInvocation,
        tool: Tool,
        policy: ToolRuntimePolicy,
        context: dict[str, Any],
    ) -> ToolCheckResult:
        ...


class RequiredContextHook:
    name = "required_context"

    async def check(
        self,
        invocation: ToolInvocation,
        tool: Tool,
        policy: ToolRuntimePolicy,
        context: dict[str, Any],
    ) -> ToolCheckResult:
        missing = [key for key in policy.required_context_keys if key not in context]
        if missing:
            return ToolCheckResult.fail(
                ToolExecutionStatus.DENIED,
                "missing_context",
                f"Missing required context keys: {missing}",
                {"missing": missing},
            )
        return ToolCheckResult.pass_()


class InputSizeLimitHook:
    name = "input_size_limit"

    async def check(
        self,
        invocation: ToolInvocation,
        tool: Tool,
        policy: ToolRuntimePolicy,
        context: dict[str, Any],
    ) -> ToolCheckResult:
        if policy.max_input_chars is None:
            return ToolCheckResult.pass_()
        raw = json.dumps(invocation.input, ensure_ascii=False)
        if len(raw) > policy.max_input_chars:
            return ToolCheckResult.fail(
                ToolExecutionStatus.INVALID_INPUT,
                "input_too_large",
                f"Tool input exceeds {policy.max_input_chars} characters.",
                {"input_chars": len(raw), "max_input_chars": policy.max_input_chars},
            )
        return ToolCheckResult.pass_()


class JsonSchemaRequiredHook:
    name = "json_schema_required"

    async def check(
        self,
        invocation: ToolInvocation,
        tool: Tool,
        policy: ToolRuntimePolicy,
        context: dict[str, Any],
    ) -> ToolCheckResult:
        schema = tool.definition.llm_spec.parameters_schema
        if schema.get("type") != "object":
            return ToolCheckResult.pass_()
        required = schema.get("required") or []
        missing = [key for key in required if key not in invocation.input]
        if missing:
            return ToolCheckResult.fail(
                ToolExecutionStatus.INVALID_INPUT,
                "missing_required_input",
                f"Missing required tool arguments: {missing}",
                {"missing": missing},
            )
        return ToolCheckResult.pass_()


class AllowedSkillIdHook:
    name = "allowed_skill_id"

    async def check(
        self,
        invocation: ToolInvocation,
        tool: Tool,
        policy: ToolRuntimePolicy,
        context: dict[str, Any],
    ) -> ToolCheckResult:
        skill_id = (invocation.input.get("skill_id") or "").strip()
        allowed = set(context.get("allowed_skill_ids") or [])
        if skill_id not in allowed:
            return ToolCheckResult.fail(
                ToolExecutionStatus.DENIED,
                "skill_not_available",
                f"Skill '{skill_id}' is not available in this turn.",
                {"skill_id": skill_id, "allowed": sorted(allowed)},
            )
        return ToolCheckResult.pass_()

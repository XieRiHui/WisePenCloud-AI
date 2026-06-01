from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from chat.application.tools.core.checkers import ToolInputHook


class ToolTimeoutStrategy(StrEnum):
    CANCEL_TASK = "cancel_task"
    MARK_TIMEOUT_ONLY = "mark_timeout_only"


class ToolRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ToolLLMSpec:
    name: str
    description: str
    parameters_schema: dict[str, Any]

    def to_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }


@dataclass(frozen=True)
class ToolRuntimePolicy:
    """Framework-side execution policy for a tool.

    Field status:
    - timeout_seconds: enforced by ToolExecutor with asyncio.wait_for().
    - reserved: enforced by ToolRegistry.derive() when building ToolScope.
    - ephemeral_output: propagated to ToolExecutionResult and Role.TOOL messages.
    - required_context_keys: enforced by RequiredContextHook before tool execution.
    - max_input_chars: enforced by InputSizeLimitHook before tool execution.
    - max_output_chars: currently advisory; concrete tools may still truncate locally.
      Intended owner is a future output-size hook/normalizer in the core result path.
    - allow_parallel: currently advisory; ToolDispatcher still runs all calls via gather().
      Intended to support serial groups or high-risk tools that must not run in parallel.
    - risk_level: currently metadata only. Intended for audit, approval, or policy gating.
    - timeout_strategy: currently metadata only; timeout_seconds always cancels the task.
      Intended to support non-cancelling timeout reports or stronger sandbox/process kill.
    """

    timeout_seconds: float | None = None
    timeout_strategy: ToolTimeoutStrategy = ToolTimeoutStrategy.CANCEL_TASK
    reserved: bool = False
    ephemeral_output: bool = False
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    required_context_keys: tuple[str, ...] = ()
    max_input_chars: int | None = None
    max_output_chars: int | None = None
    allow_parallel: bool = True


@dataclass(frozen=True)
class ToolDefinition:
    llm_spec: ToolLLMSpec
    runtime_policy: ToolRuntimePolicy = field(default_factory=ToolRuntimePolicy)
    input_hooks: tuple["ToolInputHook", ...] = ()


@dataclass(frozen=True)
class ToolExecutionRequest:
    invocation: "ToolInvocation"
    context: dict[str, Any]
    policy: ToolRuntimePolicy


class Tool(Protocol):
    @property
    def definition(self) -> ToolDefinition:
        ...

    async def execute(self, request: ToolExecutionRequest) -> Any:
        ...


from chat.application.tools.core.invocation import ToolInvocation  # noqa: E402

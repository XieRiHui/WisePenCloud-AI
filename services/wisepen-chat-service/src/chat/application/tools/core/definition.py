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
    """工具的框架侧运行约束。

    字段状态：
    - timeout_seconds：已由 ToolExecutor 通过 asyncio.wait_for() 执行。
    - reserved：已由 ToolRegistry.derive() 在构造 ToolScope 时执行。
    - ephemeral_output：已传递到 ToolExecutionResult 和 Role.TOOL 消息。
    - required_context_keys：已由 RequiredContextHook 在工具执行前检查。
    - max_input_chars：已由 InputSizeLimitHook 在工具执行前检查。
    - max_output_chars：当前是约束声明，具体工具仍可能自己截断输出。
      后续应由 core 结果链路中的输出尺寸 hook/normalizer 统一处理。
    - allow_parallel：当前是约束声明，ToolDispatcher 仍用 gather() 并发执行。
      后续用于支持串行分组，或禁止高风险工具并行执行。
    - risk_level：当前只是元数据。后续用于审计、审批或策略阻断。
    - timeout_strategy：当前只是元数据；timeout_seconds 总是取消协程任务。
      后续用于支持只标记超时、不取消，或更强的沙箱/进程 kill。
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

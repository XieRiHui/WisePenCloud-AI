from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, AsyncGenerator, List, Dict, Optional, Any
from chat.domain.entities import ChatMessage
from chat.domain.entities.provider import ProviderType

if TYPE_CHECKING:
    from chat.domain.repositories.model_repo import ModelRequestInfo

@dataclass
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

@dataclass
class LLMCompletionResult:
    content: str
    token_usage: int
    raw: Any = None

@dataclass
class LLMToolCall:
    call_id: str
    name: str
    arguments: dict[str, Any]

class LLMEventType(str, Enum):
    TEXT_DELTA = "TEXT_DELTA"
    REASONING_DELTA = "REASONING_DELTA"
    TOOL_CALLS = "TOOL_CALLS"
    USAGE = "USAGE"
    STATE = "STATE"

@dataclass
class LLMStreamEvent:
    type: LLMEventType
    delta: str | None = None
    tool_calls: list[LLMToolCall] | None = None
    usage: LLMUsage | None = None
    provider_payload: dict[str, Any] | None = None
    response_id: str | None = None

class LLMProvider(ABC):
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        pass

    def supports_tools(self, model_request: "ModelRequestInfo") -> bool:
        return True

    @abstractmethod
    async def stream_chat_completion(
            self,
            messages: List[ChatMessage],
            model_request: "ModelRequestInfo",
            tools: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[LLMStreamEvent, None]:
        yield  # type: ignore[misc]

class TextCompletionProvider(ABC):
    @abstractmethod
    async def chat_completion(
            self,
            messages: List[ChatMessage],
            model_name: str,
            temperature: float = 0.7,
            tools: Optional[List[Dict[str, Any]]] = None,
            api_base: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> LLMCompletionResult:
        pass

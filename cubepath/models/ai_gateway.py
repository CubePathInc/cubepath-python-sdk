from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ChatMessage",
    "ToolCall",
    "FunctionCall",
    "Tool",
    "ToolFunction",
    "ChatCompletionRequest",
    "ChatCompletionChoice",
    "CompletionUsage",
    "ChatCompletionResponse",
    "ChatCompletionChunk",
    "ChatCompletionDelta",
    "DeltaContent",
    "ModelPricing",
    "ModelCapabilities",
    "ModelLimits",
    "ModelInfo",
    "ModelListResponse",
]


# --- Messages and tools ---


@dataclass
class FunctionCall:
    name: str = ""
    arguments: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FunctionCall:
        return cls(
            name=data.get("name", ""),
            arguments=data.get("arguments", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "arguments": self.arguments}


@dataclass
class ToolCall:
    id: str = ""
    type: str = "function"
    function: FunctionCall = field(default_factory=FunctionCall)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolCall:
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "function"),
            function=FunctionCall.from_dict(data.get("function", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type, "function": self.function.to_dict()}


@dataclass
class ChatMessage:
    role: str = ""
    content: Any = ""
    name: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatMessage:
        tool_calls = [ToolCall.from_dict(tc) for tc in data.get("tool_calls", []) or []]
        return cls(
            role=data.get("role", ""),
            content=data.get("content", ""),
            name=data.get("name", ""),
            tool_calls=tool_calls,
            tool_call_id=data.get("tool_call_id", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.name:
            d["name"] = self.name
        if self.tool_calls:
            d["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d


@dataclass
class ToolFunction:
    name: str = ""
    description: str = ""
    parameters: Any = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"name": self.name}
        if self.description:
            d["description"] = self.description
        if self.parameters is not None:
            d["parameters"] = self.parameters
        return d


@dataclass
class Tool:
    type: str = "function"
    function: ToolFunction = field(default_factory=ToolFunction)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "function": self.function.to_dict()}


# --- Request ---


@dataclass
class ChatCompletionRequest:
    """Request for the chat completions endpoint.

    ``model`` uses the ``"provider/model_id"`` format,
    e.g. ``"openai/gpt-4o"`` or ``"anthropic/claude-sonnet-4-20250514"``.
    """

    model: str = ""
    messages: list[ChatMessage] = field(default_factory=list)
    temperature: float | None = None
    top_p: float | None = None
    n: int | None = None
    stream: bool = False
    stop: Any = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    user: str = ""
    tools: list[Tool] = field(default_factory=list)
    tool_choice: Any = None
    response_format: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "model": self.model,
            "messages": [m.to_dict() for m in self.messages],
        }
        if self.temperature is not None:
            d["temperature"] = self.temperature
        if self.top_p is not None:
            d["top_p"] = self.top_p
        if self.n is not None:
            d["n"] = self.n
        if self.stream:
            d["stream"] = True
        if self.stop is not None:
            d["stop"] = self.stop
        if self.max_tokens is not None:
            d["max_tokens"] = self.max_tokens
        if self.presence_penalty is not None:
            d["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty is not None:
            d["frequency_penalty"] = self.frequency_penalty
        if self.user:
            d["user"] = self.user
        if self.tools:
            d["tools"] = [t.to_dict() for t in self.tools]
        if self.tool_choice is not None:
            d["tool_choice"] = self.tool_choice
        if self.response_format is not None:
            d["response_format"] = self.response_format
        return d


# --- Response (non-streaming) ---


@dataclass
class CompletionUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompletionUsage:
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )


@dataclass
class ChatCompletionChoice:
    index: int = 0
    message: ChatMessage = field(default_factory=ChatMessage)
    finish_reason: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatCompletionChoice:
        return cls(
            index=data.get("index", 0),
            message=ChatMessage.from_dict(data.get("message", {})),
            finish_reason=data.get("finish_reason"),
        )


@dataclass
class ChatCompletionResponse:
    id: str = ""
    object: str = "chat.completion"
    created: int = 0
    model: str = ""
    choices: list[ChatCompletionChoice] = field(default_factory=list)
    usage: CompletionUsage | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatCompletionResponse:
        usage = CompletionUsage.from_dict(data["usage"]) if data.get("usage") else None
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion"),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=[ChatCompletionChoice.from_dict(c) for c in data.get("choices", [])],
            usage=usage,
        )


# --- Streaming types ---


@dataclass
class DeltaContent:
    role: str = ""
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeltaContent:
        tool_calls = [ToolCall.from_dict(tc) for tc in data.get("tool_calls", []) or []]
        return cls(
            role=data.get("role", ""),
            content=data.get("content", ""),
            tool_calls=tool_calls,
        )


@dataclass
class ChatCompletionDelta:
    index: int = 0
    delta: DeltaContent = field(default_factory=DeltaContent)
    finish_reason: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatCompletionDelta:
        return cls(
            index=data.get("index", 0),
            delta=DeltaContent.from_dict(data.get("delta", {})),
            finish_reason=data.get("finish_reason"),
        )


@dataclass
class ChatCompletionChunk:
    id: str = ""
    object: str = "chat.completion.chunk"
    created: int = 0
    model: str = ""
    choices: list[ChatCompletionDelta] = field(default_factory=list)
    usage: CompletionUsage | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatCompletionChunk:
        usage = CompletionUsage.from_dict(data["usage"]) if data.get("usage") else None
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "chat.completion.chunk"),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=[ChatCompletionDelta.from_dict(c) for c in data.get("choices", [])],
            usage=usage,
        )


# --- Model listing ---


@dataclass
class ModelPricing:
    input_per_million_tokens: str = ""
    output_per_million_tokens: str = ""
    currency: str = "USD"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelPricing:
        return cls(
            input_per_million_tokens=data.get("input_per_million_tokens", ""),
            output_per_million_tokens=data.get("output_per_million_tokens", ""),
            currency=data.get("currency", "USD"),
        )


@dataclass
class ModelCapabilities:
    streaming: bool = False
    vision: bool = False
    tools: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelCapabilities:
        return cls(
            streaming=data.get("streaming", False),
            vision=data.get("vision", False),
            tools=data.get("tools", False),
        )


@dataclass
class ModelLimits:
    max_context_tokens: int = 0
    max_output_tokens: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelLimits:
        return cls(
            max_context_tokens=data.get("max_context_tokens", 0),
            max_output_tokens=data.get("max_output_tokens", 0),
        )


@dataclass
class ModelInfo:
    id: str = ""
    object: str = "model"
    owned_by: str = ""
    pricing: ModelPricing = field(default_factory=ModelPricing)
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    limits: ModelLimits = field(default_factory=ModelLimits)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelInfo:
        return cls(
            id=data.get("id", ""),
            object=data.get("object", "model"),
            owned_by=data.get("owned_by", ""),
            pricing=ModelPricing.from_dict(data.get("pricing", {})),
            capabilities=ModelCapabilities.from_dict(data.get("capabilities", {})),
            limits=ModelLimits.from_dict(data.get("limits", {})),
        )


@dataclass
class ModelListResponse:
    object: str = "list"
    data: list[ModelInfo] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelListResponse:
        return cls(
            object=data.get("object", "list"),
            data=[ModelInfo.from_dict(m) for m in data.get("data", [])],
        )

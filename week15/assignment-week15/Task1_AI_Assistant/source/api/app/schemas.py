from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    quote: str = Field(max_length=400)


class Answer(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low"]
    citations: list[Citation] = []
    follow_up: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str = "default"
    use_tools: bool = True
    use_rag: bool | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)


class BatchRequest(BaseModel):
    messages: list[str] = Field(min_length=1, max_length=32)
    use_tools: bool = False


class Source(BaseModel):
    source: str
    score: float
    text: str
    category: str | None = None


class ChatResponse(BaseModel):
    answer: str
    confidence: str
    citations: list[Citation] = []
    follow_up: str | None = None
    agent: str | None
    router_agent: str | None
    router_confidence: float
    router_energy: float
    router_agrees: bool | None = None
    out_of_scope: bool
    sources: list[Source] = []
    tool_calls: list[str] = []
    tool_results: list[dict] = []
    cache: Literal["miss", "exact", "semantic"] = "miss"
    degraded: bool = False
    model: str
    latency_ms: int


class IngestResponse(BaseModel):
    files: int
    chunks: int
    collection: str

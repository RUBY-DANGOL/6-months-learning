from pydantic import BaseModel


class AgentRequest(BaseModel):
    question: str


class AgentResponse(BaseModel):
    sql: str
    result: list | None = None
    summary: str
    status: str
    error: str | None = None
    execution_time: float | None = None
    retries: int = 0

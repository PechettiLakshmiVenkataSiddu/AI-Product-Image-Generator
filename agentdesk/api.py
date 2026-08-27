from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent import format_reasoning_trace, run_agent_turn
from config import get_settings, setup_logging

settings = get_settings()
setup_logging(settings)

app = FastAPI(title="AgentDesk API", version="1.0.0")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = "api-default"
    debug: bool = False


class ChatResponse(BaseModel):
    output: str
    reasoning_trace: list[str] | None = None


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    result = run_agent_turn(
        message=payload.message,
        session_id=payload.session_id,
        debug=payload.debug,
    )

    reasoning_trace = None
    if payload.debug:
        reasoning_trace = format_reasoning_trace(result.get("intermediate_steps", []))

    return ChatResponse(output=result.get("output", ""), reasoning_trace=reasoning_trace)

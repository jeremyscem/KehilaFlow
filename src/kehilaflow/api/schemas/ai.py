from typing import Literal

from pydantic import BaseModel, Field


class AIChatHistoryMessage(BaseModel):
    role: Literal[
        "user",
        "assistant",
    ]

    content: str


class AIChatRequest(BaseModel):
    message: str

    history: list[AIChatHistoryMessage] = Field(default_factory=list)

    pending_action_token: str | None = None


class AIChatResponse(BaseModel):
    answer: str

    pending_action_token: str | None = None

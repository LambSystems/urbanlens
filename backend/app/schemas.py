from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# --- Core ---

class LatLng(BaseModel):
    lat: float
    lng: float


# --- Session ---

class SessionStatus(str, Enum):
    region_loaded = "region_loaded"
    investigating = "investigating"
    answered = "answered"


class ChainOfThoughtStepType(str, Enum):
    reasoning = "reasoning"
    tool_call = "tool_call"
    answer = "answer"


class StepStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    error = "error"


class ChainOfThoughtStep(BaseModel):
    step_id: str
    step_type: ChainOfThoughtStepType
    tool_name: str | None = None
    status: StepStatus = StepStatus.running
    summary: str = ""
    evidence: dict | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class SessionMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    message_index: int = 0
    chain_of_thought: list[ChainOfThoughtStep] = Field(default_factory=list)


class Session(BaseModel):
    session_id: str
    center: LatLng
    radius_m: int = 120
    status: SessionStatus = SessionStatus.region_loaded
    messages: list[SessionMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now())


# --- Requests / Responses ---

class CreateSessionRequest(BaseModel):
    center: LatLng
    radius_m: int = Field(default=120, ge=1, le=1000)


class UserPromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)


class InvestigationResponse(BaseModel):
    session_id: str
    prompt: str
    chain_of_thought: list[ChainOfThoughtStep]
    answer: str

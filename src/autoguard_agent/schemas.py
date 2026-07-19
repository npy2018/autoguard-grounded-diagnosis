from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    uri: str
    source_type: Literal["log", "video", "version", "replay", "case"]
    summary: str
    value: Any = None


class ToolCallRecord(BaseModel):
    tool: str
    arguments: dict[str, Any]
    evidence: list[Evidence]


class Hypothesis(BaseModel):
    statement: str
    confidence: float = Field(ge=0, le=1)
    support: list[Evidence]
    counter_evidence: list[Evidence] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    falsifiable_prediction: str
    recommended_experiment: str
    status: Literal["candidate", "supported", "rejected", "insufficient_evidence"]


class DiagnosisReport(BaseModel):
    event_id: str
    hypotheses: list[Hypothesis]
    tool_trace: list[ToolCallRecord]
    grounded: bool
    stop_reason: str

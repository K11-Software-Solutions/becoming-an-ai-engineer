"""The data the assistant produces. Structured outputs turn a model's reply into these types."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AcceptanceCriterion(BaseModel):
    given: str = Field(description="The starting situation")
    when: str = Field(description="What the user does")
    then: str = Field(description="The observable result")


class UserStory(BaseModel):
    title: str = Field(description="A short title, at most 80 characters")
    as_a: str = Field(description="The kind of user")
    i_want: str = Field(description="What they want to do")
    so_that: str = Field(description="Why it matters to them")
    acceptance_criteria: list[AcceptanceCriterion] = Field(description="Given/When/Then criteria, at least two")
    open_questions: list[str] = Field(description="What the request leaves unclear; empty if nothing")
    priority: Literal["low", "medium", "high"]


class TriageDecision(BaseModel):
    decision: Literal["duplicate", "related", "new"]
    story_id: str | None = Field(description="The existing story, for duplicate or related; otherwise null")
    reason: str

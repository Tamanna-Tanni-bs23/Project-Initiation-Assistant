"""Extract goals, stakeholders, functional requirements, and constraints from raw input."""

from typing import List

import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = (
    "You are a business analyst extracting structured requirements from raw "
    "project-discovery input (meeting notes, a client requirement document, or a "
    "voice transcript). Extract only what is stated or clearly implied by the "
    "text — do not invent requirements, stakeholders, or constraints that aren't "
    "grounded in the input."
)


class RequirementAnalysis(BaseModel):
    goals: List[str]
    stakeholders: List[str]
    functional_requirements: List[str]
    constraints: List[str]


def analyze(raw_text: str) -> dict:
    """Return {"goals": [...], "stakeholders": [...], "functional_requirements": [...], "constraints": [...]}."""
    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw_text}],
        output_format=RequirementAnalysis,
    )
    return response.parsed_output.model_dump()

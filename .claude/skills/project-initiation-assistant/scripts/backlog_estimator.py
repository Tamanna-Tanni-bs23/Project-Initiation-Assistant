"""Assign Story Points, Priority, and Complexity to user stories; surface project risks."""

import json
from typing import List

import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-4-8"

STORY_POINT_SCALE = [1, 2, 3, 5, 8, 13, 21]

ESTIMATE_SYSTEM_PROMPT = (
    "You are a technical lead estimating a backlog. You are given a list of "
    "user stories, each with an id, the story text, and its acceptance "
    "criteria. For each story, assign:\n"
    "- priority: High, Medium, or Low, based on how central the story is to "
    "the product's core goals\n"
    f"- story_points: one of {STORY_POINT_SCALE} (Fibonacci-like scale), sized "
    "relative to the other stories in this same list — the smallest, simplest "
    "story should get the lowest number\n"
    "- complexity: Low, Medium, or High, reflecting technical difficulty "
    "(integrations, data migrations, unclear requirements, etc.), which is "
    "independent from priority\n\n"
    "Return exactly one estimate per input story_id — do not add, drop, or "
    "merge stories."
)

RISK_SYSTEM_PROMPT = (
    "You are a project manager identifying delivery risks from a requirement "
    "analysis and its resulting backlog. Surface risks grounded in the "
    "constraints, ambiguous or conflicting requirements, dependencies between "
    "stories, and anything the stakeholders or goals suggest could delay or "
    "derail the project. For each risk, give a one-sentence impact statement "
    "and a concrete, actionable mitigation. Do not pad the list with generic "
    "software-project risks that aren't grounded in the given input."
)


class StoryEstimate(BaseModel):
    story_id: str
    priority: str
    story_points: int
    complexity: str


class EstimateList(BaseModel):
    estimates: List[StoryEstimate]


class Risk(BaseModel):
    risk: str
    impact: str
    mitigation: str


class RiskList(BaseModel):
    risks: List[Risk]


def estimate(user_stories: List[dict]) -> List[dict]:
    """Return user_stories with "priority", "story_points", "complexity" fields added."""
    client = anthropic.Anthropic()
    stories_payload = [
        {
            "story_id": story["story_id"],
            "story": story["story"],
            "acceptance_criteria": story.get("acceptance_criteria", []),
        }
        for story in user_stories
    ]
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=ESTIMATE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"User stories:\n\n{json.dumps(stories_payload, indent=2)}",
            }
        ],
        output_format=EstimateList,
    )
    estimates_by_id = {
        e.story_id: e.model_dump() for e in response.parsed_output.estimates
    }
    return [
        {
            **story,
            **{
                k: v
                for k, v in estimates_by_id.get(story["story_id"], {}).items()
                if k != "story_id"
            },
        }
        for story in user_stories
    ]


def identify_risks(analysis: dict, user_stories: List[dict]) -> List[dict]:
    """Return [{"risk": ..., "impact": ..., "mitigation": ...}, ...]."""
    client = anthropic.Anthropic()
    story_summaries = [
        {"story_id": story["story_id"], "story": story["story"]}
        for story in user_stories
    ]
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=RISK_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Requirement analysis (JSON):\n\n"
                    f"{json.dumps(analysis, indent=2)}\n\n"
                    "Backlog (JSON):\n\n"
                    f"{json.dumps(story_summaries, indent=2)}"
                ),
            }
        ],
        output_format=RiskList,
    )
    return [risk.model_dump() for risk in response.parsed_output.risks]

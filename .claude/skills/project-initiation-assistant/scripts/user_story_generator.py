"""Derive Epics and User Stories (As a / I want / So that) from a PRD (see references/user_story_template.md)."""

import json
from pathlib import Path
from typing import List

import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-4-8"

TEMPLATE_PATH = Path(__file__).parent.parent / "references" / "user_story_template.md"

EPIC_SYSTEM_PROMPT = (
    "You are a business analyst grouping a PRD's functional requirements into "
    "epics. Read the PRD and identify the distinct, cohesive bodies of work it "
    "describes. For each epic, give a sequential ID (EPIC-1, EPIC-2, ...), a "
    "short name, and a one- or two-sentence description. Every functional "
    "requirement in the PRD must map to exactly one epic; do not invent epics "
    "that aren't grounded in the PRD."
)

USER_STORY_SYSTEM_PROMPT = (
    "You are a business analyst writing user stories for a single epic, in the "
    "format described here:\n\n"
    f"{TEMPLATE_PATH.read_text()}\n\n"
    "Write one or more user stories that fully cover the epic's description. "
    "Give each story a sequential ID scoped to the epic (<epic_id>-1, "
    "<epic_id>-2, ...), the story itself as 'As a ... / I want ... / So that "
    "...', and 2-5 concrete, testable acceptance criteria in Given/When/Then "
    "form. Do not invent scope beyond the epic's description."
)


class Epic(BaseModel):
    epic_id: str
    name: str
    description: str


class EpicList(BaseModel):
    epics: List[Epic]


class UserStory(BaseModel):
    story_id: str
    epic_id: str
    story: str
    acceptance_criteria: List[str]


class UserStoryList(BaseModel):
    stories: List[UserStory]


def generate_epics(prd: str) -> List[dict]:
    """Return [{"epic_id": ..., "name": ..., "description": ...}, ...]."""
    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=EPIC_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"PRD:\n\n{prd}"}],
        output_format=EpicList,
    )
    return [epic.model_dump() for epic in response.parsed_output.epics]


def generate_user_stories(epics: List[dict]) -> List[dict]:
    """Return [{"story_id": ..., "epic_id": ..., "story": ..., "acceptance_criteria": [...]}, ...]."""
    client = anthropic.Anthropic()
    all_stories: List[dict] = []
    for epic in epics:
        response = client.messages.parse(
            model=MODEL,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=USER_STORY_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Epic:\n\n{json.dumps(epic, indent=2)}"}
            ],
            output_format=UserStoryList,
        )
        all_stories.extend(
            story.model_dump() for story in response.parsed_output.stories
        )
    return all_stories

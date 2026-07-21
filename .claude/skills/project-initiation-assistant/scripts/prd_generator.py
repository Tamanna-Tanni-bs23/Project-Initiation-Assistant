"""Turn analyzed requirements into a structured PRD (see references/prd_template.md)."""

import json
from pathlib import Path

import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-4-8"

TEMPLATE_PATH = Path(__file__).parent.parent / "references" / "prd_template.md"

SYSTEM_PROMPT = (
    "You are a business analyst writing a Product Requirements Document from "
    "structured requirement analysis. Fill in the following markdown template "
    "exactly — keep every heading, in order, and do not add, remove, or rename "
    "sections. Write plain prose and bullet lists under each heading; leave a "
    "heading's body empty only if the input truly gives you nothing for it. "
    "Base every statement on the provided analysis — do not invent goals, "
    "stakeholders, or requirements that aren't grounded in it.\n\n"
    f"Template:\n\n{TEMPLATE_PATH.read_text()}"
)

OVERVIEW_SYSTEM_PROMPT = (
    "You are a project manager filling in a project tracker's cover sheet from "
    "a PRD. Extract the project name, client, a one-sentence objective, and an "
    "overall priority (High, Medium, or Low, based on how the PRD frames "
    "urgency and business impact). If the PRD doesn't name a client or project "
    "name explicitly, give your best concise label grounded in the PRD's "
    "content rather than leaving it blank."
)


class ProjectOverview(BaseModel):
    project_name: str
    client: str
    objective: str
    priority: str


def generate(analysis: dict) -> str:
    """Return PRD as markdown text."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Requirement analysis (JSON):\n\n"
                    f"{json.dumps(analysis, indent=2)}"
                ),
            }
        ],
    )
    return next(block.text for block in response.content if block.type == "text")


def extract_overview(prd: str) -> dict:
    """Return {"Project Name": ..., "Client": ..., "Objective": ..., "Priority": ...} from a generated PRD."""
    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=OVERVIEW_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"PRD:\n\n{prd}"}],
        output_format=ProjectOverview,
    )
    overview = response.parsed_output
    return {
        "Project Name": overview.project_name,
        "Client": overview.client,
        "Objective": overview.objective,
        "Priority": overview.priority,
    }

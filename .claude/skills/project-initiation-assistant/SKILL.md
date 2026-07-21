---
name: project-initiation-assistant
description: >
  Converts raw requirement inputs (meeting notes, client requirement documents, voice
  transcripts) into a development-ready backlog: Project Vision, PRD, Epic List, User
  Stories, Acceptance Criteria, and Effort Estimates, then creates and populates a 
  project tracking document (spreadsheet, Jira, Linear, Airtable, or custom) in a 
  designated storage location and returns the shared tracker URL. Works with any LLM 
  backend (Claude, GPT, Gemini, local models). Use when the user provides 
  discovery-meeting notes, a requirements doc, or a transcript and wants a PRD, backlog, 
  or project tracker generated from it.
---

# Project Initiation Assistant (Multi-AI, Multi-Platform)

Automates the requirement-to-development handoff pipeline, agnostic to LLM backend or tracking platform:

```
Meeting Notes / Client Requirements
  -> Requirement Analysis
  -> PRD Generation
  -> Epic Creation
  -> User Story Creation
  -> Acceptance Criteria
  -> Effort Estimation
  -> Tracker Population (Sheets/Jira/Linear/Custom)
  -> Development-Ready Backlog
```

## Inputs

Accept any one of:
- Raw meeting notes (text)
- Client requirement document
- Voice transcript (text)

## Pipeline stages

Run in order; each stage's output feeds the next. The orchestrator wires all stages together.

1. **Requirement Analyzer** — Extract goals, stakeholders, functional requirements, constraints from raw input. Returns structured analysis.
2. **PRD Generator** — Transform extracted requirements into a structured PRD using the template (`references/prd_template.md`). Extract project overview fields (Project Name, Client, Objective, Priority) back out of the generated PRD.
3. **User Story Generator** — Generate epics from the PRD, then create user stories per epic in "As a / I want / So that" form with acceptance criteria. Template: `references/user_story_template.md`.
4. **Backlog Estimation Assistant** — Assign Story Points, Priority, and Complexity to each story (sized relative to each other); surface Risks with Impact and Mitigation.
5. **Project Tracker Creator** — Create and populate tracker (Google Sheets, Jira, Linear, Airtable, or custom API) with four sections: Project Overview, Epics, User Stories, Risks. Return the shared tracker URL.

## Running the pipeline

Basic invocation (CLI):
```bash
python scripts/run_pipeline.py <input_file> --tracker-type sheets --tracker-config '{"folder_id": "..."}' --share-with alice@example.com
```

Or from Python with custom LLM:
```python
from run_pipeline import run

config = {
    "llm_provider": "openai",  # or "claude", "gemini", "local", etc.
    "tracker_type": "jira",    # or "sheets", "linear", "airtable", "custom"
    "tracker_config": {...},
    "share_with": ["alice@example.com"]
}

result = run(raw_text, config=config)
# result: {"analysis", "prd", "project_overview", "epics", "user_stories", "risks", "tracker_url"}
```

## Configuration

### LLM Backend (`llm_provider`)
- `claude` — Anthropic Claude (default)
- `openai` — OpenAI GPT
- `gemini` — Google Gemini
- `local` — Local/self-hosted model (LM Studio, Ollama, etc.)
- `custom` — Custom API endpoint

Set via env var `LLM_PROVIDER` or config dict. Requires respective API keys/credentials.

### Tracker Backend (`tracker_type`)
- `sheets` — Google Sheets (requires `GOOGLE_APPLICATION_CREDENTIALS`)
- `jira` — Atlassian Jira (requires `JIRA_API_TOKEN`, `JIRA_DOMAIN`)
- `linear` — Linear.app (requires `LINEAR_API_KEY`)
- `airtable` — Airtable (requires `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`)
- `custom` — Custom HTTP API (requires `tracker_config.endpoint`, `tracker_config.auth_header`)

## Output documents

- Project Vision
- PRD
- Epic List
- User Stories
- Acceptance Criteria
- Initial Estimates
- Tracker URL (Sheets/Jira/Linear/Airtable/custom)

## Tracker sections

See `references/sheet_schema.md` for exact columns/fields:
- Project Overview (name, client, objective, priority)
- Epics (id, name, description)
- User Stories (id, epic, story, priority, story points, acceptance criteria)
- Risks (risk, impact, mitigation)

## Success criterion

A 1-hour discovery meeting's notes should become PRD + Epic List + User Stories + Estimates + Project Tracker + shared link within a few minutes, regardless of LLM backend or tracking platform used.

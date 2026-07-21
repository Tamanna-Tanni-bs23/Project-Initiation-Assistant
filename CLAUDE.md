# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

`Assignment.pdf` (spec doc) plus a scaffolded Claude Skill at `.claude/skills/project-initiation-assistant/`. All five pipeline stage functions in `scripts/*.py` are implemented. No package manifest at the repo root, no build system, no tests — add those sections if a top-level project scaffold is added later.

## Skill layout

`.claude/skills/project-initiation-assistant/`
- `SKILL.md` — skill frontmatter (name/description) + pipeline description, loaded by Claude Code when the skill is invoked.
- `CONTEXT.md` — longer-form reference: stage-by-stage design rationale, batching decisions, environment/testing status, and known gaps. Read this before extending the pipeline.
- `scripts/` — one module per pipeline stage, all implemented, plus an orchestrator. Each stage's output is the next stage's input (see call order in SKILL.md):
  - `requirement_analyzer.py` — `analyze(raw_text) -> analysis` via `anthropic.messages.parse` + Pydantic schema.
  - `prd_generator.py` — `generate(analysis) -> prd` (text generation against `references/prd_template.md`); `extract_overview(prd) -> project_overview` pulls Project Name/Client/Objective/Priority back out of the PRD for the tracker's cover sheet.
  - `user_story_generator.py` — `generate_epics(prd) -> epics`, then `generate_user_stories(epics) -> user_stories` per epic.
  - `backlog_estimator.py` — `estimate(user_stories) -> user_stories` sizes all stories in one call for relative-points consistency; `identify_risks(analysis, user_stories) -> risks`. (These four modules all call the Claude API via `messages.parse`.)
  - `sheet_tracker.py` — Google Sheets/Drive API, not Claude: `create_tracker(...)` creates the spreadsheet, moves it into `drive_folder_id`, populates all four worksheets via `values().batchUpdate`, shares with `share_with` via Drive permissions, returns the spreadsheet URL.
  - `run_pipeline.py` — orchestrator; `run(raw_text, drive_folder_id, share_with) -> dict` chains all five stages in order (also runnable as `python scripts/run_pipeline.py <input_file> --drive-folder-id ... --share-with ...`).
  - `requirements.txt` — `anthropic`, `pydantic`, `google-api-python-client`, `google-auth`. Run `pip install -r scripts/requirements.txt` before invoking any stage. Requires `ANTHROPIC_API_KEY` (or an `ant auth login` profile) and, for `sheet_tracker.py`, `GOOGLE_APPLICATION_CREDENTIALS` pointing at a service-account key with Sheets + Drive scopes and access to the target Drive folder.
- `references/` — templates/schemas the scripts follow: `prd_template.md`, `user_story_template.md`, `sheet_schema.md`.

## Project brief (from Assignment.pdf)

Goal: build an AI Agent Skill called **Project Initiation Assistant** that automates requirement-to-development handoff.

Pipeline: Meeting Notes / Client Requirements → Requirement Analysis → PRD Generation → Epic Creation → User Story Creation → Acceptance Criteria → Effort Estimation → Google Sheet Population → Development-Ready Backlog.

### Inputs
- Raw meeting notes
- Client requirement document
- Voice transcript

### Outputs
- Documents: Project Vision, PRD, Epic List, User Stories, Acceptance Criteria, Initial Estimates
- Automated action: create + populate a Google Sheet (in a designated Drive folder) with three worksheets:
  - **Project Overview**: Project Name, Client, Objective, Priority
  - **Epics**: Epic ID, Epic Name, Description
  - **User Stories**: Story ID, Epic, Story, Priority, Story Points
  - **Risks**: Risk, Impact, Mitigation

### Sub-skills to build
1. **Requirement Analyzer** — extract goals, stakeholders, functional requirements, constraints
2. **PRD Generator** — produce structured PRD
3. **User Story Generator** — standard "As a / I want / So that" format
4. **Backlog Estimation Assistant** — assign story points, priority, complexity
5. **Google Sheet Project Tracker Creator** — create spreadsheet, create worksheets, populate data, share with project team, return spreadsheet URL

### Candidate tech stack (not yet chosen)
Google Drive API, Google Sheets API, MCP tooling, Zapier, Make.com, custom Python tool, Claude tool use, OpenAI function calling.

### Success criterion
Turn a 1-hour discovery meeting into PRD + Epic List + User Stories + Estimates + Project Tracker Spreadsheet + shared Drive link, within a few minutes.

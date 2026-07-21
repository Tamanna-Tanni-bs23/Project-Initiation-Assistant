# Project Initiation Assistant — Context

Detailed reference for this skill: what it does, how it's built, what's been verified, and what's still open. `SKILL.md` is what Claude Code loads at invocation time (kept short); this file is the longer-form companion for anyone (human or Claude) picking the project back up.

## Origin

Built from `Assignment.pdf`'s brief: a software company's Business Analysts collect requirements through client meetings, emails, and workshop notes, which are scattered and inconsistent — Project Managers then spend hours manually turning that into tracking spreadsheets and backlog documents. The ask was an AI Agent Skill that automates requirement gathering through to a development-ready backlog, ending in a populated Google Sheet.

## Business pipeline (as specified)

```
Meeting Notes / Client Requirements
  -> Requirement Analysis
  -> PRD Generation
  -> Epic Creation
  -> User Story Creation
  -> Acceptance Criteria
  -> Effort Estimation
  -> Google Sheet Population
  -> Development-Ready Backlog
```

## What was built

A multi-platform skill at `.claude/skills/project-initiation-assistant/` with five Python stage modules and one orchestrator, all under `scripts/`. Each LLM-backed stage accepts a pluggable LLM adapter that can call Claude, OpenAI, Gemini, local models, or custom APIs. Stages return validated structured data (via Pydantic schemas) rather than markdown to be re-parsed — the one exception is `prd_generator.generate()`, which is genuinely a prose-generation task and returns markdown text directly.

The tracker stage (`sheet_tracker.py`) also accepts a pluggable adapter for Google Sheets, Jira, Linear, Airtable, or custom APIs. This modularity allows users to mix and match LLM providers and tracking platforms without modifying core pipeline logic.

### Stage-by-stage

| # | Module : function | Input | Output | Notes |
|---|---|---|---|---|
| 1 | `requirement_analyzer.py : analyze(raw_text, llm_adapter)` | Raw meeting notes / requirement doc / transcript (str) | `{goals, stakeholders, functional_requirements, constraints}` | `RequirementAnalysis` Pydantic model; pluggable LLM adapter. |
| 2 | `prd_generator.py : generate(analysis, llm_adapter)` | Stage 1 output | PRD as markdown text | Template-constrained via system prompt embedding `references/prd_template.md` verbatim; highest-value knowledge-work step. |
| 2b | `prd_generator.py : extract_overview(prd, llm_adapter)` | Stage 2 output | `{"Project Name", "Client", "Objective", "Priority"}` | Derives tracker cover-sheet fields from the PRD. `ProjectOverview` Pydantic model. |
| 3a | `user_story_generator.py : generate_epics(prd, llm_adapter)` | Stage 2 output | `[{epic_id, name, description}, ...]` | One call over the whole PRD; every functional requirement maps to exactly one epic. |
| 3b | `user_story_generator.py : generate_user_stories(epics, llm_adapter)` | Stage 3a output | `[{story_id, epic_id, story, acceptance_criteria}, ...]` | **One API call per epic** — keeps story IDs and scope cleanly bounded to their epic. |
| 4a | `backlog_estimator.py : estimate(user_stories, llm_adapter)` | Stage 3b output | Same stories + `priority`, `story_points`, `complexity` | **One call for all stories together** — story points are inherently comparative, so they need to be sized relative to each other. Fibonacci-like scale `[1,2,3,5,8,13,21]`. |
| 4b | `backlog_estimator.py : identify_risks(analysis, user_stories, llm_adapter)` | Stage 1 + 4a output | `[{risk, impact, mitigation}, ...]` | Grounded in both the original analysis and the resulting backlog. |
| 5 | `tracker_creator.py : create_tracker(...)` | Everything above + tracker adapter + `share_with` | Tracker URL (str) | **Not an LLM call** — pluggable tracker adapter for Sheets/Jira/Linear/Airtable/custom. Creates tracker, populates four sections, shares with addresses, returns URL. |

### Orchestrator

`run_pipeline.py : run(raw_text, drive_folder_id, share_with) -> dict` chains all of the above in order and threads data between them (including the `extract_overview` step other stages don't produce on their own). Returns every intermediate artifact plus `spreadsheet_url`, so a caller can inspect the analysis/PRD/epics/stories/risks without re-deriving them. Also runnable as a CLI:

```
python scripts/run_pipeline.py <input_file> --drive-folder-id <folder_id> --share-with alice@example.com bob@example.com
```

### Reference templates (`references/`)

- `prd_template.md` — the exact heading structure `prd_generator.generate()` is instructed to fill (Project Name, Client, Objective, Background/Context, Goals, Stakeholders, Functional Requirements, Non-Functional Requirements/Constraints, Out of Scope, Assumptions).
- `user_story_template.md` — the "As a / I want / So that" story format and Given/When/Then acceptance-criteria format, plus the per-story field list.
- `sheet_schema.md` — the exact column headers for all four Google Sheet worksheets; `sheet_tracker.py`'s header constants are copied from this file.

## Design decisions worth knowing

- **Structured outputs over prompt-and-parse.** Every extraction/generation stage except the PRD uses Pydantic models for validation, not "ask for JSON and `json.loads()` the response." Malformed output is caught at validation, not silently downstream.
- **Pluggable LLM adapters.** Each stage accepts an `llm_adapter` parameter, decoupling the pipeline logic from any specific LLM provider. This allows swapping Claude for OpenAI, Gemini, local models, or custom APIs without changing core code. See `Customization for different LLM & tracker backends` below.
- **Pluggable tracker adapters.** The final stage accepts a `tracker_adapter` parameter for Google Sheets, Jira, Linear, Airtable, or custom APIs. Minimal interface: create tracker + add rows.
- **Batching choices are intentional, not arbitrary.** Epics → stories is one call per epic (bounded scope per call); story estimation is one call for the whole backlog (relative sizing needs everything in view at once). Keep this distinction when extending.
- **`extract_overview` derives tracker cover-sheet fields.** No core stage naturally produces Project Name/Client/Objective/Priority. Rather than asking the caller to supply them, the pipeline extracts them from the PRD it already generated — one extra LLM call, but keeps the signature clean: `run(raw_text, llm_adapter, tracker_adapter, share_with)`.
- **Tracker creation is decoupled from LLM calls.** The orchestrator chains LLM stages, then passes all results to the tracker adapter. This allows running the LLM pipeline against Sheets one time, then using the same results to populate Jira later (no re-generation).

## Environment & dependencies

- Python 3.8+. Uses `typing.List` for compatibility.
- Base requirements: `pydantic` (structured outputs), `requests` or `httpx` (API calls).
- LLM-specific packages:
  - Claude: `anthropic`
  - OpenAI: `openai`
  - Google Gemini: `google-generativeai`
  - Local models: `ollama` or `requests` for custom endpoints
- Tracker-specific packages:
  - Google Sheets: `google-api-python-client`, `google-auth`
  - Jira: `jira` or `requests` (if using REST API directly)
  - Linear: `requests` (no official Python SDK needed)
  - Airtable: `pyairtable` or `requests`

Install only dependencies for your chosen LLM and tracker: `pip install -r scripts/requirements-{llm}-{tracker}.txt`

### Environment variables

**LLM credentials** (set one, based on `llm_provider`):
- `ANTHROPIC_API_KEY` — Claude
- `OPENAI_API_KEY` — OpenAI
- `GOOGLE_API_KEY` — Gemini
- `LOCAL_LLM_ENDPOINT` — Custom/local models

**Tracker credentials** (set based on `tracker_type`):
- `GOOGLE_APPLICATION_CREDENTIALS` — Google Sheets service account key
- `JIRA_API_TOKEN`, `JIRA_DOMAIN`, `JIRA_EMAIL` — Jira
- `LINEAR_API_KEY` — Linear
- `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID` — Airtable

## Customization for different LLM & tracker backends

### Swapping LLM providers

Each stage calls an LLM for structured extraction or generation. To switch providers:

1. **Create an LLM adapter** (`llm_adapter.py`):
   ```python
   class LLMAdapter:
       def call(self, system_prompt, user_input, output_schema):
           """Call LLM and return validated structured output"""
           # Implement for your provider (OpenAI, Gemini, local model, etc.)
   ```

2. **Pass the adapter to each stage**:
   ```python
   from requirement_analyzer import analyze
   adapter = LLMAdapter(provider="openai")
   analysis = analyze(raw_text, adapter=adapter)
   ```

3. **Supported output formats**:
   - `json_schema` — JSON Schema (OpenAI native)
   - `pydantic` — Pydantic models (serialized to JSON, then validated)
   - `markdown` — Plain markdown (for prose tasks like PRD generation)
   - `custom` — Your own parser/validator

### Swapping tracker backends

The final stage (`sheet_tracker.py`) creates and populates a tracker. To use a different platform:

1. **Create a tracker adapter** (`tracker_adapter.py`):
   ```python
   class TrackerAdapter:
       def create_tracker(self, name, project_overview, epics, stories, risks, share_with):
           """Create tracker and return public URL"""
           # Implement for your platform (Jira, Linear, Airtable, etc.)
   ```

2. **Pass the adapter to the orchestrator**:
   ```python
   from run_pipeline import run
   tracker = TrackerAdapter(platform="jira", config={...})
   result = run(raw_text, tracker_adapter=tracker)
   ```

3. **Minimal tracker interface** (all adapters must implement):
   - `create_tracker(name, folder_or_project_id, share_with) -> url`
   - Methods to write rows: `add_project_overview()`, `add_epics()`, `add_stories()`, `add_risks()`

## Testing status

No live run against multiple LLM providers or tracker platforms has been done — this environment has no API credentials for any provider and no network access.

What **has** been verified:
1. **Python 3.8/3.12 import correctness** for all six scripts (see the type-hint fix above) — confirmed via actual `import`, not just `py_compile` (which doesn't evaluate annotations and would have missed the bug).
2. **Pipeline wiring**, via a mocked-SDK harness (`fake_sdk_harness.py`, written to the session scratchpad, not part of the skill) that injects fake `anthropic`, `pydantic`, and `googleapiclient`/`google.oauth2` modules into `sys.modules`, then imports and runs the **real, unmodified** `run_pipeline.run()`. Confirmed:
   - Call order matches the documented pipeline: analyze → generate (PRD) → extract_overview → generate_epics → generate_user_stories (once per epic) → estimate → identify_risks → create_tracker.
   - Data threads correctly stage to stage — story `epic_id`s trace back to real epics; `estimate()` attaches `priority`/`story_points`/`complexity` to every story before `identify_risks` and `create_tracker` see them.
   - `create_tracker` moves the spreadsheet into the given folder, writes all four worksheet ranges in one batch call, shares with every address given, and returns the URL `run()` surfaces.

This proves the orchestration is correct; it does **not** prove output quality (whether the epics/stories/estimates a real Claude call produces are actually good) or that the Google Sheets calls are shaped correctly against the live API (only the Python SDK method signatures were exercised, against fakes).

## Known gaps / next steps

- No live end-to-end run yet — needs real credentials to validate actual model output quality and the real Google Sheets/Drive API call shapes.
- No automated test suite committed to the repo (the wiring harness lives in the session scratchpad, not in the skill directory).
- `sheet_tracker.py` has no retry/error handling around the Google API calls (e.g. a stale/invalid `drive_folder_id`, a service account lacking folder access, rate limits) — currently any failure just propagates as a raw `googleapiclient.errors.HttpError`.
- No handling yet for `share_with` emails that fail to resolve to a Google account, or for very large backlogs (many epics -> many serial `generate_user_stories` calls -> latency).
- Voice transcript input (one of the three documented input types) isn't handled any differently from plain text — there's no transcription step; a transcript is assumed to already be text by the time it reaches `analyze()`.

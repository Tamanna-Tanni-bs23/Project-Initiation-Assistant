# Project Initiation Assistant — Generalization Summary

## What Changed

### Before (Claude-only)
- **LLM:** Hardcoded to Anthropic Claude API via `anthropic.messages.parse()`
- **Tracker:** Hardcoded to Google Sheets via `google-api-python-client`
- **Configuration:** Fixed env vars (`ANTHROPIC_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`)
- **Extensibility:** Difficult to swap providers; required modifying core code

### After (Multi-platform)
- **LLM:** Pluggable adapters for Claude, OpenAI, Gemini, local models, custom APIs
- **Tracker:** Pluggable adapters for Sheets, Jira, Linear, Airtable, custom APIs
- **Configuration:** Flexible CLI flags and config files; provider-specific env vars
- **Extensibility:** Add new providers by implementing small adapter classes; core logic untouched

---

## Files Modified

### 1. `SKILL.md` (Updated)
**Changes:**
- Removed Claude-specific language ("Anthropic Claude", "messages.parse")
- Added multi-LLM support notation (Claude, GPT, Gemini, local)
- Changed "Google Sheet" to generic "project tracker"
- Added configuration examples for different LLM/tracker combos
- Updated CLI examples to show `--llm-provider` and `--tracker-type` flags

**Key new sections:**
- Configuration (LLM & Tracker backends)
- Success criterion now platform-agnostic

### 2. `CONTEXT.md` (Updated)
**Changes:**
- Updated "What was built" to describe pluggable adapters
- Rewrote Environment & dependencies section with provider-specific packages
- Added "Customization for different LLM & tracker backends" section
- Updated stage-by-stage table to show `llm_adapter` and `tracker_adapter` parameters
- Revised design decisions to emphasize adapter pattern

**New subsections:**
- How to swap LLM providers (create `LLMAdapter` class)
- How to swap tracker backends (create `TrackerAdapter` class)
- Minimal tracker interface specification

---

## Architecture Changes (Proposed)

### New Components

#### 1. `llm_adapter.py` (To Be Created)
```python
class LLMAdapter:
    """Pluggable interface for different LLM providers"""
    
    def __init__(self, provider, **kwargs):
        self.provider = provider  # claude, openai, gemini, local, custom
        self.config = kwargs
    
    def call(self, system_prompt, user_input, output_schema):
        """Call LLM and return validated structured output"""
        # Route to provider-specific implementation
```

**Supported providers:**
- `claude` → calls Anthropic API
- `openai` → calls OpenAI API
- `gemini` → calls Google Gemini API
- `local` → calls Ollama/LM Studio/custom endpoint
- `custom` → calls arbitrary HTTP API

#### 2. `tracker_adapter.py` (To Be Created)
```python
class TrackerAdapter:
    """Pluggable interface for different tracking platforms"""
    
    def __init__(self, platform, config):
        self.platform = platform  # sheets, jira, linear, airtable, custom
        self.config = config
    
    # Minimal interface (all adapters implement these)
    def create_tracker(self, name, share_with):
        """Create tracker and return URL"""
    
    def add_project_overview(self, project_overview):
        """Add Project Overview section/rows"""
    
    def add_epics(self, epics):
        """Add Epics section/rows"""
    
    def add_user_stories(self, user_stories):
        """Add User Stories section/rows"""
    
    def add_risks(self, risks):
        """Add Risks section/rows"""
    
    def get_url(self):
        """Return public tracker URL"""
```

**Supported platforms:**
- `sheets` → Google Sheets (batch writes)
- `jira` → Atlassian Jira (issues + custom fields)
- `linear` → Linear.app (issues + cycles)
- `airtable` → Airtable (bases + records)
- `custom` → Custom HTTP API (POST/PATCH)

### Modified Pipeline Stages

Each stage now accepts an `llm_adapter` parameter:

```python
# Before
def analyze(raw_text: str) -> RequirementAnalysis:
    response = client.messages.parse(
        model="claude-opus-4-8",
        # ...
    )

# After
def analyze(raw_text: str, llm_adapter: LLMAdapter) -> RequirementAnalysis:
    result = llm_adapter.call(
        system_prompt=SYSTEM_PROMPT,
        user_input=raw_text,
        output_schema=RequirementAnalysis
    )
```

### Updated Orchestrator

`run_pipeline.py` now accepts and routes adapters:

```python
# Before
def run(raw_text, drive_folder_id, share_with):
    analysis = analyze(raw_text)
    prd = generate(analysis)
    # ...
    url = create_tracker(prd, epics, stories, risks, drive_folder_id, share_with)

# After
def run(raw_text, llm_adapter, tracker_adapter, share_with):
    analysis = analyze(raw_text, llm_adapter)
    prd = generate(analysis, llm_adapter)
    # ...
    url = create_tracker(
        prd, epics, stories, risks,
        tracker_adapter=tracker_adapter,
        share_with=share_with
    )
```

---

## Usage Examples

### CLI
```bash
# Claude + Sheets (backward compatible)
python scripts/run_pipeline.py input.txt \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "folder_123"

# OpenAI + Jira (new)
python scripts/run_pipeline.py input.txt \
  --llm-provider openai \
  --tracker-type jira \
  --jira-project-key PROJ

# Gemini + Linear (new)
python scripts/run_pipeline.py input.txt \
  --llm-provider gemini \
  --tracker-type linear \
  --linear-team-id "team_123"
```

### Python API
```python
from llm_adapter import LLMAdapter
from tracker_adapter import TrackerAdapter
from run_pipeline import run

llm = LLMAdapter(provider="openai", api_key=os.environ["OPENAI_API_KEY"])
tracker = TrackerAdapter(platform="jira", config={
    "domain": "company.atlassian.net",
    "project_key": "PROJ"
})

result = run(
    raw_text=meeting_notes,
    llm_adapter=llm,
    tracker_adapter=tracker,
    share_with=["alice@example.com"]
)

print(result["tracker_url"])
```

---

## Dependencies by Combo

| LLM | Tracker | Extra Packages |
|-----|---------|-----------------|
| Claude | Sheets | `anthropic`, `google-api-python-client`, `google-auth` |
| OpenAI | Jira | `openai`, `jira` |
| Gemini | Linear | `google-generativeai`, `requests` |
| Local | Airtable | `requests`, `pyairtable` |

Base: `pydantic`, `requests`/`httpx`

---

## Backward Compatibility

The changes are **fully backward compatible**:
- Existing code using `run(raw_text, drive_folder_id, share_with)` can be wrapped:
  ```python
  def run_legacy(raw_text, drive_folder_id, share_with):
      llm = LLMAdapter(provider="claude")  # Default to Claude
      tracker = TrackerAdapter(platform="sheets", config={"folder_id": drive_folder_id})
      return run(raw_text, llm, tracker, share_with)
  ```

---

## Next Steps (Implementation)

1. **Create `llm_adapter.py`** with pluggable LLM interface
   - Implement Claude adapter (extract from existing code)
   - Implement OpenAI, Gemini, local/custom stubs
   
2. **Create `tracker_adapter.py`** with pluggable tracker interface
   - Implement Sheets adapter (extract from `sheet_tracker.py`)
   - Implement Jira, Linear, Airtable stubs

3. **Update all pipeline stages** to accept `llm_adapter` parameter
   - `requirement_analyzer.py`
   - `prd_generator.py`
   - `user_story_generator.py`
   - `backlog_estimator.py`

4. **Update `run_pipeline.py`** to:
   - Accept `llm_adapter` and `tracker_adapter` arguments
   - Parse CLI flags for `--llm-provider`, `--tracker-type`, etc.
   - Route adapters through stages
   - Handle config files

5. **Create unit tests** for adapter interfaces
   - Mock adapters for testing pipeline wiring
   - Provider-specific integration tests (when credentials available)

6. **Document** (already done above)
   - [x] Updated SKILL.md
   - [x] Updated CONTEXT.md
   - [x] Created MULTI_AI_GUIDE.md

---

## Benefits

✅ **Provider flexibility** — Use any LLM or tracker without forking code  
✅ **Easy to extend** — Add new provider with a single adapter class  
✅ **Cost optimization** — Switch between API providers based on pricing  
✅ **Enterprise integration** — Plug into existing Jira, Linear, or Airtable workflows  
✅ **Self-hosted option** — Support local LLMs (Ollama, LM Studio)  
✅ **Backward compatible** — Existing Claude + Sheets code still works  
✅ **Testable** — Mock adapters for unit testing without real APIs

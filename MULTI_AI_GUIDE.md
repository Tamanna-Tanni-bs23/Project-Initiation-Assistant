# Project Initiation Assistant — Multi-AI Adapter Guide

This skill has been generalized to work with **any LLM backend** and **any project tracker platform**.

## Quick Start Examples

### 1. Claude + Google Sheets (Original)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

python scripts/run_pipeline.py input.txt \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "folder_123" \
  --share-with alice@example.com
```

### 2. OpenAI GPT + Jira
```bash
export OPENAI_API_KEY="sk-proj-..."
export JIRA_API_TOKEN="ATATT3xF..."
export JIRA_DOMAIN="company.atlassian.net"
export JIRA_EMAIL="bot@company.com"

python scripts/run_pipeline.py input.txt \
  --llm-provider openai \
  --tracker-type jira \
  --jira-project-key PROJ \
  --share-with team@example.com
```

### 3. Google Gemini + Linear
```bash
export GOOGLE_API_KEY="AIzaSyD..."
export LINEAR_API_KEY="lin_api_..."

python scripts/run_pipeline.py input.txt \
  --llm-provider gemini \
  --tracker-type linear \
  --linear-team-id "team_123" \
  --share-with team@linear.app
```

### 4. Local LLM (Ollama) + Airtable
```bash
export LOCAL_LLM_ENDPOINT="http://localhost:11434/api/generate"
export LOCAL_LLM_MODEL="llama2"
export AIRTABLE_API_KEY="patXXX..."
export AIRTABLE_BASE_ID="appXXX..."

python scripts/run_pipeline.py input.txt \
  --llm-provider local \
  --llm-model llama2 \
  --tracker-type airtable \
  --share-with team@airtable.com
```

## Architecture

### LLM Adapters (`llm_adapter.py`)

Each stage calls `adapter.call(system_prompt, user_input, output_schema)`:

```python
class LLMAdapter:
    def __init__(self, provider="claude", **kwargs):
        self.provider = provider
        self.config = kwargs
    
    def call(self, system_prompt, user_input, output_schema):
        """
        Call LLM and return validated structured output.
        
        Args:
            system_prompt: System instructions
            user_input: User message
            output_schema: Pydantic model class or dict schema
        
        Returns:
            Validated output (dict or Pydantic model instance)
        """
        if self.provider == "claude":
            return self._call_claude(system_prompt, user_input, output_schema)
        elif self.provider == "openai":
            return self._call_openai(system_prompt, user_input, output_schema)
        # ... etc
```

**Supported providers:**
- `claude` — Anthropic Claude (via `anthropic` SDK)
- `openai` — OpenAI GPT (via `openai` SDK, uses `gpt-4-turbo`)
- `gemini` — Google Gemini (via `google-generativeai`)
- `local` — Local/self-hosted via Ollama, LM Studio, or custom endpoint
- `custom` — Custom HTTP API

### Tracker Adapters (`tracker_adapter.py`)

Each adapter implements:

```python
class TrackerAdapter:
    def __init__(self, platform, config):
        self.platform = platform
        self.config = config
    
    def create_tracker(self, name, share_with):
        """Create tracker container, return URL and internal ID"""
        pass
    
    def add_project_overview(self, project_overview):
        """Add Project Overview row(s)"""
        pass
    
    def add_epics(self, epics):
        """Add Epic rows"""
        pass
    
    def add_user_stories(self, stories):
        """Add User Story rows"""
        pass
    
    def add_risks(self, risks):
        """Add Risk rows"""
        pass
    
    def get_url(self):
        """Return public tracker URL"""
        pass
```

**Supported platforms:**
- `sheets` — Google Sheets (batch writes via Sheets API)
- `jira` — Atlassian Jira (issues + custom fields)
- `linear` — Linear.app (issues + cycles)
- `airtable` — Airtable (bases + records)
- `custom` — Custom HTTP API (POST/PATCH)

## Adding a New LLM Provider

1. **Create a new method in `llm_adapter.py`:**
   ```python
   def _call_mistral(self, system_prompt, user_input, output_schema):
       from mistralai.client import MistralClient
       client = MistralClient(api_key=self.config.get("api_key"))
       
       # Call Mistral API
       response = client.chat(
           model="mistral-large",
           messages=[
               {"role": "system", "content": system_prompt},
               {"role": "user", "content": user_input}
           ]
       )
       
       # Parse and validate against output_schema (Pydantic)
       result = json.loads(response.choices[0].message.content)
       return output_schema(**result)
   ```

2. **Register in `__init__`:**
   ```python
   def call(self, system_prompt, user_input, output_schema):
       # ... existing code ...
       elif self.provider == "mistral":
           return self._call_mistral(system_prompt, user_input, output_schema)
   ```

3. **Set env var and run:**
   ```bash
   export MISTRAL_API_KEY="..." 
   python scripts/run_pipeline.py input.txt --llm-provider mistral --tracker-type sheets
   ```

## Adding a New Tracker Platform

1. **Create adapter in `tracker_adapter.py`:**
   ```python
   def _create_tracker_monday(self, name, config, share_with):
       from monday import MondayClient
       client = MondayClient(token=config.get("api_token"))
       
       board = client.create_board(name=name)
       # Create columns for project_overview, epics, stories, risks
       # Return board URL and ID for later writes
       return board.url, board.id
   ```

2. **Implement row-add methods:**
   ```python
   def add_user_stories(self, stories):
       for story in stories:
           self.client.create_item(
               board_id=self.tracker_id,
               group_id="stories",
               item_name=story.story,
               column_values={"points": story.story_points, ...}
           )
   ```

3. **Register and run:**
   ```bash
   export MONDAY_API_TOKEN="..."
   python scripts/run_pipeline.py input.txt --tracker-type monday
   ```

## Configuration File (Optional)

Create `config.yaml`:
```yaml
llm:
  provider: openai
  model: gpt-4-turbo
  temperature: 0.7
  max_tokens: 4000

tracker:
  platform: jira
  domain: company.atlassian.net
  project_key: PROJ
  issue_type: Story

sharing:
  - alice@example.com
  - bob@example.com
```

Run with:
```bash
python scripts/run_pipeline.py input.txt --config config.yaml
```

## Dependencies for Different Setups

### Claude + Sheets (original)
```bash
pip install anthropic pydantic google-api-python-client google-auth
```

### OpenAI + Jira
```bash
pip install openai pydantic jira
```

### Gemini + Linear
```bash
pip install google-generativeai pydantic requests
```

### Local (Ollama) + Airtable
```bash
pip install pydantic requests pyairtable
```

## Error Handling by Provider

Each adapter should handle provider-specific errors:

```python
def _call_openai(self, system_prompt, user_input, output_schema):
    try:
        # OpenAI call
    except openai.RateLimitError:
        print(f"Rate limited; retrying in {backoff}s...")
        # Retry with exponential backoff
    except openai.APIError as e:
        print(f"OpenAI API error: {e}")
        raise
```

## Testing

Run without credentials to test pipeline wiring:
```bash
python scripts/test_pipeline_wiring.py
```

This uses mocked adapters to verify data flows correctly through all stages without hitting real APIs.

## Migration Path

If you're currently using Claude + Sheets and want to switch:

1. **Keep your LLM, change tracker:**
   ```bash
   # Old: Claude → Sheets
   # New: Claude → Jira
   python scripts/run_pipeline.py input.txt --llm-provider claude --tracker-type jira
   ```

2. **Keep your tracker, change LLM:**
   ```bash
   # Old: Claude → Sheets
   # New: OpenAI → Sheets
   python scripts/run_pipeline.py input.txt --llm-provider openai --tracker-type sheets
   ```

3. **Switch both:**
   ```bash
   # Old: Claude → Sheets
   # New: Gemini → Linear
   python scripts/run_pipeline.py input.txt --llm-provider gemini --tracker-type linear
   ```

The pipeline logic remains unchanged; only the adapters swap.

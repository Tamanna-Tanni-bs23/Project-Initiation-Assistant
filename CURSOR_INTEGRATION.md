# Project Initiation Assistant — Cursor Integration Guide

How to use the Project Initiation Assistant skill from within Cursor editor.

## Quick Start: Use in Cursor Composer

### 1. Create a Cursor Agent File

Create `.cursor/agents/project-initiation.md` in your workspace:

```markdown
---
name: Project Initiation Assistant
description: Convert meeting notes/requirements into PRD, epics, user stories, and project tracker
---

# Project Initiation Assistant Agent

You are an AI agent that automates the requirement-to-development handoff pipeline.

## Inputs
- Raw meeting notes
- Client requirement documents
- Voice transcripts

## Process
When the user provides requirements, follow this pipeline:

1. **Analyze Requirements** → Extract goals, stakeholders, functional requirements, constraints
2. **Generate PRD** → Create structured Product Requirements Document
3. **Create Epics** → Break down into high-level features
4. **Write User Stories** → Create "As a / I want / So that" stories with acceptance criteria
5. **Estimate & Identify Risks** → Assign story points, priority, and surface risks
6. **Create Project Tracker** → Populate Google Sheet/Jira/Linear with all data

## Configuration

Set these env vars in `.cursor/env`:
- `LLM_PROVIDER=claude` (or openai, gemini, local)
- `TRACKER_TYPE=sheets` (or jira, linear, airtable)
- `ANTHROPIC_API_KEY=sk-ant-...` (if using Claude)
- `GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json` (if using Sheets)

## Python Command

The underlying pipeline is in `scripts/run_pipeline.py`. You can execute it via:

```bash
python scripts/run_pipeline.py <input_file> \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "folder_id" \
  --share-with alice@example.com
```

## Example Usage

User: "Here are meeting notes from our client kickoff. Create a PRD and backlog."
Assistant: 
1. Read the meeting notes
2. Run `python scripts/run_pipeline.py` with the notes
3. Return the generated PRD, epics, stories, and tracker URL
```

### 2. Use the Agent in Composer

In Cursor:
1. Open **Composer** (Cmd+Shift+L on Mac, Ctrl+Shift+L on Windows)
2. Type: `@project-initiation` (or use the agent dropdown)
3. Paste your meeting notes
4. Agent runs the full pipeline and returns:
   - Analyzed requirements
   - Generated PRD
   - Epic list
   - User stories with acceptance criteria
   - Risk assessment
   - Project tracker URL (Sheets/Jira/Linear/etc.)

---

## Integration Method 1: Python Script Execution

### Setup

1. **Create a custom Cursor command** in `.cursor/commands.json`:

```json
{
  "commands": [
    {
      "name": "Generate Project Backlog",
      "description": "Convert requirements to PRD, epics, stories, and tracker",
      "command": "python",
      "args": ["${workspaceFolder}/scripts/run_pipeline.py"],
      "input": "file",
      "output": "terminal"
    }
  ]
}
```

2. **In Cursor**, press Cmd+K (Quick Command) and type:
   - `Generate Project Backlog`
   - Select your requirements file
   - Script runs and outputs results

### Example: Requirements File → Backlog

**Input file: `requirements.txt`**
```
Meeting Date: 2026-07-22
Attendees: Client PM, Tech Lead, Designer

Key Requirements:
- Build a dashboard for real-time sales analytics
- Support multiple data sources (Salesforce, HubSpot, custom APIs)
- Integrate with Slack for alerts
- Target: Launch MVP in 8 weeks

Constraints:
- Must be mobile-responsive
- GDPR compliant
```

**Run in Cursor**:
```bash
python scripts/run_pipeline.py requirements.txt \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "folder_id" \
  --share-with team@company.com
```

**Output**:
```
✅ Analysis complete
  - 5 goals identified
  - 3 stakeholder groups
  - 12 functional requirements
  - 4 constraints

✅ PRD generated (2500 words)
  - Project: Sales Analytics Dashboard
  - Client: Internal Product Team
  - Objective: Real-time sales visibility

✅ Epics created (4)
  - Epic 1: Data Integration (HubSpot, Salesforce, APIs)
  - Epic 2: Dashboard UI & Visualization
  - Epic 3: Slack Integration & Alerts
  - Epic 4: Mobile Responsiveness & Accessibility

✅ User Stories created (24)
  - 6 stories per epic
  - Acceptance criteria included
  - Estimated effort assigned

✅ Risks identified (5)
  - Risk: Data sync latency
  - Risk: GDPR compliance edge cases
  - Risk: Mobile performance

✅ Project Tracker created
  - URL: https://docs.google.com/spreadsheets/d/1aBc...
  - 4 worksheets: Overview, Epics, Stories, Risks
  - Shared with team@company.com
```

---

## Integration Method 2: Web API Wrapper

Make the skill accessible from **any AI tool** (Claude web, ChatGPT, etc.) via HTTP.

### Create a Flask API Wrapper

**File: `scripts/api_server.py`**

```python
from flask import Flask, request, jsonify
from run_pipeline import run
from llm_adapter import create_llm_adapter
from tracker_adapter import create_tracker_adapter
import os

app = Flask(__name__)

@app.route("/api/v1/generate-backlog", methods=["POST"])
def generate_backlog():
    """
    POST /api/v1/generate-backlog
    
    Request body:
    {
        "raw_text": "Meeting notes...",
        "llm_provider": "claude",
        "tracker_type": "sheets",
        "drive_folder_id": "folder_123",
        "share_with": ["alice@example.com"]
    }
    
    Returns:
    {
        "success": true,
        "analysis": {...},
        "prd": "PRD text...",
        "epics": [...],
        "user_stories": [...],
        "risks": [...],
        "tracker_url": "https://..."
    }
    """
    try:
        data = request.json
        
        # Create adapters
        llm = create_llm_adapter(
            provider=data.get("llm_provider", "claude")
        )
        tracker = create_tracker_adapter(
            platform=data.get("tracker_type", "sheets"),
            folder_id=data.get("drive_folder_id")
        )
        
        # Run pipeline
        result = run(
            raw_text=data.get("raw_text"),
            llm_adapter=llm,
            tracker_adapter=tracker,
            share_with=data.get("share_with", [])
        )
        
        return jsonify({
            "success": True,
            "analysis": result["analysis"],
            "prd": result["prd"],
            "epics": result["epics"],
            "user_stories": result["user_stories"],
            "risks": result["risks"],
            "tracker_url": result["tracker_url"]
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "project-initiation-assistant"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

### Run the API Server

```bash
pip install flask
python scripts/api_server.py
# Server running at http://localhost:5000
```

### Use from Cursor

**Create `.cursor/agents/api-backlog-generator.md`:**

```markdown
---
name: Project Backlog Generator (API)
description: Call the local API to generate backlog
---

# Project Backlog Generator

When user provides requirements, make an HTTP POST request to the local API:

```python
import requests

def generate_backlog(requirements_text):
    response = requests.post(
        "http://localhost:5000/api/v1/generate-backlog",
        json={
            "raw_text": requirements_text,
            "llm_provider": "claude",
            "tracker_type": "sheets",
            "drive_folder_id": os.environ.get("DRIVE_FOLDER_ID"),
            "share_with": ["team@company.com"]
        }
    )
    
    result = response.json()
    if result["success"]:
        return {
            "prd": result["prd"],
            "epics": result["epics"],
            "stories": result["user_stories"],
            "risks": result["risks"],
            "tracker_url": result["tracker_url"]
        }
    else:
        raise Exception(result["error"])
```
```

---

## Integration Method 3: Cursor with MCP (Model Context Protocol)

Use Cursor's MCP support to expose the skill as a tool.

### Create MCP Server

**File: `.cursor/mcp_servers/project_initiation.py`**

```python
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult
import asyncio
from run_pipeline import run
from llm_adapter import create_llm_adapter
from tracker_adapter import create_tracker_adapter

server = Server("project-initiation-assistant")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate_project_backlog",
            description="Convert requirements/meeting notes into PRD, epics, stories, and tracker",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Raw meeting notes, requirements doc, or transcript"
                    },
                    "llm_provider": {
                        "type": "string",
                        "enum": ["claude", "openai", "gemini", "local"],
                        "description": "Which LLM to use"
                    },
                    "tracker_type": {
                        "type": "string",
                        "enum": ["sheets", "jira", "linear", "airtable"],
                        "description": "Where to create the tracker"
                    },
                    "drive_folder_id": {
                        "type": "string",
                        "description": "Google Drive folder ID (if using Sheets)"
                    },
                    "share_with": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Email addresses to share tracker with"
                    }
                },
                "required": ["requirements"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> ToolResult:
    if name != "generate_project_backlog":
        return ToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")]
        )
    
    try:
        # Parse arguments
        raw_text = arguments.get("requirements")
        llm_provider = arguments.get("llm_provider", "claude")
        tracker_type = arguments.get("tracker_type", "sheets")
        drive_folder_id = arguments.get("drive_folder_id")
        share_with = arguments.get("share_with", [])
        
        # Create adapters
        llm = create_llm_adapter(provider=llm_provider)
        tracker = create_tracker_adapter(
            platform=tracker_type,
            folder_id=drive_folder_id
        )
        
        # Run pipeline
        result = run(
            raw_text=raw_text,
            llm_adapter=llm,
            tracker_adapter=tracker,
            share_with=share_with
        )
        
        # Format output
        output = f"""
## Project Backlog Generated ✅

### PRD
{result['prd']}

### Epics ({len(result['epics'])} total)
"""
        for epic in result["epics"]:
            output += f"\n- **{epic['name']}**: {epic['description']}"
        
        output += f"\n\n### User Stories ({len(result['user_stories'])} total)\n"
        for story in result["user_stories"][:5]:  # Show first 5
            output += f"\n- {story['story']} ({story['story_points']} pts)"
        
        output += f"\n\n### Risks ({len(result['risks'])} identified)\n"
        for risk in result["risks"]:
            output += f"\n- **{risk['risk']}** (Impact: {risk['impact']})"
        
        output += f"\n\n### Project Tracker\n📊 {result['tracker_url']}"
        
        return ToolResult(
            content=[TextContent(type="text", text=output)]
        )
    
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

if __name__ == "__main__":
    server.run()
```

### Register in `.cursor/settings.json`

```json
{
  "mcp_servers": {
    "project-initiation": {
      "command": "python",
      "args": [".cursor/mcp_servers/project_initiation.py"]
    }
  }
}
```

---

## Integration Method 4: Cursor Commands with Keyboard Shortcut

### Configure Keyboard Shortcut

**File: `.cursor/keybindings.json`**

```json
[
  {
    "key": "cmd+shift+p",  // or ctrl+shift+p on Windows
    "command": "extension.projectInitiation"
  }
]
```

### Create Command Handler

**File: `.cursor/extensions/project_initiation.js`**

```javascript
const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');

function activate(context) {
  let disposable = vscode.commands.registerCommand(
    'extension.projectInitiation',
    async () => {
      // Get active editor
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showErrorMessage('No file open');
        return;
      }

      // Get file path
      const filePath = editor.document.fileName;
      const workspaceFolder = vscode.workspace.workspaceFolders[0].uri.fsPath;

      // Show input dialog
      const llmProvider = await vscode.window.showQuickPick(
        ['claude', 'openai', 'gemini', 'local'],
        { placeHolder: 'Select LLM provider' }
      );

      const trackerType = await vscode.window.showQuickPick(
        ['sheets', 'jira', 'linear', 'airtable'],
        { placeHolder: 'Select tracker platform' }
      );

      const folderIdOrProjectKey = await vscode.window.showInputBox({
        placeHolder: 'Enter folder ID, project key, or team ID'
      });

      // Build command
      const pythonScript = path.join(
        workspaceFolder,
        'scripts/run_pipeline.py'
      );
      const cmd = `python "${pythonScript}" "${filePath}" --llm-provider ${llmProvider} --tracker-type ${trackerType}`;

      // Show output panel
      const terminal = vscode.window.createTerminal('Project Initiation');
      terminal.sendText(cmd);
      terminal.show();
    }
  );

  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = { activate, deactivate };
```

---

## Integration Method 5: Use with Claude Web / ChatGPT

### Export Results as Shared Document

The API wrapper or MCP server can be deployed to generate a public URL.

**Option A: Use ngrok for local tunneling**

```bash
# Terminal 1: Run API server
python scripts/api_server.py

# Terminal 2: Tunnel to internet
ngrok http 5000
# Exposes: https://abcd-1234.ngrok.io
```

**Option B: Deploy to Cloud**

Deploy `api_server.py` to:
- **Vercel** (serverless Python)
- **Heroku** (traditional app hosting)
- **AWS Lambda + API Gateway**
- **Google Cloud Run**
- **Railway**, **Render**, etc.

### Share with Claude Web

1. Provide the API endpoint to Claude:
   ```
   I've deployed the Project Initiation Assistant to:
   https://project-init.example.com/api/v1/generate-backlog
   
   Requirements:
   - POST endpoint
   - JSON body: { raw_text, llm_provider, tracker_type, drive_folder_id, share_with }
   - Returns: { success, prd, epics, user_stories, risks, tracker_url }
   
   Here are my meeting notes: [paste notes]
   ```

2. Claude makes the API call and returns structured results

---

## Integration Summary Table

| Method | Setup Time | Ease | Use Case |
|--------|-----------|------|----------|
| **Cursor Agent** | 5 min | ⭐⭐⭐⭐⭐ | Quick iteration; full AI context |
| **Python Script** | 10 min | ⭐⭐⭐⭐ | Local workflow; terminal-based |
| **Web API** | 20 min | ⭐⭐⭐⭐ | Multi-tool access; remote teams |
| **MCP Server** | 15 min | ⭐⭐⭐⭐ | Native Cursor integration |
| **Cloud Deploy** | 30 min | ⭐⭐⭐ | Team-wide access; CI/CD |
| **Custom Command** | 10 min | ⭐⭐⭐⭐⭐ | Keyboard shortcut workflow |

---

## Full Example: Cursor + Claude + Sheets

### Setup (One-time)

```bash
# 1. Install dependencies
cd "claude skill assignment"
pip install -r scripts/requirements.txt

# 2. Set up credentials
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# 3. Optional: Deploy API server
python scripts/api_server.py  # Runs on http://localhost:5000
```

### Workflow in Cursor

```
1. Open meeting notes file in Cursor
   File: meeting_kickoff_2026_07_22.txt

2. Press Cmd+Shift+L (open Composer)

3. Type: @project-initiation
   "Convert this to a PRD and backlog"

4. Copy meeting notes into Composer

5. Agent runs pipeline:
   ✅ Analyzes requirements
   ✅ Generates PRD
   ✅ Creates 4 epics
   ✅ Writes 24 user stories
   ✅ Identifies 5 risks
   ✅ Creates Google Sheet

6. Results in Composer window:
   - Full PRD displayed
   - Epics list
   - Sample stories (with acceptance criteria)
   - Risks & mitigations
   - 🔗 Tracker URL: https://docs.google.com/spreadsheets/d/...

7. Share URL with team
```

---

## Troubleshooting

### API Key Not Found
```bash
# Make sure env vars are set
echo $ANTHROPIC_API_KEY
echo $GOOGLE_APPLICATION_CREDENTIALS

# Or set in .cursor/env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

### Python Script Not Found
```bash
# Make sure you're in the right directory
cd "claude skill assignment"
python scripts/run_pipeline.py --help
```

### Tracker Creation Fails
```bash
# Test credentials
python -c "from google.oauth2.service_account import Credentials; Credentials.from_service_account_file('/path/to/key.json')"

# Or for Jira
curl -X GET "https://company.atlassian.net/rest/api/3/myself" \
  -H "Authorization: Bearer $JIRA_API_TOKEN"
```

### Rate Limits
Add exponential backoff to adapters:
```python
import time

def call_with_retry(self, system_prompt, user_input, output_schema, max_retries=3):
    for attempt in range(max_retries):
        try:
            return self.call(system_prompt, user_input, output_schema)
        except RateLimitError:
            wait_time = 2 ** attempt
            print(f"Rate limited; waiting {wait_time}s...")
            time.sleep(wait_time)
```

---

## Next Steps

- [ ] Copy `.cursor/agents/project-initiation.md` to your workspace
- [ ] Set `ANTHROPIC_API_KEY` and `GOOGLE_APPLICATION_CREDENTIALS`
- [ ] Open Composer in Cursor and try `@project-initiation`
- [ ] For APIs: Run `python scripts/api_server.py`
- [ ] For cloud: Deploy to Vercel/Railway/Heroku

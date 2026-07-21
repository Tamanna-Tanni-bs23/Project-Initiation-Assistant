# Project Initiation Assistant — AI Tools Integration Guide

Complete guide to integrate the skill with **all major AI platforms and tools**.

---

## Integration Methods Overview

| AI Tool | Integration Method | Ease | Setup Time |
|---------|-------------------|------|-----------|
| **Claude (claude.ai)** | Claude Skills API | ⭐⭐⭐⭐⭐ | 10 min |
| **ChatGPT** | OpenAI Custom GPT + API | ⭐⭐⭐⭐ | 15 min |
| **Google Gemini** | Google AI Studio + API | ⭐⭐⭐⭐ | 15 min |
| **Copilot (Microsoft)** | OpenAI API Backend | ⭐⭐⭐ | 20 min |
| **Slack** | Slack Bot + API | ⭐⭐⭐⭐ | 20 min |
| **Discord** | Discord Bot + API | ⭐⭐⭐⭐ | 20 min |
| **VSCode** | VS Code Extension | ⭐⭐⭐ | 25 min |
| **Cursor** | MCP + Custom Commands | ⭐⭐⭐⭐ | 15 min |
| **JetBrains IDEs** | Plugin | ⭐⭐ | 30 min |
| **Zapier/Make** | Webhook Integration | ⭐⭐⭐⭐ | 15 min |

---

## 1. Claude Web (claude.ai/code)

### Method A: Use as Claude Skill (Recommended)

Already set up! The skill is at `.claude/skills/project-initiation-assistant/`

**Usage:**
```
1. Go to claude.ai/code
2. Add the project folder
3. Type: /project-initiation-assistant
4. Paste your meeting notes
```

### Method B: Direct API Call

```python
# Use the skill directly via Anthropic SDK
from anthropic import Anthropic

client = Anthropic()

# Load the skill definition
with open(".claude/skills/project-initiation-assistant/SKILL.md") as f:
    skill_definition = f.read()

# Use in conversation
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    system=f"{skill_definition}\n\nYou are the Project Initiation Assistant. Process the requirements and generate backlog.",
    messages=[
        {"role": "user", "content": meeting_notes}
    ]
)

print(response.content[0].text)
```

---

## 2. ChatGPT / OpenAI

### Method A: Custom GPT with Actions

1. **Create Custom GPT at chat.openai.com/gpts/editor**
   - Name: "Project Initiation Assistant"
   - Description: "Convert meeting notes into PRD, epics, user stories, and project tracker"

2. **Add Instructions:**
```
You are an expert Project Manager and Requirements Analyst. When users provide meeting notes, requirements, or transcripts, follow this pipeline:

1. Analyze Requirements
2. Generate PRD (Product Requirements Document)
3. Create Epics
4. Write User Stories (As a / I want / So that)
5. Estimate effort and identify risks
6. Create project tracker

Always ask clarifying questions before starting.
Return structured output: PRD, Epics List, User Stories with acceptance criteria, Risks, and Tracker URL.
```

3. **Configure Actions (Schema)**

Create a JSON schema for the API:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Project Initiation API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://project-initiation-api.example.com"
    }
  ],
  "paths": {
    "/api/v1/generate-backlog": {
      "post": {
        "summary": "Generate project backlog from requirements",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "raw_text": {
                    "type": "string",
                    "description": "Meeting notes or requirements"
                  },
                  "llm_provider": {
                    "type": "string",
                    "enum": ["openai", "claude", "gemini"],
                    "default": "openai"
                  },
                  "tracker_type": {
                    "type": "string",
                    "enum": ["sheets", "jira", "linear"],
                    "default": "sheets"
                  }
                },
                "required": ["raw_text"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Backlog generated successfully",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "prd": {"type": "string"},
                    "epics": {"type": "array"},
                    "user_stories": {"type": "array"},
                    "risks": {"type": "array"},
                    "tracker_url": {"type": "string"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

4. **Deploy API** (see Web API section below)

5. **Add to GPT**
   - Go to Custom GPT Editor
   - Click "Create new action"
   - Paste the OpenAPI schema above
   - Enter your API endpoint (e.g., `https://project-initiation-api.example.com`)
   - Set authentication (API key or OAuth)

### Method B: Use OpenAI GPT as LLM Backend

Update `llm_adapter.py` to use OpenAI (already included in examples):

```python
from llm_adapter import create_llm_adapter

llm = create_llm_adapter("openai", model="gpt-4-turbo")

# Use with the skill
from run_pipeline import run
result = run(meeting_notes, llm_adapter=llm, ...)
```

---

## 3. Google Gemini

### Method A: Google AI Studio

1. **Create Project** at aistudio.google.com

2. **Create Prompt**
```
You are the Project Initiation Assistant. Convert meeting notes into:
1. Analyzed requirements
2. Product Requirements Document (PRD)
3. Epic breakdown
4. User stories with acceptance criteria
5. Risk assessment
6. Project tracker URL

Format output as markdown with clear sections.
```

3. **Add to Google AI Studio**
   - Paste meeting notes
   - Generate backlog

### Method B: Use as LLM Backend

```python
from llm_adapter import create_llm_adapter

llm = create_llm_adapter("gemini", model="gemini-2.0-flash")
result = run(meeting_notes, llm_adapter=llm, ...)
```

### Method C: Deploy as Google Cloud Function

```python
# File: main.py
import functions_framework
from flask import jsonify
from run_pipeline import run
from llm_adapter import create_llm_adapter
from tracker_adapter import create_tracker_adapter

@functions_framework.http
def generate_backlog(request):
    request_json = request.get_json()
    
    try:
        llm = create_llm_adapter("gemini")
        tracker = create_tracker_adapter("sheets", ...)
        
        result = run(
            raw_text=request_json["raw_text"],
            llm_adapter=llm,
            tracker_adapter=tracker,
            share_with=request_json.get("share_with", [])
        )
        
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

Deploy to Google Cloud:
```bash
gcloud functions deploy generate-backlog \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated
```

---

## 4. Slack

### Setup Slack Bot

1. **Create Slack App** at api.slack.com/apps

2. **Enable Features**
   - Slash Commands
   - Message Actions
   - Event Subscriptions

3. **Add Bot Code** (`slack_bot.py`)

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from run_pipeline import run
from llm_adapter import create_llm_adapter
from tracker_adapter import create_tracker_adapter

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/generate-backlog")
def handle_backlog_command(ack, body, client):
    ack()
    
    channel_id = body["channel_id"]
    user_id = body["user_id"]
    text = body["text"]
    
    # Show processing message
    client.chat_postMessage(
        channel=channel_id,
        text="🔄 Processing requirements... This may take a minute."
    )
    
    try:
        # Run pipeline
        llm = create_llm_adapter("claude")
        tracker = create_tracker_adapter("sheets", folder_id=os.environ.get("DRIVE_FOLDER_ID"))
        
        result = run(
            raw_text=text,
            llm_adapter=llm,
            tracker_adapter=tracker,
            share_with=[user_id]  # Share with user
        )
        
        # Send results
        client.chat_postMessage(
            channel=channel_id,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *Backlog Generated*\n\n" +
                               f"📊 *Epics:* {len(result['epics'])}\n" +
                               f"📝 *User Stories:* {len(result['user_stories'])}\n" +
                               f"⚠️ *Risks:* {len(result['risks'])}\n\n" +
                               f"<{result['tracker_url']}|View Project Tracker>"
                    }
                }
            ]
        )
    
    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Error: {str(e)}"
        )

@app.action("share_tracker")
def handle_share_tracker(ack, body, client):
    ack()
    channel_id = body["channel"]["id"]
    tracker_url = body["actions"][0]["value"]
    
    client.chat_postMessage(
        channel=channel_id,
        text=f"📊 Project Tracker: {tracker_url}"
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
```

4. **Run Bot**
```bash
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
export ANTHROPIC_API_KEY="sk-ant-..."
python slack_bot.py
```

5. **Use in Slack**
```
/generate-backlog Meeting notes from client kickoff...

[Bot processes and returns tracker URL]
```

---

## 5. Discord

### Setup Discord Bot

1. **Create Bot** at discord.com/developers/applications

2. **Bot Code** (`discord_bot.py`)

```python
import discord
from discord.ext import commands
from run_pipeline import run
from llm_adapter import create_llm_adapter
from tracker_adapter import create_tracker_adapter
import os

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.command(name="backlog")
async def generate_backlog(ctx, *, requirements):
    """Generate project backlog from requirements"""
    
    # Show processing
    await ctx.send("🔄 Generating backlog... (this may take a minute)")
    
    try:
        # Run pipeline
        llm = create_llm_adapter("claude")
        tracker = create_tracker_adapter("sheets", folder_id=os.environ.get("DRIVE_FOLDER_ID"))
        
        result = run(
            raw_text=requirements,
            llm_adapter=llm,
            tracker_adapter=tracker,
            share_with=[ctx.author.name]
        )
        
        # Format response
        response = f"""
✅ **Backlog Generated**

📊 **Epics:** {len(result['epics'])}
📝 **User Stories:** {len(result['user_stories'])}
⚠️ **Risks:** {len(result['risks'])}

📈 **Tracker URL:** {result['tracker_url']}

**First 3 Epics:**
"""
        for i, epic in enumerate(result['epics'][:3], 1):
            response += f"\n{i}. **{epic['name']}** - {epic['description'][:50]}..."
        
        # Send embed
        embed = discord.Embed(
            title="Project Backlog Generated",
            description=response,
            color=discord.Color.green(),
            url=result['tracker_url']
        )
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

bot.run(os.environ["DISCORD_BOT_TOKEN"])
```

3. **Run Bot**
```bash
export DISCORD_BOT_TOKEN="MzA3..."
export ANTHROPIC_API_KEY="sk-ant-..."
python discord_bot.py
```

4. **Use in Discord**
```
/backlog Meeting notes from project kickoff...

[Bot generates and returns backlog with tracker link]
```

---

## 6. VSCode Extension

### Extension Structure

```
project-initiation-extension/
├── package.json
├── src/
│   ├── extension.ts
│   └── commands.ts
└── dist/
```

### `package.json`

```json
{
  "name": "project-initiation-assistant",
  "displayName": "Project Initiation Assistant",
  "description": "Generate PRD, epics, stories, and tracker from requirements",
  "version": "1.0.0",
  "publisher": "your-name",
  "engines": {
    "vscode": "^1.75.0"
  },
  "activationEvents": ["onCommand:projectInitiation.generate"],
  "main": "./dist/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "projectInitiation.generate",
        "title": "Generate Project Backlog",
        "category": "Project Initiation"
      }
    ],
    "keybindings": [
      {
        "command": "projectInitiation.generate",
        "key": "ctrl+shift+p",
        "mac": "cmd+shift+p"
      }
    ]
  }
}
```

### `src/extension.ts`

```typescript
import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand(
        'projectInitiation.generate',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No file open');
                return;
            }

            const text = editor.document.getText();
            
            // Show options
            const llmProvider = await vscode.window.showQuickPick(
                ['claude', 'openai', 'gemini', 'local'],
                { placeHolder: 'Select LLM' }
            );
            
            const trackerType = await vscode.window.showQuickPick(
                ['sheets', 'jira', 'linear', 'airtable'],
                { placeHolder: 'Select tracker' }
            );

            try {
                // Call API
                const response = await axios.post(
                    'http://localhost:5000/api/v1/generate-backlog',
                    {
                        raw_text: text,
                        llm_provider: llmProvider,
                        tracker_type: trackerType
                    }
                );

                // Display results
                const panel = vscode.window.createWebviewPanel(
                    'projectBacklog',
                    'Project Backlog',
                    vscode.ViewColumn.Two,
                    {}
                );

                panel.webview.html = `
                    <html>
                    <body>
                        <h1>Project Backlog Generated</h1>
                        <h2>PRD</h2>
                        <pre>${response.data.prd}</pre>
                        <h2>Epics (${response.data.epics.length})</h2>
                        <ul>
                            ${response.data.epics.map(e => `<li>${e.name}: ${e.description}</li>`).join('')}
                        </ul>
                        <h2>Tracker</h2>
                        <p><a href="${response.data.tracker_url}">${response.data.tracker_url}</a></p>
                    </body>
                    </html>
                `;
            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${error}`);
            }
        }
    );

    context.subscriptions.push(disposable);
}

export function deactivate() {}
```

### Install Extension
```bash
cd project-initiation-extension
npm install
npm run compile
code --install-extension dist/
```

---

## 7. Zapier / Make.com

### Zapier Integration

1. **Create Zap** at zapier.com

2. **Trigger** (When to run)
   - Example: New email with attachment
   - Extract email body/attachment

3. **Action** (What to do)
   - POST to your API endpoint
   - Body: Meeting notes text
   - Receive: Tracker URL

4. **Zap Template**

```yaml
Trigger:
  App: Gmail
  Event: New Email with Attachment
  Filters:
    From: client@company.com
    Subject contains: "meeting notes"

Action 1:
  App: Webhook
  Method: POST
  URL: https://project-initiation-api.example.com/api/v1/generate-backlog
  Body:
    raw_text: {email_body}
    llm_provider: claude
    tracker_type: sheets

Action 2:
  App: Gmail
  Event: Send Email
  To: {original_from}
  Subject: "✅ Project Backlog Generated"
  Body: "Tracker: {webhook_response.tracker_url}"
```

### Make.com Integration

Similar setup with Make scenarios:
- Trigger: Google Forms submission, Slack message, etc.
- Action: Call API, store results
- Filter/Condition: Check for required fields

---

## 8. Web API Deployment

### Deploy with Docker

**Dockerfile:**
```dockerfile
FROM python:3.11

WORKDIR /app

COPY scripts/requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/ /app/scripts/
COPY references/ /app/references/

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["python", "scripts/api_server.py"]
```

### Deploy to Cloud Platforms

#### Vercel (Serverless)
```bash
vercel deploy
# Auto-detects Python, deploys api_server.py
```

#### Heroku
```bash
heroku create project-initiation-api
heroku config:set ANTHROPIC_API_KEY="sk-ant-..."
git push heroku main
```

#### Railway
```bash
railway up
# Detects Python, deploys automatically
```

#### AWS Lambda + API Gateway
```bash
# Package code
zip lambda_function.zip scripts/ references/

# Create Lambda function
aws lambda create-function \
  --function-name project-initiation \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler scripts/api_server.lambda_handler \
  --zip-file fileb://lambda_function.zip

# Create API Gateway
aws apigateway create-rest-api \
  --name project-initiation-api
```

#### Google Cloud Run
```bash
gcloud run deploy project-initiation \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 9. Make Your Own Integration

### Minimal Example: Custom CLI Tool

```python
#!/usr/bin/env python3
"""project-init: CLI tool for generating project backlogs"""

import argparse
import sys
from run_pipeline import run
from llm_adapter import create_llm_adapter
from tracker_adapter import create_tracker_adapter

def main():
    parser = argparse.ArgumentParser(
        description="Generate project backlog from requirements"
    )
    parser.add_argument("input_file", help="Requirements file")
    parser.add_argument("--llm", default="claude", 
                       choices=["claude", "openai", "gemini", "local"])
    parser.add_argument("--tracker", default="sheets",
                       choices=["sheets", "jira", "linear", "airtable"])
    parser.add_argument("--folder-id", help="Folder/project ID")
    parser.add_argument("--share-with", nargs="+", default=[],
                       help="Email addresses to share with")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Read input
    with open(args.input_file) as f:
        raw_text = f.read()
    
    # Create adapters
    llm = create_llm_adapter(args.llm)
    tracker = create_tracker_adapter(args.tracker, folder_id=args.folder_id)
    
    # Run pipeline
    result = run(raw_text, llm_adapter=llm, tracker_adapter=tracker,
                share_with=args.share_with)
    
    # Output results
    if args.output:
        import json
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"✅ Results saved to {args.output}")
    else:
        print(f"✅ Backlog generated")
        print(f"📊 Tracker: {result['tracker_url']}")
        print(f"📋 {len(result['epics'])} epics, {len(result['user_stories'])} stories")

if __name__ == "__main__":
    main()
```

Install as CLI:
```bash
pip install -e .
project-init meeting_notes.txt --llm claude --tracker sheets --folder-id folder_123
```

---

## Comparison & Recommendations

### For Teams (Real-Time Collaboration)
- **Slack** — Quick access, inline results
- **Discord** — Gaming teams, tech-savvy groups

### For Developers
- **VSCode Extension** — Integrated workflow
- **Cursor** — AI-native, fast iteration
- **CLI Tool** — Script-friendly, CI/CD compatible

### For Product/Project Managers
- **Claude Web** — Full context, detailed analysis
- **ChatGPT** — Familiar interface, widely accessible
- **Google Sheets** — Results already in Sheets

### For Automation
- **Zapier/Make** — No-code integration
- **Web API** — Custom workflows
- **Webhooks** — Event-driven

### For Organizations
- **Slack Bot** + **Sheets** — Central hub
- **Jira Integration** — Existing workflows
- **Cloud Deployment** — Scalable, secure

---

## Security Considerations

### API Keys
```bash
# ❌ Don't hardcode
api_key = "sk-ant-xxx"

# ✅ Use environment variables
import os
api_key = os.environ.get("ANTHROPIC_API_KEY")

# ✅ Use secrets manager
from google.cloud import secretmanager
```

### Authentication
- Use OAuth 2.0 for user-facing apps
- Use service accounts for backend automation
- Rotate keys regularly

### Rate Limiting
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=60)  # 10 calls per minute
def call_llm(*args, **kwargs):
    return llm.call(*args, **kwargs)
```

### Input Validation
```python
def validate_requirements(text):
    if len(text) < 100:
        raise ValueError("Requirements too short")
    if len(text) > 100000:
        raise ValueError("Requirements too long")
    return text
```

---

## Monitoring & Logging

### Add Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Starting pipeline for {user_id}")
logger.info(f"Generated {len(epics)} epics")
logger.error(f"Failed to create tracker: {error}")
```

### Monitor API Usage
```python
# Track in database
import time
start = time.time()
result = run(...)
duration = time.time() - start

log_event({
    "user": user_id,
    "llm": llm_provider,
    "tracker": tracker_type,
    "duration": duration,
    "epics": len(result['epics']),
    "stories": len(result['user_stories'])
})
```

---

## Next Steps

1. **Choose integration method** based on your use case
2. **Deploy API server** (if needed)
3. **Set up credentials** for your LLM + tracker
4. **Test with sample requirements**
5. **Share with team**

See the specific guides above for step-by-step setup for each tool!

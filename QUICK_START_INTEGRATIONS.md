# Project Initiation Assistant — Quick Start Guide

**One-page reference for using the skill with different AI tools.**

---

## 🚀 Fastest Option: Claude Web

```bash
# Already integrated! Just open:
claude.ai/code

# Add your project folder
# Type: /project-initiation-assistant
# Paste meeting notes → Get backlog in seconds
```

---

## 🔌 All Integration Options

### **1. Claude Web (claude.ai)**
- ⏱️ **Time:** 5 minutes
- 🎯 **Best for:** Full analysis, detailed PRD, team collaboration
- 📝 **Setup:** Already built-in, just use!

```
1. Go to claude.ai/code
2. Add project folder
3. Use: @project-initiation-assistant
4. Paste meeting notes
```

---

### **2. ChatGPT / OpenAI**
- ⏱️ **Time:** 15 minutes
- 🎯 **Best for:** ChatGPT users, OpenAI ecosystem
- 📝 **Setup:**

```bash
# Step 1: Deploy API server
pip install flask
python scripts/api_server.py  # Runs on :5000

# Step 2: Create Custom GPT at chat.openai.com/gpts/editor
Name: "Project Initiation Assistant"
Instructions: (paste from MULTI_AI_GUIDE.md)

# Step 3: Add Action (OpenAPI schema)
POST http://localhost:5000/api/v1/generate-backlog
{
  "raw_text": string,
  "llm_provider": "openai",
  "tracker_type": string
}

# Step 4: Use in ChatGPT
"Create a backlog from these meeting notes..."
```

---

### **3. Google Gemini**
- ⏱️ **Time:** 10 minutes
- 🎯 **Best for:** Google ecosystem, AI Studio
- 📝 **Setup:**

```bash
# Option A: Direct API
export GOOGLE_API_KEY="AIzaSy..."
python scripts/run_pipeline.py notes.txt \
  --llm-provider gemini \
  --tracker-type sheets

# Option B: AI Studio (aistudio.google.com)
1. Create new prompt
2. Paste skill definition
3. Add meeting notes
4. Generate → Get backlog
```

---

### **4. VSCode Extension**
- ⏱️ **Time:** 20 minutes
- 🎯 **Best for:** Developers, integrated workflow
- 📝 **Setup:**

```bash
# 1. Install dependencies
pip install -r scripts/requirements.txt

# 2. Create extension
mkdir vscode-project-initiation
cd vscode-project-initiation
npm init -y
npm install vscode

# 3. Copy extension code (see AI_TOOLS_INTEGRATION.md)

# 4. Run API server
python scripts/api_server.py &

# 5. Start VS Code
code --extensionDevelopmentPath=. .

# 6. F5 to launch extension host

# 7. Cmd+Shift+P: "Generate Project Backlog"
```

---

### **5. Slack Bot**
- ⏱️ **Time:** 20 minutes
- 🎯 **Best for:** Team communication, quick access
- 📝 **Setup:**

```bash
# 1. Create app at api.slack.com/apps → New App

# 2. Add Slash Command
   Command: /backlog
   Request URL: https://your-domain.com/slack/slash

# 3. Install bot code (see AI_TOOLS_INTEGRATION.md)

# 4. Run bot
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
python slack_bot.py

# 5. Use in Slack
   /backlog Meeting notes from kickoff today
```

---

### **6. Discord Bot**
- ⏱️ **Time:** 15 minutes
- 🎯 **Best for:** Gaming, tech communities
- 📝 **Setup:**

```bash
# 1. Create bot at discord.com/developers/applications

# 2. Enable Slash Commands

# 3. Install bot code (see AI_TOOLS_INTEGRATION.md)

# 4. Run
export DISCORD_BOT_TOKEN="MzA3..."
python discord_bot.py

# 5. Use
   /backlog Meeting notes here...
```

---

### **7. Cursor Editor**
- ⏱️ **Time:** 10 minutes
- 🎯 **Best for:** Cursor users, AI-native editing
- 📝 **Setup:**

```bash
# Option A: Use as API
python scripts/api_server.py

# Option B: Use MCP Server (see AI_TOOLS_INTEGRATION.md)

# In Cursor:
# Composer (Cmd+Shift+L)
# Paste meeting notes
# Agent processes → Returns backlog + tracker URL
```

---

### **8. Web API (Standalone)**
- ⏱️ **Time:** 10 minutes
- 🎯 **Best for:** Any tool, custom workflows
- 📝 **Setup:**

```bash
# 1. Run API server
pip install flask
python scripts/api_server.py

# 2. Test
curl -X POST http://localhost:5000/api/v1/generate-backlog \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Meeting notes...",
    "llm_provider": "claude",
    "tracker_type": "sheets",
    "drive_folder_id": "folder_123"
  }'

# 3. Get results
{
  "success": true,
  "prd": "...",
  "epics": [...],
  "user_stories": [...],
  "risks": [...],
  "tracker_url": "https://..."
}
```

---

### **9. CLI Tool (Command Line)**
- ⏱️ **Time:** 5 minutes
- 🎯 **Best for:** Scripts, CI/CD, automation
- 📝 **Setup:**

```bash
# Run directly
python scripts/run_pipeline.py meeting_notes.txt \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "folder_123" \
  --share-with alice@example.com bob@example.com

# Or as installed command
pip install -e .
project-init meeting_notes.txt --llm claude --tracker sheets
```

---

### **10. Zapier / Make.com (No-Code)**
- ⏱️ **Time:** 15 minutes
- 🎯 **Best for:** Automation, non-technical users
- 📝 **Setup:**

```
Zapier:
1. Create Zap at zapier.com
2. Trigger: Gmail new email
3. Action: POST to your API endpoint
4. Receive: Tracker URL in response

Make.com:
1. Create Scenario
2. Trigger: Google Forms submission
3. Action: HTTP request to API
4. Automation: Send email with tracker link
```

---

## 🎯 Recommended by Use Case

### For Individual Developers
- **Best:** Claude Web, VSCode Extension, CLI
- **Setup:** 5-20 minutes

### For Teams
- **Best:** Slack Bot, Claude Web, Web API
- **Setup:** 15-30 minutes

### For Organizations
- **Best:** Jira Integration, Google Sheets, Slack Bot
- **Setup:** 20-40 minutes

### For Non-Technical Users
- **Best:** ChatGPT Custom GPT, Zapier, Google AI Studio
- **Setup:** 10-20 minutes

### For CI/CD / Automation
- **Best:** CLI, Web API, GitHub Actions
- **Setup:** 10-15 minutes

---

## 📋 Pre-Setup Checklist

Before starting, make sure you have:

- [ ] **LLM API Key** (pick one):
  - `ANTHROPIC_API_KEY` (Claude)
  - `OPENAI_API_KEY` (ChatGPT)
  - `GOOGLE_API_KEY` (Gemini)

- [ ] **Tracker Credentials** (pick one):
  - `GOOGLE_APPLICATION_CREDENTIALS` (Google Sheets)
  - `JIRA_API_TOKEN` (Jira)
  - `LINEAR_API_KEY` (Linear)
  - `AIRTABLE_API_KEY` (Airtable)

- [ ] **Python 3.8+** installed

- [ ] **Dependencies installed:**
  ```bash
  pip install -r scripts/requirements.txt
  ```

- [ ] **Folder/Project ID ready** (where results will be stored)

---

## 🚦 Quick Decision Tree

```
┌─ Are you using Claude?
│  ├─ YES → Use Claude Web (fastest!)
│  └─ NO → Continue
│
├─ Do you prefer terminal/script?
│  ├─ YES → Use CLI tool
│  └─ NO → Continue
│
├─ Do you need team collaboration?
│  ├─ YES (Slack) → Use Slack Bot
│  ├─ YES (Discord) → Use Discord Bot
│  └─ NO → Continue
│
├─ Do you use an IDE?
│  ├─ VSCode → Use VSCode Extension
│  ├─ Cursor → Use Cursor MCP
│  ├─ JetBrains → Use Plugin (or Web API)
│  └─ Other → Continue
│
└─ Use Web API
   (works with anything!)
```

---

## 🔧 Environment Setup

### One-Time Setup

```bash
# 1. Clone/extract project
cd "claude skill assignment"

# 2. Install Python dependencies
pip install -r scripts/requirements.txt

# 3. Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Optional: Add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
source .env
```

### For Each Integration

```bash
# Claude Web
# (No setup needed - already built-in!)

# ChatGPT
export OPENAI_API_KEY="sk-proj-..."
python scripts/api_server.py

# Slack Bot
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
python slack_bot.py

# VSCode Extension
cd vscode-project-initiation
npm install
npm run compile
code --install-extension dist/
```

---

## ✅ Test Your Integration

### Test 1: CLI
```bash
python scripts/run_pipeline.py \
  --help
```

### Test 2: API
```bash
python scripts/api_server.py &
curl http://localhost:5000/api/v1/health
```

### Test 3: Full Pipeline
```bash
# Create test file
echo "Meeting: Sales dashboard project, 8 week timeline, Salesforce + Slack integration" > test.txt

# Run pipeline
python scripts/run_pipeline.py test.txt \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "test_folder_id"
```

---

## 📚 Learn More

- **Full Integration Guide:** `AI_TOOLS_INTEGRATION.md`
- **Adapter Examples:** `ADAPTER_EXAMPLES.py`
- **Customization:** `MULTI_AI_GUIDE.md`
- **Generalization:** `GENERALIZATION_SUMMARY.md`

---

## 💡 Pro Tips

1. **Use Claude Web first** for exploration
2. **Slack Bot** for team adoption
3. **CLI** for automation/CI-CD
4. **Web API** for flexibility
5. **Custom GPT** for ChatGPT users

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'anthropic'` | `pip install -r scripts/requirements.txt` |
| `ANTHROPIC_API_KEY not found` | `export ANTHROPIC_API_KEY="sk-ant-..."` |
| `Connection refused (localhost:5000)` | `python scripts/api_server.py` in separate terminal |
| `Slack token invalid` | Check token at api.slack.com/apps |
| `Google Sheets permission denied` | Verify service account has folder access |

---

**Ready to get started? Pick one method above and follow the setup steps!** 🎉

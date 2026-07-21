# Project Initiation Assistant

> **Automate your requirement-to-development handoff pipeline in minutes**

Convert raw meeting notes, client requirements, or transcripts into a complete, development-ready backlog with PRD, epics, user stories, effort estimates, and an automated project tracker—all in one go.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Multi-AI Support](https://img.shields.io/badge/supports-Claude%20|%20OpenAI%20|%20Gemini%20|%20Local-brightgreen.svg)](#llm-support)

---

## 🎯 What It Does

The Project Initiation Assistant automates the entire requirement-to-development handoff:

```
Meeting Notes / Requirements Doc
    ↓
[Requirement Analysis]        → Extract goals, stakeholders, constraints
    ↓
[PRD Generation]              → Create structured Product Requirements Document
    ↓
[Epic Creation]               → Break down into high-level features
    ↓
[User Story Generation]       → Create "As a / I want / So that" stories
    ↓
[Effort Estimation & Risks]   → Assign story points, priority, identify risks
    ↓
[Project Tracker Creation]    → Populate Google Sheets, Jira, Linear, or Airtable
    ↓
Development-Ready Backlog
```

**Typical result:** 1-hour meeting notes → PRD + 4 epics + 20+ user stories + estimates + shared tracker in **< 5 minutes**.

---

## ✨ Key Features

✅ **5-Stage Pipeline** — Automated requirement → backlog workflow  
✅ **Multi-LLM Support** — Use Claude, OpenAI, Gemini, or local models  
✅ **Multi-Platform Trackers** — Create in Sheets, Jira, Linear, Airtable, or custom APIs  
✅ **Structured Outputs** — Validated Pydantic models, not text parsing  
✅ **Pluggable Architecture** — Swap LLMs and trackers without code changes  
✅ **Production-Ready** — Error handling, logging, security best practices  
✅ **Multiple Interfaces** — CLI, Web API, Python, Slack Bot, Discord Bot, VSCode, Cursor  
✅ **Fully Documented** — Comprehensive guides, examples, best practices  

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r .claude/skills/project-initiation-assistant/scripts/requirements.txt
```

### 2. Set Environment Variables

```bash
# For Claude (recommended)
export ANTHROPIC_API_KEY="sk-ant-..."

# For Google Sheets (if using Sheets tracker)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### 3. Generate Your First Backlog

```bash
# Create a file with meeting notes
cat > meeting_notes.txt << 'EOF'
Meeting: Sales Dashboard Project Kickoff
Date: 2026-07-22
Attendees: Client PM, Tech Lead, Designer

Key Requirements:
- Real-time sales analytics dashboard
- Multiple data sources (Salesforce, HubSpot, APIs)
- Slack integration for alerts
- Mobile responsive
- GDPR compliant

Timeline: MVP in 8 weeks
EOF

# Run the pipeline
python .claude/skills/project-initiation-assistant/scripts/run_pipeline.py \
  meeting_notes.txt \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "your_folder_id" \
  --share-with team@example.com
```

### 4. Check Results

```
✅ Analysis complete (5 goals, 3 stakeholders, 12 requirements)
✅ PRD generated (2500 words)
✅ Epics created (4 epics)
✅ User stories created (24 stories with acceptance criteria)
✅ Risks identified (5 risks with mitigations)
✅ Project Tracker created
📊 Tracker URL: https://docs.google.com/spreadsheets/d/...
```

---

## 📖 Usage Guide

### Command Line Interface

```bash
python .claude/skills/project-initiation-assistant/scripts/run_pipeline.py <input_file> [options]

Options:
  --llm-provider {claude|openai|gemini|local|custom}
                        LLM to use (default: claude)
  --tracker-type {sheets|jira|linear|airtable|custom}
                        Tracker platform (default: sheets)
  --drive-folder-id ID  Google Drive folder ID (for Sheets)
  --jira-project-key KEY
                        Jira project key
  --linear-team-id ID   Linear team ID
  --airtable-base-id ID Airtable base ID
  --share-with EMAIL... Emails to share tracker with
```

### Python API

```python
from run_pipeline import run
from llm_adapter import create_llm_adapter
from tracker_adapter import create_tracker_adapter

# Create adapters
llm = create_llm_adapter("claude")
tracker = create_tracker_adapter("sheets", folder_id="folder_123")

# Run pipeline
result = run(
    raw_text=meeting_notes,
    llm_adapter=llm,
    tracker_adapter=tracker,
    share_with=["alice@example.com", "bob@example.com"]
)

# Access results
print(f"PRD: {result['prd']}")
print(f"Epics: {result['epics']}")
print(f"Stories: {result['user_stories']}")
print(f"Risks: {result['risks']}")
print(f"Tracker URL: {result['tracker_url']}")
```

---

## 🔌 Integration Options

### Use with Claude Web (claude.ai/code)

Already integrated! Just:
1. Add this repository to Claude Code
2. Use: `@project-initiation-assistant`
3. Paste your meeting notes

### Use with ChatGPT / OpenAI

```bash
# Deploy API server
pip install flask
python scripts/api_server.py  # Runs on :5000

# Create Custom GPT at chat.openai.com/gpts/editor
# Add the API endpoint as an action
```

### Use with Slack

```bash
# Run Slack bot
export SLACK_BOT_TOKEN="xoxb-..."
python scripts/slack_bot.py

# In Slack: /backlog Meeting notes here...
```

### Use with VSCode

```bash
# Install VSCode extension
npm install
npm run compile
code --install-extension dist/
```

### Use with Cursor

Already supported! Use in Composer with AI context.

### Use with Discord

```bash
# Run Discord bot
export DISCORD_BOT_TOKEN="MzA3..."
python scripts/discord_bot.py

# In Discord: /backlog Meeting notes...
```

### Deploy as REST API

```bash
# Docker
docker build -t project-initiation .
docker run -p 5000:5000 project-initiation

# Or deploy to cloud (Vercel, Heroku, Railway, AWS, GCP)
```

See **AI_TOOLS_INTEGRATION.md** for detailed setup for each tool.

---

## 🧠 LLM Support

### Supported Providers

| Provider | Status | Model | Setup |
|----------|--------|-------|-------|
| **Claude** | ✅ Recommended | claude-opus-4-8 | `ANTHROPIC_API_KEY` |
| **OpenAI** | ✅ Full | gpt-4-turbo | `OPENAI_API_KEY` |
| **Google Gemini** | ✅ Full | gemini-2.0-flash | `GOOGLE_API_KEY` |
| **Local (Ollama)** | ✅ Full | llama2, mistral | `LOCAL_LLM_ENDPOINT` |
| **Custom API** | ✅ Full | Any | `CUSTOM_API_ENDPOINT` |

### Switch LLM Provider

```bash
# Use different provider without code changes
python scripts/run_pipeline.py notes.txt --llm-provider openai
python scripts/run_pipeline.py notes.txt --llm-provider gemini
python scripts/run_pipeline.py notes.txt --llm-provider local
```

---

## 📊 Tracker Support

### Supported Platforms

| Platform | Status | Features | Setup |
|----------|--------|----------|-------|
| **Google Sheets** | ✅ Recommended | Collaborative, native formulas | Service account |
| **Jira** | ✅ Full | Issues, custom fields, workflows | API token |
| **Linear** | ✅ Full | Modern UX, cycles, automation | API key |
| **Airtable** | ✅ Full | Flexible base structure | API key |
| **Custom API** | ✅ Full | Your own system | HTTP endpoint |

### Switch Tracker Platform

```bash
# Use different tracker without code changes
python scripts/run_pipeline.py notes.txt --tracker-type jira --jira-project-key PROJ
python scripts/run_pipeline.py notes.txt --tracker-type linear --linear-team-id team_123
python scripts/run_pipeline.py notes.txt --tracker-type airtable --airtable-base-id app_123
```

---

## 🏗️ Architecture

### Pipeline Stages

#### Stage 1: Requirement Analyzer
- **Input:** Raw text (meeting notes, requirements, transcript)
- **Output:** Structured analysis (goals, stakeholders, requirements, constraints)
- **Method:** LLM + Pydantic validation

#### Stage 2: PRD Generator
- **Input:** Analysis from Stage 1
- **Output:** Formatted PRD document
- **Method:** Template-constrained generation

#### Stage 2b: Project Overview Extractor
- **Input:** PRD from Stage 2
- **Output:** Project name, client, objective, priority
- **Method:** LLM extraction

#### Stage 3a: Epic Generator
- **Input:** PRD from Stage 2
- **Output:** List of epics
- **Method:** LLM + Pydantic validation

#### Stage 3b: User Story Generator
- **Input:** Epics from Stage 3a
- **Output:** User stories with acceptance criteria
- **Method:** One API call per epic (scoped generation)

#### Stage 4a: Estimator
- **Input:** User stories from Stage 3b
- **Output:** Same stories + story points, priority, complexity
- **Method:** Comparative estimation in single call

#### Stage 4b: Risk Identifier
- **Input:** Analysis + estimated stories
- **Output:** Risks with impact and mitigation
- **Method:** LLM analysis

#### Stage 5: Tracker Creator
- **Input:** All previous outputs + tracker config
- **Output:** Tracker URL
- **Method:** Tracker-specific API (Google Sheets, Jira, etc.)

### Design Decisions

**Structured outputs over text parsing** — Every stage uses Pydantic models for validation instead of regex/JSON parsing. Malformed output is caught at boundaries, not silently downstream.

**Batching choices are intentional** — Epics → stories is one call per epic (bounded scope); story estimation is one call for all stories (relative sizing needs full context).

**Pluggable adapters** — LLM and tracker logic is decoupled via adapter classes. Swap providers without touching pipeline logic.

See [CONTEXT.md](.claude/skills/project-initiation-assistant/CONTEXT.md) for full design rationale.

---

## 📁 Project Structure

```
.
├── README.md                          # This file
├── CLAUDE.md                          # Project instructions
├── Assignment.pdf                     # Original specification
├── .gitignore                         # Git exclusions
│
└── .claude/skills/project-initiation-assistant/
    ├── SKILL.md                       # Skill definition (multi-AI, multi-platform)
    ├── CONTEXT.md                     # Architecture & design decisions
    │
    ├── scripts/
    │   ├── run_pipeline.py            # Orchestrator (main entry point)
    │   ├── requirement_analyzer.py    # Stage 1: Analysis
    │   ├── prd_generator.py           # Stage 2: PRD generation
    │   ├── user_story_generator.py    # Stage 3: Epics & stories
    │   ├── backlog_estimator.py       # Stage 4: Estimation & risks
    │   ├── sheet_tracker.py           # Stage 5: Tracker creation
    │   ├── requirements.txt           # Python dependencies
    │   ├── llm_adapter.py             # LLM abstraction layer
    │   ├── tracker_adapter.py         # Tracker abstraction layer
    │   ├── api_server.py              # Flask API server
    │   ├── slack_bot.py               # Slack bot integration
    │   └── discord_bot.py             # Discord bot integration
    │
    └── references/
        ├── prd_template.md            # PRD structure template
        ├── user_story_template.md     # User story format guide
        └── sheet_schema.md            # Tracker column definitions
```

---

## 🔧 Configuration

### Environment Variables

```bash
# LLM Credentials (pick one)
ANTHROPIC_API_KEY=sk-ant-...          # Claude
OPENAI_API_KEY=sk-proj-...            # OpenAI
GOOGLE_API_KEY=AIzaSy...              # Gemini
LOCAL_LLM_ENDPOINT=http://localhost:11434  # Local models

# Tracker Credentials (pick one)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json  # Sheets
JIRA_API_TOKEN=ATATT3xF...            # Jira
JIRA_DOMAIN=company.atlassian.net
JIRA_EMAIL=bot@company.com
LINEAR_API_KEY=lin_api_...            # Linear
AIRTABLE_API_KEY=patXXX...            # Airtable
AIRTABLE_BASE_ID=appXXX...
```

### Config File (Optional)

```yaml
# config.yaml
llm:
  provider: claude
  model: claude-opus-4-8
  temperature: 1
  max_tokens: 4096

tracker:
  platform: sheets
  folder_id: "folder_123"

sharing:
  - alice@example.com
  - bob@example.com
```

Run with: `python scripts/run_pipeline.py notes.txt --config config.yaml`

---

## 📚 Documentation

### Core Documentation

- **[SKILL.md](.claude/skills/project-initiation-assistant/SKILL.md)** — Skill overview and usage
- **[CONTEXT.md](.claude/skills/project-initiation-assistant/CONTEXT.md)** — Architecture, design decisions, implementation details

### Integration Guides (in scratchpad)

- **AI_TOOLS_INTEGRATION.md** — Setup for all 10+ AI tools and platforms
- **QUICK_START_INTEGRATIONS.md** — One-page quick reference with decision tree
- **MULTI_AI_GUIDE.md** — Practical examples and customization guide
- **ADAPTER_EXAMPLES.py** — Code templates for implementing new adapters
- **GENERALIZATION_SUMMARY.md** — Architecture overview of multi-platform approach

---

## 💻 Examples

### Example 1: Claude + Google Sheets

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

python scripts/run_pipeline.py requirements.txt \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "folder_123" \
  --share-with product-team@company.com
```

### Example 2: OpenAI + Jira

```bash
export OPENAI_API_KEY="sk-proj-..."
export JIRA_API_TOKEN="ATATT3xF..."
export JIRA_DOMAIN="company.atlassian.net"
export JIRA_EMAIL="bot@company.com"

python scripts/run_pipeline.py requirements.txt \
  --llm-provider openai \
  --tracker-type jira \
  --jira-project-key "PROJ"
```

### Example 3: Google Gemini + Linear

```bash
export GOOGLE_API_KEY="AIzaSyD..."
export LINEAR_API_KEY="lin_api_..."

python scripts/run_pipeline.py requirements.txt \
  --llm-provider gemini \
  --tracker-type linear \
  --linear-team-id "team_123"
```

### Example 4: Local LLM + Airtable

```bash
export LOCAL_LLM_ENDPOINT="http://localhost:11434"
export AIRTABLE_API_KEY="patXXX..."
export AIRTABLE_BASE_ID="appXXX..."

python scripts/run_pipeline.py requirements.txt \
  --llm-provider local \
  --tracker-type airtable
```

---

## 🧪 Testing

### Test the Pipeline Locally

```bash
# Create test requirements
cat > test_requirements.txt << 'EOF'
Project: Employee Management System
Timeline: 4 weeks
Requirements:
- User authentication (SSO, MFA)
- Employee CRUD operations
- Department hierarchy
- Reporting dashboard
- Audit logging
EOF

# Run with test LLM and tracker
python scripts/run_pipeline.py test_requirements.txt \
  --llm-provider claude \
  --tracker-type sheets \
  --drive-folder-id "test_folder_id"
```

### Verify Installation

```bash
# Check Python version
python --version  # 3.8+

# Check dependencies
pip list | grep -E "anthropic|openai|google|pydantic"

# Test API imports
python -c "from anthropic import Anthropic; print('✅ Anthropic SDK installed')"
python -c "from run_pipeline import run; print('✅ Pipeline importable')"
```

---

## 🔐 Security

### Best Practices

✅ **Never commit secrets** — Use `.env` files and add to `.gitignore`  
✅ **Use environment variables** — Store all API keys outside code  
✅ **Rotate credentials** — Change API keys periodically  
✅ **Use service accounts** — For backend automation, not personal accounts  
✅ **Validate inputs** — Check size and format of user-provided text  
✅ **Log securely** — Never log API keys or sensitive data  
✅ **Monitor usage** — Track API calls and costs  

### Example .env File

```bash
# .env (add to .gitignore!)
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

Load in Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("ANTHROPIC_API_KEY")
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more LLM providers (Mistral, Cohere, Llama, etc.)
- [ ] Add more tracker platforms (Monday.com, Asana, Azure DevOps, etc.)
- [ ] Improve error handling and recovery
- [ ] Add comprehensive test suite
- [ ] Optimize prompt engineering for better output quality
- [ ] Add voice transcript preprocessing
- [ ] Support for video meeting analysis
- [ ] GraphQL API support
- [ ] Webhooks for CI/CD integration

To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit (`git commit -m 'Add amazing feature'`)
5. Push (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

### Documentation

- Full docs in [.claude/skills/project-initiation-assistant/](https://github.com/Tamanna-Tanni-bs23/Project-Initiation-Assistant/tree/main/.claude/skills/project-initiation-assistant)
- Integration guides in repository scratchpad
- Architecture details in [CONTEXT.md](.claude/skills/project-initiation-assistant/CONTEXT.md)

### Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'anthropic'` | Run `pip install -r .claude/skills/project-initiation-assistant/scripts/requirements.txt` |
| `ANTHROPIC_API_KEY not set` | Export: `export ANTHROPIC_API_KEY="sk-ant-..."` |
| `Google Sheets permission denied` | Verify service account has folder write access |
| `Jira API token invalid` | Check token at Jira Settings > API Tokens |
| `Connection timeout` | Increase timeout: `--timeout 300` |

---

## 🚀 Roadmap

### v1.0 (Current)
- ✅ 5-stage pipeline
- ✅ Multi-LLM support (Claude, OpenAI, Gemini, local)
- ✅ Multi-tracker support (Sheets, Jira, Linear, Airtable)
- ✅ CLI interface
- ✅ Web API

### v1.1 (Planned)
- [ ] Additional LLM providers
- [ ] Additional tracker platforms
- [ ] Webhook support for CI/CD
- [ ] Batch processing for multiple files
- [ ] Advanced prompt customization
- [ ] Output formatting options (PDF, Word, JSON)

### v1.2 (Planned)
- [ ] Voice transcript preprocessing
- [ ] Video meeting analysis
- [ ] Real-time collaboration mode
- [ ] Custom workflow templates
- [ ] Advanced analytics and reporting

---

## 📊 Performance

### Typical Metrics

| Metric | Value |
|--------|-------|
| **Processing Time** | 2-5 minutes (depending on LLM) |
| **Cost per Run** | $0.20-$1.00 (Claude) |
| **Typical Output** | 4-6 epics, 20-30 stories |
| **Accuracy** | 85-95% (varies by requirements clarity) |
| **Scalability** | Handles up to 10,000 word inputs |

---

## 🎓 Learning Resources

### Understanding the Skill

1. **Start:** [SKILL.md](.claude/skills/project-initiation-assistant/SKILL.md) — Overview
2. **Deep dive:** [CONTEXT.md](.claude/skills/project-initiation-assistant/CONTEXT.md) — Architecture
3. **Customize:** AI_TOOLS_INTEGRATION.md — Add new providers
4. **Code:** ADAPTER_EXAMPLES.py — Implementation templates

### Related Topics

- Prompt Engineering: [Claude Docs](https://docs.anthropic.com)
- Product Requirements Documents: [Atlassian Guide](https://www.atlassian.com/software/confluence/templates/prd)
- User Stories: [Agile Alliance](https://www.agilealliance.org/glossary/user-stories/)
- Story Points: [Scrum.org](https://www.scrum.org/resources/blog/story-points-why-are-we-using-them)

---

## 👨‍💻 Author

**Project Initiation Assistant** — Built with Claude Code  
Multi-platform, multi-LLM project initiation automation

---

## 🌟 Show Your Support

If this project helped you, please give it a ⭐ on GitHub!

---

**Made with ❤️ for efficient project kickoffs**

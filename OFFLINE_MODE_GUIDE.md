# Project Initiation Assistant — Offline Mode Guide

## 🚀 Run Offline Without Any Credentials!

The skill now works **100% offline** without requiring:
- ❌ Claude API key
- ❌ OpenAI API key
- ❌ Google API key
- ❌ Google Sheets credentials
- ❌ Jira credentials
- ❌ Linear credentials
- ❌ Any internet connection

Perfect for quick prototyping, demos, and users without API access.

---

## ✨ What You Get

### Input
- Plain text file with meeting notes, requirements, or transcript

### Automatic Output
1. **PRD (Markdown)** — Professional Product Requirements Document
2. **Epics (CSV)** — Epic breakdown with descriptions
3. **User Stories (CSV)** — 8-20 user stories with:
   - Story ID and epic reference
   - Story text in "As a / I want / So that" format
   - Acceptance criteria
   - Story points (1-13 Fibonacci scale)
   - Priority (High/Medium/Low)
   - Complexity (High/Medium/Low)
4. **Risks (CSV)** — Identified risks with impact and mitigation
5. **Summary (JSON)** — Complete metadata and file index

All saved to **local CSV/JSON/Markdown files** — no cloud needed!

---

## 🎯 Quick Start

### Step 1: Create Meeting Notes File

```bash
cat > meeting_notes.txt << 'EOF'
PROJECT KICKOFF: Mobile Banking App
Date: 2026-07-22
Attendees: Product Manager, Tech Lead, Designer

OBJECTIVES:
- Build secure mobile banking app
- Support iOS and Android
- Launch MVP in 12 weeks

REQUIREMENTS:
1. User authentication with biometric support
2. Account dashboard with balance and transactions
3. Money transfer capability
4. Bill payment and tracking
5. Push notifications for alerts

CONSTRAINTS:
- Must comply with PCI DSS
- GDPR compliance required
- 99.9% uptime SLA
- Support 1M+ concurrent users
EOF
```

### Step 2: Run Offline Pipeline

```bash
python3 run_offline.py meeting_notes.txt "Mobile Banking App" output/

# Or use defaults
python3 run_offline.py meeting_notes.txt
```

### Step 3: Open Generated Files

```bash
# View PRD
cat output/01_PRD_*.md

# View epics
cat output/02_Epics_*.csv

# View user stories
cat output/03_User_Stories_*.csv

# View risks
cat output/04_Risks_*.csv

# Open in Excel (if on macOS/Windows)
open output/  # or `start output/` on Windows
```

That's it! ✅

---

## 📋 Input Format

Your meeting notes file should include any of these sections:

```
OBJECTIVES / GOALS
- What you want to achieve
- Project vision
- Success criteria

STAKEHOLDERS / ATTENDEES
- Users
- Teams involved
- Decision makers

REQUIREMENTS / FEATURES
1. Feature 1
2. Feature 2
- Must-have functionality

CONSTRAINTS / TIMELINE
- Deadline (12 weeks, MVP, etc.)
- Budget
- Compliance requirements
- Performance requirements
- Scalability needs
```

**Format doesn't matter!** The offline analyzer uses intelligent pattern matching to extract:
- Goals from action-oriented text
- Stakeholders from mentions of users/teams
- Requirements from feature descriptions
- Constraints from timeline/budget/compliance mentions

---

## 📊 Output Files

### 1. 01_PRD_*.md (Markdown)

Professional PRD document with:
- Project overview
- Goals & objectives
- Stakeholders
- Functional requirements
- Constraints & assumptions
- Success criteria
- Next steps

**Example:**
```markdown
# PRODUCT REQUIREMENTS DOCUMENT
## Mobile Banking App

### 1. Project Overview
**Objective:** Build a secure mobile banking application

### 2. Goals & Objectives
1. Build a secure mobile banking application
2. Launch MVP in 12 weeks
3. Support iOS and Android platforms
...
```

### 2. 02_Epics_*.csv (Spreadsheet)

| epic_id | name | description |
|---------|------|-------------|
| EPIC-1 | User Authentication | Build authentication & biometric support |
| EPIC-2 | Dashboard | Real-time account dashboard |
| EPIC-3 | Money Transfer | Payments and fund transfers |

### 3. 03_User_Stories_*.csv (Spreadsheet)

| story_id | epic_id | story | acceptance_criteria | story_points | priority | complexity |
|----------|---------|-------|-------------------|--------------|----------|-----------|
| EPIC-1-1 | EPIC-1 | As a user, I want to log in with biometric so that access is secure | Fingerprint/face login works | 13 | High | High |
| EPIC-1-2 | EPIC-1 | As a user, I want MFA so that account is protected | MFA can be configured | 5 | Medium | Medium |

### 4. 04_Risks_*.csv (Spreadsheet)

| risk | impact | mitigation |
|------|--------|-----------|
| Third-party API downtime | Medium | Add fallback mechanisms |
| Regulatory compliance | Critical | Conduct audit, implement controls |
| Performance on slow devices | Medium | Optimize code, test on devices |

### 5. 00_Summary_*.json (Metadata)

```json
{
  "project_name": "Mobile Banking App",
  "generated_at": "2026-07-22T02:17:35.491110",
  "summary": {
    "epics": 5,
    "user_stories": 8,
    "total_story_points": 59,
    "risks": 4
  }
}
```

---

## 🔍 How It Works

### Stage 1: Intelligent Pattern Matching
- Extracts goals from action-oriented sentences
- Identifies stakeholders from user/team mentions
- Finds requirements from feature descriptions
- Detects constraints from timeline/compliance text

### Stage 2: Professional PRD Generation
- Uses extracted data to fill PRD template
- Structures content with clear sections
- Adds standard sections (success criteria, next steps)

### Stage 3: Automatic Epic Generation
- Matches requirements to epic templates:
  - Authentication, Dashboard, Integration, Reporting
  - Notifications, Mobile, API, Database, Performance, Security
- Creates descriptive epic names and descriptions

### Stage 4: Story Generation
- Generates "As a / I want / So that" stories
- Includes acceptance criteria for each story
- Assigns story points intelligently:
  - Large features (Dashboard, Reporting): 13 points
  - Complex features (API, Integration): 8 points
  - Simple features (Display, Update): 5 points

### Stage 5: Risk Identification
- Pattern matches on requirements to identify risks
- Matches against risk templates:
  - Timeline pressure, API dependencies, Compliance, Performance, Data consistency
- Provides mitigation strategies

### Stage 6: Export to Local Files
- Saves to CSV (Excel-compatible)
- Saves PRD as Markdown (readable, version-controllable)
- Creates JSON summary for tool integration
- All files in a local folder — no cloud upload!

---

## 💡 Real-World Examples

### Example 1: Quick MVP Planning

```bash
# Create quick notes
echo "
Build: Real-time analytics dashboard
Users: Sales team, executives
Features: Live KPIs, Slack alerts, PDF export
Timeline: 6 weeks
" > quick_notes.txt

# Generate backlog
python3 run_offline.py quick_notes.txt "Analytics Dashboard"

# Done! You have:
# - PRD (shows what to build)
# - 4 epics (organized features)
# - 12 stories (what to implement)
# - 3 risks (watch out for these)
```

### Example 2: Convert Meeting Recording to Backlog

```bash
# Transcribe Zoom recording to text (external tool)
# Save as meeting_transcript.txt

# Generate backlog
python3 run_offline.py meeting_transcript.txt "Project Name"

# Share outputs with team (all local files)
```

### Example 3: Quick Estimation for Stakeholder

```bash
# Client provides rough requirements
python3 run_offline.py client_requirements.txt "Client Project"

# View story points to give estimate
cat output/03_User_Stories_*.csv | cut -d, -f6 | tail -n +2 | paste -sd+ | bc

# Total points tells you rough effort/timeline
```

---

## 📈 Customization

### Change Project Name

```bash
python3 run_offline.py notes.txt "My Custom Project Name" output/
```

### Change Output Directory

```bash
python3 run_offline.py notes.txt "Project" /path/to/backlog/
```

### Use in Python

```python
from run_offline import OfflineAnalyzer, OfflinePRDGenerator, OfflineStoryGenerator

# Analyze
analyzer = OfflineAnalyzer()
analysis = analyzer.analyze(meeting_notes)

# Generate PRD
prd_gen = OfflinePRDGenerator()
prd = prd_gen.generate(analysis, "Project Name")

# Generate stories
story_gen = OfflineStoryGenerator()
epics = story_gen.generate_epics(analysis)
stories = []
for epic in epics:
    stories.extend(story_gen.generate_user_stories(epic))

# Use the data however you want
print(f"Generated {len(stories)} stories")
```

---

## ⚙️ Advanced Usage

### Batch Processing Multiple Files

```bash
for file in meetings/*.txt; do
    python3 run_offline.py "$file" "$(basename $file .txt)" "output/$(basename $file .txt)"
done
```

### Integration with Other Tools

Export to CSV, then import to:
- **Excel/Google Sheets** — Drag CSV files in
- **Jira** — Bulk import user stories
- **Linear** — Import via CSV
- **Trello** — Import as cards
- **Azure DevOps** — Bulk import work items
- **Asana** — Import tasks

### Generate on a Schedule

```bash
# Create cron job to generate backlog daily
0 9 * * * cd /path && python3 run_offline.py input.txt "Daily Backlog" output/ >> backlog.log 2>&1
```

---

## 🎯 When to Use Offline Mode

### ✅ Use Offline When:
- You don't have API credentials
- You need quick prototyping
- You're preparing for a meeting
- You need to demo the skill
- You work in air-gapped environments
- You want to avoid API costs
- You need to work offline/on a plane
- You're testing the pipeline logic

### ❌ Use API Mode When:
- You need perfect AI-generated content
- You want to customize prompts
- You need advanced LLM reasoning
- You're building production automation
- You want to use latest LLM models

---

## 🔄 Upgrading to API Mode

If you start with offline mode and later want to use Claude/OpenAI:

1. **Keep the same input** — No changes needed to your meeting notes
2. **Install dependencies** — `pip install -r requirements.txt`
3. **Set API keys** — `export ANTHROPIC_API_KEY="..."`
4. **Switch to API mode** — `python3 scripts/run_pipeline.py notes.txt --llm-provider claude`

Your meeting notes work with both!

---

## 📊 Sample Output

Running on "Mobile Banking App" meeting notes:

```
PROJECT INITIATION ASSISTANT - OFFLINE MODE
======================================================================
Project: Mobile Banking App
Input: meeting_notes.txt
Output: project_backlog

📋 Stage 1: Analyzing Requirements...
  ✅ 4 goals extracted
  ✅ 9 stakeholders identified
  ✅ 8 requirements found
  ✅ 8 constraints identified

📋 Stage 2: Generating PRD...
  ✅ PRD generated (2134 characters)

📋 Stage 3: Generating Epics & User Stories...
  ✅ 5 epics created:
      - User Authentication & Authorization
      - Dashboard & Visualization
      - Integration & Data Sync
      - Notifications & Alerts
      - Mobile & Responsive Design
  ✅ 8 user stories generated

📋 Stage 4: Identifying Risks...
  ✅ 4 risks identified

📋 Stage 5: Exporting Results...
  ✅ All files saved to: project_backlog/

📊 SUMMARY:
   Epics: 5
   User Stories: 8
   Total Story Points: 59
   Risks: 4

📁 OUTPUT FILES:
   ✅ 01_PRD_Mobile Banking App.md
   ✅ 02_Epics_Mobile Banking App.csv
   ✅ 03_User_Stories_Mobile Banking App.csv
   ✅ 04_Risks_Mobile Banking App.csv
   ✅ 00_Summary_Mobile Banking App.json

📂 All files saved to: /path/to/output/
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| `python3: command not found` | Install Python 3.8+ from python.org |
| `ModuleNotFoundError: No module named 'pydantic'` | Run `pip3 install pydantic` |
| `FileNotFoundError: input.txt` | Check file path: `ls input.txt` |
| No epics generated | Ensure meeting notes contain feature descriptions |
| Stories seem generic | That's normal! They're template-based. Use API mode for AI-generated stories. |

---

## 🎉 You're Ready!

The offline mode is **production-ready** for:
- ✅ Rapid prototyping
- ✅ Demo and pitches
- ✅ Quick backlog generation
- ✅ Offline environments
- ✅ Zero-cost option

**No credentials. No internet. No costs. Just run it!**

---

## Next Steps

1. **Create your meeting notes** file
2. **Run offline pipeline** — `python3 run_offline.py notes.txt "Project Name"`
3. **Open CSV files** in Excel or view with cat
4. **Share with team** — All files are portable
5. **Import to Jira/Linear/etc** — CSV files work everywhere

That's it! You have a professional project backlog in minutes. 🚀

---

**Questions? Check the main README.md or AI_TOOLS_INTEGRATION.md for more details!**

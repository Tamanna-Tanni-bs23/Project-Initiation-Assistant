#!/usr/bin/env python3
"""
Project Initiation Assistant - Offline Mode

Generate PRD, epics, stories, and project tracker WITHOUT requiring:
- API credentials (Claude, OpenAI, Gemini)
- Google credentials (no Google Sheets needed)
- Internet connection

Uses intelligent template-based generation and local file output (CSV, JSON, Markdown).
Works 100% offline - perfect for quick prototyping and demos.
"""

import json
import csv
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import re


# ============================================================================
# TEMPLATE-BASED ANALYSIS (No LLM needed)
# ============================================================================

class OfflineAnalyzer:
    """Analyzes requirements using intelligent pattern matching"""

    def __init__(self):
        self.keywords = {
            "goals": ["goal", "objective", "target", "aim", "achieve", "accomplish"],
            "stakeholders": ["stakeholder", "user", "team", "department", "client", "customer"],
            "requirements": ["requirement", "must", "should", "feature", "capability", "need"],
            "constraints": ["constraint", "limit", "timeline", "budget", "deadline", "compliance"]
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """Extract requirements using pattern matching"""
        lines = text.split('\n')

        analysis = {
            "goals": self._extract_section(lines, ["goal", "objective", "aim"]),
            "stakeholders": self._extract_section(lines, ["stakeholder", "user", "team", "attendee"]),
            "functional_requirements": self._extract_requirements(text),
            "constraints": self._extract_section(lines, ["constraint", "timeline", "budget", "deadline"])
        }

        # Fallback: extract if not found
        if not analysis["goals"]:
            analysis["goals"] = self._infer_goals(text)
        if not analysis["functional_requirements"]:
            analysis["functional_requirements"] = self._infer_requirements(text)

        return analysis

    def _extract_section(self, lines: List[str], keywords: List[str]) -> List[str]:
        """Extract items from a section marked by keywords"""
        results = []
        in_section = False

        for line in lines:
            lower_line = line.lower()

            # Check if this line starts a relevant section
            if any(kw in lower_line for kw in keywords):
                in_section = True
                continue

            # If in section and line is a bullet/number, extract it
            if in_section and line.strip():
                if line.strip().startswith(('-', '•', '*', '1.', '2.', '3.')):
                    item = re.sub(r'^[-•*\d.]+\s*', '', line.strip())
                    if item:
                        results.append(item)
                elif line.startswith(' ' * 4) or line.startswith('\t'):
                    item = line.strip()
                    if item:
                        results.append(item)

            # End section if we hit another header or blank line after content
            if in_section and not line.strip() and results:
                in_section = False

        return results if results else []

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract functional requirements"""
        requirements = []

        # Find sections with "requirement" keyword
        req_pattern = r'(?:requirement|feature|capability)s?:?\s*(.*?)(?:\n\n|\Z)'
        matches = re.finditer(req_pattern, text, re.IGNORECASE | re.DOTALL)

        for match in matches:
            section = match.group(1)
            items = re.findall(r'[-•*]\s*(.+?)(?=[-•*]|\n\n|\Z)', section, re.DOTALL)
            requirements.extend([item.strip() for item in items if item.strip()])

        return requirements if requirements else []

    def _infer_goals(self, text: str) -> List[str]:
        """Infer goals if not explicitly stated"""
        lines = text.split('\n')
        goals = []

        # Look for sentences with action words
        action_words = ['build', 'create', 'develop', 'implement', 'provide', 'enable', 'improve']

        for line in lines[:20]:  # Check first 20 lines
            if any(word in line.lower() for word in action_words):
                # Extract goal-like sentence
                goal = re.sub(r'^[-•*\d.]+\s*', '', line.strip())
                if goal and len(goal) > 10:
                    goals.append(goal)

        return goals if goals else ["Achieve project objectives", "Deliver value to stakeholders"]

    def _infer_requirements(self, text: str) -> List[str]:
        """Infer requirements if not explicitly stated"""
        lines = text.split('\n')
        requirements = []

        # Look for technical terms and features
        tech_terms = ['dashboard', 'api', 'integration', 'auth', 'database', 'report', 'alert', 'mobile']

        for line in lines:
            if any(term in line.lower() for term in tech_terms):
                req = re.sub(r'^[-•*\d.]+\s*', '', line.strip())
                if req and len(req) > 5:
                    requirements.append(req)

        return requirements if requirements else ["System architecture", "User authentication", "Data storage"]


# ============================================================================
# TEMPLATE-BASED PRD GENERATION (No LLM needed)
# ============================================================================

class OfflinePRDGenerator:
    """Generates PRD using templates and analysis"""

    def generate(self, analysis: Dict[str, Any], project_name: str = "Project") -> str:
        """Generate PRD from analysis"""

        prd = f"""
# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## {project_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. Project Overview

**Project Name:** {project_name}

**Objective:** {self._get_first_or_default(analysis['goals'], 'Deliver high-quality solution')}

---

## 2. Goals & Objectives

"""

        for i, goal in enumerate(analysis['goals'], 1):
            prd += f"\n{i}. {goal}"

        prd += f"""

---

## 3. Stakeholders

"""

        for i, stakeholder in enumerate(analysis['stakeholders'], 1):
            prd += f"\n- {stakeholder}"

        prd += f"""

---

## 4. Functional Requirements

"""

        for i, req in enumerate(analysis['functional_requirements'], 1):
            prd += f"\n{i}. {req}"

        prd += f"""

---

## 5. Constraints & Assumptions

"""

        for i, constraint in enumerate(analysis['constraints'], 1):
            prd += f"\n- {constraint}"

        prd += """

---

## 6. Success Criteria

- Requirements are clearly defined and prioritized
- Stakeholders have reviewed and approved the PRD
- Timeline and resources are realistic and achievable
- Quality standards are established and measurable

---

## 7. Next Steps

1. Review and approve PRD with stakeholders
2. Break down into epics and user stories
3. Estimate effort and create project timeline
4. Identify and mitigate risks
5. Begin implementation

---

*This PRD was generated using the Project Initiation Assistant*
"""

        return prd

    def _get_first_or_default(self, lst: List[str], default: str) -> str:
        return lst[0] if lst else default


# ============================================================================
# TEMPLATE-BASED EPIC & STORY GENERATION (No LLM needed)
# ============================================================================

class OfflineStoryGenerator:
    """Generates epics and user stories using templates"""

    def generate_epics(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate epics from requirements"""

        epic_templates = {
            "authentication": "User Authentication & Authorization",
            "dashboard": "Dashboard & Visualization",
            "integration": "Integration & Data Sync",
            "reporting": "Reporting & Analytics",
            "notification": "Notifications & Alerts",
            "mobile": "Mobile & Responsive Design",
            "api": "API Development",
            "database": "Data Management",
            "performance": "Performance & Optimization",
            "security": "Security & Compliance"
        }

        epics = []
        epic_id = 1
        used_templates = set()

        # Match requirements to epic templates
        all_requirements = ' '.join(analysis['functional_requirements']).lower()

        for keyword, epic_name in epic_templates.items():
            if keyword in all_requirements and keyword not in used_templates:
                epics.append({
                    "epic_id": f"EPIC-{epic_id}",
                    "name": epic_name,
                    "description": f"Build and implement {epic_name.lower()} capabilities"
                })
                used_templates.add(keyword)
                epic_id += 1

        # If no epics generated, create generic ones
        if not epics:
            epics = [
                {
                    "epic_id": "EPIC-1",
                    "name": "Core Features",
                    "description": "Implement core functionality"
                },
                {
                    "epic_id": "EPIC-2",
                    "name": "User Experience",
                    "description": "Enhance user interface and experience"
                }
            ]

        return epics

    def generate_user_stories(self, epic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate user stories for an epic"""

        stories_by_epic = {
            "authentication": [
                {
                    "story": "As a user, I want to log in with SSO so that I can access the system securely",
                    "acceptance_criteria": "Login works with single sign-on providers"
                },
                {
                    "story": "As a user, I want to enable MFA so that my account is protected",
                    "acceptance_criteria": "MFA can be configured and enforced"
                }
            ],
            "dashboard": [
                {
                    "story": "As a user, I want to see real-time metrics so that I can track progress",
                    "acceptance_criteria": "Dashboard displays up-to-date KPIs"
                },
                {
                    "story": "As a user, I want to customize my dashboard so that I see relevant information",
                    "acceptance_criteria": "Users can add/remove widgets from dashboard"
                }
            ],
            "integration": [
                {
                    "story": "As a developer, I want to connect external APIs so that data is synchronized",
                    "acceptance_criteria": "API integration works reliably with error handling"
                },
                {
                    "story": "As a user, I want data synced automatically so that information stays current",
                    "acceptance_criteria": "Data syncs within acceptable timeframe"
                }
            ],
            "reporting": [
                {
                    "story": "As a manager, I want to generate custom reports so that I can analyze data",
                    "acceptance_criteria": "Reports can be created with custom filters"
                },
                {
                    "story": "As a user, I want to export reports to PDF so that I can share them",
                    "acceptance_criteria": "PDF export maintains formatting and data"
                }
            ],
            "notification": [
                {
                    "story": "As a user, I want to receive alerts so that I'm notified of important events",
                    "acceptance_criteria": "Alerts are delivered in real-time"
                }
            ],
            "mobile": [
                {
                    "story": "As a mobile user, I want the app to work on my phone so that I can access it anywhere",
                    "acceptance_criteria": "UI is responsive and works on mobile devices"
                }
            ]
        }

        # Get stories for this epic
        epic_name = epic['name'].lower()
        stories = []

        for keyword, epic_stories in stories_by_epic.items():
            if keyword in epic_name:
                stories = epic_stories
                break

        # Fallback stories
        if not stories:
            stories = [
                {
                    "story": f"As a user, I want {epic['name'].lower()} so that I can be productive",
                    "acceptance_criteria": f"{epic['name']} functionality is working correctly"
                },
                {
                    "story": f"As a user, I want {epic['name'].lower()} to be reliable so that I can trust the system",
                    "acceptance_criteria": f"{epic['name']} has proper error handling and monitoring"
                }
            ]

        # Add IDs and epic reference
        result = []
        for i, story in enumerate(stories, 1):
            result.append({
                "story_id": f"{epic['epic_id']}-{i}",
                "epic_id": epic['epic_id'],
                "story": story['story'],
                "acceptance_criteria": story['acceptance_criteria'],
                "story_points": self._estimate_points(story['story']),
                "priority": self._assign_priority(i, len(stories)),
                "complexity": self._assign_complexity(story['story'])
            })

        return result

    def _estimate_points(self, story: str) -> int:
        """Estimate story points based on story text"""
        complexity_indicators = ["complex", "difficult", "multiple", "integrate", "api", "database"]
        large_indicators = ["dashboard", "report", "integration", "system"]

        story_lower = story.lower()

        if any(word in story_lower for word in large_indicators):
            return 13
        elif any(word in story_lower for word in complexity_indicators):
            return 8
        else:
            return 5

    def _assign_priority(self, position: int, total: int) -> str:
        """Assign priority based on position"""
        if position == 1:
            return "High"
        elif position <= total / 2:
            return "Medium"
        else:
            return "Low"

    def _assign_complexity(self, story: str) -> str:
        """Assign complexity based on story text"""
        high_complexity = ["integrate", "api", "database", "system", "multiple"]
        medium_complexity = ["display", "create", "update", "feature"]

        story_lower = story.lower()

        if any(word in story_lower for word in high_complexity):
            return "High"
        elif any(word in story_lower for word in medium_complexity):
            return "Medium"
        else:
            return "Low"


# ============================================================================
# RISK IDENTIFICATION (Template-based)
# ============================================================================

class OfflineRiskIdentifier:
    """Identifies risks using pattern matching"""

    def identify(self, analysis: Dict[str, Any], stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify risks from analysis and stories"""

        risks = []

        # Risk templates
        risk_templates = [
            {
                "pattern": ["timeline", "deadline", "week"],
                "risk": "Timeline pressure could impact quality",
                "impact": "High - Rushed implementation may introduce bugs",
                "mitigation": "Establish realistic deadlines, prioritize features, plan for testing"
            },
            {
                "pattern": ["integration", "api", "external"],
                "risk": "Third-party API changes or downtime",
                "impact": "Medium - System depends on external services",
                "mitigation": "Add fallback mechanisms, monitor API status, implement retries"
            },
            {
                "pattern": ["compliance", "gdpr", "security", "regulation"],
                "risk": "Regulatory and compliance requirements",
                "impact": "Critical - Legal implications",
                "mitigation": "Conduct compliance audit, implement controls, regular reviews"
            },
            {
                "pattern": ["mobile", "responsive", "performance"],
                "risk": "Performance issues on slower devices",
                "impact": "Medium - Poor user experience",
                "mitigation": "Optimize code, test on various devices, implement caching"
            },
            {
                "pattern": ["data", "database", "sync"],
                "risk": "Data consistency and sync issues",
                "impact": "High - Inaccurate data impact decisions",
                "mitigation": "Implement validation, monitoring, and conflict resolution"
            }
        ]

        # Match risks to requirements
        all_text = ' '.join(analysis['functional_requirements'] + analysis['constraints']).lower()

        for template in risk_templates:
            if any(pattern in all_text for pattern in template['pattern']):
                risks.append({
                    "risk": template['risk'],
                    "impact": template['impact'],
                    "mitigation": template['mitigation']
                })

        return risks if risks else [
            {
                "risk": "Unknown unknowns in requirements",
                "impact": "Medium - Unforeseen issues may arise",
                "mitigation": "Regular stakeholder communication and requirement refinement"
            }
        ]


# ============================================================================
# FILE OUTPUT (CSV, JSON, Markdown)
# ============================================================================

class OfflineFileExporter:
    """Export results to local files (no Google Sheets needed)"""

    def __init__(self, output_dir: str = "project_backlog"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_prd(self, prd: str, project_name: str) -> str:
        """Export PRD to Markdown"""
        filename = self.output_dir / f"01_PRD_{project_name}.md"
        with open(filename, 'w') as f:
            f.write(prd)
        return str(filename)

    def export_epics(self, epics: List[Dict[str, Any]], project_name: str) -> str:
        """Export epics to CSV"""
        filename = self.output_dir / f"02_Epics_{project_name}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['epic_id', 'name', 'description'])
            writer.writeheader()
            writer.writerows(epics)
        return str(filename)

    def export_stories(self, stories: List[Dict[str, Any]], project_name: str) -> str:
        """Export stories to CSV"""
        filename = self.output_dir / f"03_User_Stories_{project_name}.csv"
        with open(filename, 'w', newline='') as f:
            fieldnames = ['story_id', 'epic_id', 'story', 'acceptance_criteria', 'story_points', 'priority', 'complexity']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(stories)
        return str(filename)

    def export_risks(self, risks: List[Dict[str, Any]], project_name: str) -> str:
        """Export risks to CSV"""
        filename = self.output_dir / f"04_Risks_{project_name}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['risk', 'impact', 'mitigation'])
            writer.writeheader()
            writer.writerows(risks)
        return str(filename)

    def export_summary(self, summary: Dict[str, Any], project_name: str) -> str:
        """Export summary to JSON"""
        filename = self.output_dir / f"00_Summary_{project_name}.json"
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        return str(filename)

    def get_tracker_url(self) -> str:
        """Return local folder URL"""
        return f"📁 Local folder: {self.output_dir.absolute()}"


# ============================================================================
# MAIN PIPELINE (Offline, no API credentials needed)
# ============================================================================

def run_offline_pipeline(input_file: str, project_name: Optional[str] = None, output_dir: str = "project_backlog") -> Dict[str, Any]:
    """
    Run the complete pipeline offline without any API credentials.

    Args:
        input_file: Path to file with meeting notes or requirements
        project_name: Project name (extracted from file if not provided)
        output_dir: Directory to save outputs

    Returns:
        Dictionary with all results
    """

    # Read input
    with open(input_file, 'r') as f:
        raw_text = f.read()

    # Extract project name from file or use provided name
    if not project_name:
        project_name = Path(input_file).stem.replace('_', ' ').title()

    print("\n" + "="*70)
    print("PROJECT INITIATION ASSISTANT - OFFLINE MODE")
    print("="*70)
    print(f"Project: {project_name}")
    print(f"Input: {input_file}")
    print(f"Output: {output_dir}")

    # Stage 1: Analyze
    print("\n📋 Stage 1: Analyzing Requirements...")
    analyzer = OfflineAnalyzer()
    analysis = analyzer.analyze(raw_text)
    print(f"  ✅ {len(analysis['goals'])} goals extracted")
    print(f"  ✅ {len(analysis['stakeholders'])} stakeholders identified")
    print(f"  ✅ {len(analysis['functional_requirements'])} requirements found")
    print(f"  ✅ {len(analysis['constraints'])} constraints identified")

    # Stage 2: Generate PRD
    print("\n📋 Stage 2: Generating PRD...")
    prd_generator = OfflinePRDGenerator()
    prd = prd_generator.generate(analysis, project_name)
    print(f"  ✅ PRD generated ({len(prd)} characters)")

    # Stage 3: Generate Epics & Stories
    print("\n📋 Stage 3: Generating Epics & User Stories...")
    story_generator = OfflineStoryGenerator()
    epics = story_generator.generate_epics(analysis)
    print(f"  ✅ {len(epics)} epics created:")
    for epic in epics:
        print(f"      - {epic['name']}")

    all_stories = []
    for epic in epics:
        stories = story_generator.generate_user_stories(epic)
        all_stories.extend(stories)
        print(f"  ✅ {len(stories)} stories for {epic['name']}")

    # Stage 4: Identify Risks
    print("\n📋 Stage 4: Identifying Risks...")
    risk_identifier = OfflineRiskIdentifier()
    risks = risk_identifier.identify(analysis, all_stories)
    print(f"  ✅ {len(risks)} risks identified:")
    for risk in risks:
        print(f"      - {risk['risk']}")

    # Stage 5: Export to Files
    print("\n📋 Stage 5: Exporting Results...")
    exporter = OfflineFileExporter(output_dir)

    summary = {
        "project_name": project_name,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "epics": len(epics),
            "user_stories": len(all_stories),
            "total_story_points": sum(s['story_points'] for s in all_stories),
            "risks": len(risks)
        },
        "files": {}
    }

    summary["files"]["prd"] = exporter.export_prd(prd, project_name)
    print(f"  ✅ PRD exported to {Path(summary['files']['prd']).name}")

    summary["files"]["epics"] = exporter.export_epics(epics, project_name)
    print(f"  ✅ Epics exported to {Path(summary['files']['epics']).name}")

    summary["files"]["stories"] = exporter.export_stories(all_stories, project_name)
    print(f"  ✅ Stories exported to {Path(summary['files']['stories']).name}")

    summary["files"]["risks"] = exporter.export_risks(risks, project_name)
    print(f"  ✅ Risks exported to {Path(summary['files']['risks']).name}")

    summary["files"]["summary"] = exporter.export_summary(summary, project_name)
    print(f"  ✅ Summary exported to {Path(summary['files']['summary']).name}")

    # Print results
    print("\n" + "="*70)
    print("✅ BACKLOG GENERATED SUCCESSFULLY!")
    print("="*70)
    print(f"\n📊 SUMMARY:")
    print(f"   Epics: {len(epics)}")
    print(f"   User Stories: {len(all_stories)}")
    print(f"   Total Story Points: {sum(s['story_points'] for s in all_stories)}")
    print(f"   Risks: {len(risks)}")
    print(f"\n📁 OUTPUT FILES:")
    for key, path in summary["files"].items():
        print(f"   ✅ {Path(path).name}")
    print(f"\n📂 All files saved to: {exporter.output_dir.absolute()}")
    print("="*70)

    return summary


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║     PROJECT INITIATION ASSISTANT - OFFLINE MODE                     ║
║     Generate backlog WITHOUT API credentials or Google Sheets        ║
╚══════════════════════════════════════════════════════════════════════╝

USAGE:
    python run_offline.py <input_file> [project_name] [output_dir]

EXAMPLE:
    # Generate from meeting notes
    python run_offline.py meeting_notes.txt "Sales Dashboard" output/

    # Generate from requirements file
    python run_offline.py requirements.md

FEATURES:
    ✅ No API credentials required
    ✅ No Google Sheets needed
    ✅ Works completely offline
    ✅ Generates professional PRD, epics, stories, risks
    ✅ Exports to CSV, JSON, Markdown
    ✅ Fast local processing

INPUT FORMAT:
    Plain text file with meeting notes, requirements, or notes.
    Can include:
    - Goals and objectives
    - Stakeholders
    - Requirements
    - Constraints
    - Timeline and budget

OUTPUTS:
    📄 01_PRD_*.md              - Product Requirements Document
    📊 02_Epics_*.csv           - Epic breakdown
    📝 03_User_Stories_*.csv    - User stories with points
    ⚠️  04_Risks_*.csv          - Risk assessment
    📋 00_Summary_*.json        - Complete summary

NO CREDENTIALS NEEDED!
""")
        sys.exit(1)

    input_file = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "project_backlog"

    # Verify input file exists
    if not os.path.isfile(input_file):
        print(f"❌ Error: Input file '{input_file}' not found")
        sys.exit(1)

    # Run pipeline
    try:
        result = run_offline_pipeline(input_file, project_name, output_dir)
        print("\n✅ Process completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

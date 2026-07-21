"""End-to-end runner: raw requirement input -> populated Google Sheet tracker.

Chains the pipeline stages in the order documented in SKILL.md:
requirement_analyzer -> prd_generator -> user_story_generator ->
backlog_estimator -> sheet_tracker.
"""

from typing import List

from backlog_estimator import estimate, identify_risks
from prd_generator import extract_overview, generate
from requirement_analyzer import analyze
from sheet_tracker import create_tracker
from user_story_generator import generate_epics, generate_user_stories


def run(raw_text: str, drive_folder_id: str, share_with: List[str]) -> dict:
    """Run the full pipeline; return every intermediate artifact plus the tracker URL."""
    analysis = analyze(raw_text)
    prd = generate(analysis)
    project_overview = extract_overview(prd)

    epics = generate_epics(prd)
    user_stories = generate_user_stories(epics)
    user_stories = estimate(user_stories)
    risks = identify_risks(analysis, user_stories)

    spreadsheet_url = create_tracker(
        drive_folder_id=drive_folder_id,
        project_overview=project_overview,
        epics=epics,
        user_stories=user_stories,
        risks=risks,
        share_with=share_with,
    )

    return {
        "analysis": analysis,
        "prd": prd,
        "project_overview": project_overview,
        "epics": epics,
        "user_stories": user_stories,
        "risks": risks,
        "spreadsheet_url": spreadsheet_url,
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Run the Project Initiation Assistant pipeline end to end."
    )
    parser.add_argument(
        "input_file",
        help="Path to raw meeting notes, a client requirement document, or a voice transcript.",
    )
    parser.add_argument(
        "--drive-folder-id", required=True, help="Destination Google Drive folder ID."
    )
    parser.add_argument(
        "--share-with",
        nargs="*",
        default=[],
        help="Email addresses to share the tracker spreadsheet with.",
    )
    args = parser.parse_args()

    with open(args.input_file, encoding="utf-8") as f:
        raw_text = f.read()

    result = run(raw_text, args.drive_folder_id, args.share_with)

    print(f"Spreadsheet: {result['spreadsheet_url']}\n")
    print(json.dumps({k: v for k, v in result.items() if k != "prd"}, indent=2))

"""Create and populate the Google Sheet project tracker (see references/sheet_schema.md)."""

import os
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

PROJECT_OVERVIEW_HEADERS = ["Field", "Value"]
EPICS_HEADERS = ["Epic ID", "Epic Name", "Description"]
USER_STORIES_HEADERS = ["Story ID", "Epic", "Story", "Priority", "Story Points"]
RISKS_HEADERS = ["Risk", "Impact", "Mitigation"]


def _get_credentials():
    key_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    return service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES
    )


def create_tracker(
    drive_folder_id: str,
    project_overview: dict,
    epics: List[dict],
    user_stories: List[dict],
    risks: List[dict],
    share_with: List[str],
) -> str:
    """Create spreadsheet, create worksheets, populate rows, share with team, return spreadsheet URL."""
    credentials = _get_credentials()
    sheets = build("sheets", "v4", credentials=credentials)
    drive = build("drive", "v3", credentials=credentials)

    project_name = project_overview.get("Project Name", "Untitled Project")

    spreadsheet = (
        sheets.spreadsheets()
        .create(
            body={
                "properties": {"title": f"{project_name} — Project Tracker"},
                "sheets": [
                    {"properties": {"title": "Project Overview"}},
                    {"properties": {"title": "Epics"}},
                    {"properties": {"title": "User Stories"}},
                    {"properties": {"title": "Risks"}},
                ],
            },
            fields="spreadsheetId,spreadsheetUrl",
        )
        .execute()
    )
    spreadsheet_id = spreadsheet["spreadsheetId"]

    file = drive.files().get(fileId=spreadsheet_id, fields="parents").execute()
    previous_parents = ",".join(file.get("parents", []))
    drive.files().update(
        fileId=spreadsheet_id,
        addParents=drive_folder_id,
        removeParents=previous_parents,
        fields="id,parents",
    ).execute()

    overview_rows = [PROJECT_OVERVIEW_HEADERS] + [
        [field, value] for field, value in project_overview.items()
    ]
    epic_rows = [EPICS_HEADERS] + [
        [epic["epic_id"], epic["name"], epic["description"]] for epic in epics
    ]
    story_rows = [USER_STORIES_HEADERS] + [
        [
            story["story_id"],
            story["epic_id"],
            story["story"],
            story.get("priority", ""),
            story.get("story_points", ""),
        ]
        for story in user_stories
    ]
    risk_rows = [RISKS_HEADERS] + [
        [risk["risk"], risk["impact"], risk["mitigation"]] for risk in risks
    ]

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "RAW",
            "data": [
                {"range": "Project Overview!A1", "values": overview_rows},
                {"range": "Epics!A1", "values": epic_rows},
                {"range": "User Stories!A1", "values": story_rows},
                {"range": "Risks!A1", "values": risk_rows},
            ],
        },
    ).execute()

    for email in share_with:
        drive.permissions().create(
            fileId=spreadsheet_id,
            body={"type": "user", "role": "writer", "emailAddress": email},
            fields="id",
            sendNotificationEmail=False,
        ).execute()

    return spreadsheet["spreadsheetUrl"]

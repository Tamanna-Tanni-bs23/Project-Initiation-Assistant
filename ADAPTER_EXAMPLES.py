"""
Example LLM and Tracker Adapters for Project Initiation Assistant

These demonstrate how to implement adapters for new providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
import json
import os


# ============================================================================
# LLM ADAPTER INTERFACE
# ============================================================================

class LLMAdapter(ABC):
    """Base class for LLM provider adapters"""

    @abstractmethod
    def call(self, system_prompt: str, user_input: str, output_schema: Type) -> Any:
        """
        Call LLM and return validated structured output.

        Args:
            system_prompt: System instructions
            user_input: User message
            output_schema: Pydantic model class to validate against

        Returns:
            Instance of output_schema with LLM response data
        """
        pass


# ============================================================================
# LLM ADAPTER IMPLEMENTATIONS
# ============================================================================

class ClaudeAdapter(LLMAdapter):
    """Anthropic Claude adapter"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-4-8", **kwargs):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.temperature = kwargs.get("temperature", 1)
        self.max_tokens = kwargs.get("max_tokens", 4096)

    def call(self, system_prompt: str, user_input: str, output_schema: Type) -> Any:
        """Call Claude API with structured output via messages.parse()"""
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_key)

        response = client.messages.parse(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}],
            output_format=output_schema  # Pydantic model
        )

        return response.content[0].parsed


class OpenAIAdapter(LLMAdapter):
    """OpenAI GPT adapter"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo", **kwargs):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 4096)

    def call(self, system_prompt: str, user_input: str, output_schema: Type) -> Any:
        """Call OpenAI API with JSON schema"""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        # Convert Pydantic schema to JSON Schema
        json_schema = {
            "name": output_schema.__name__,
            "schema": output_schema.model_json_schema(),
            "strict": True
        }

        response = client.beta.messages.parse(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_input}],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema
            }
        )

        parsed_json = json.loads(response.content[0].text)
        return output_schema(**parsed_json)


class GeminiAdapter(LLMAdapter):
    """Google Gemini adapter"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash", **kwargs):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model = model
        self.temperature = kwargs.get("temperature", 0.7)

    def call(self, system_prompt: str, user_input: str, output_schema: Type) -> Any:
        """Call Google Gemini API"""
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(
            self.model,
            generation_config={
                "temperature": self.temperature,
                "response_mime_type": "application/json",
                "response_schema": output_schema.model_json_schema()
            }
        )

        response = model.generate_content(f"{system_prompt}\n\n{user_input}")
        parsed_json = json.loads(response.text)
        return output_schema(**parsed_json)


class LocalLLMAdapter(LLMAdapter):
    """Local LLM adapter (Ollama, LM Studio, custom endpoint)"""

    def __init__(self, endpoint: Optional[str] = None, model: str = "llama2", **kwargs):
        self.endpoint = endpoint or os.environ.get("LOCAL_LLM_ENDPOINT", "http://localhost:11434")
        self.model = model or os.environ.get("LOCAL_LLM_MODEL", "llama2")

    def call(self, system_prompt: str, user_input: str, output_schema: Type) -> Any:
        """Call local LLM endpoint (Ollama-compatible)"""
        import requests

        # Build Ollama-compatible request
        prompt = f"{system_prompt}\n\nRespond in valid JSON only.\n\n{user_input}"

        response = requests.post(
            f"{self.endpoint}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=300
        )
        response.raise_for_status()

        result = response.json()
        output_text = result.get("response", "")

        # Extract JSON from response (may contain extra text)
        try:
            parsed_json = json.loads(output_text)
        except json.JSONDecodeError:
            # Try to find JSON in the output
            start = output_text.find("{")
            end = output_text.rfind("}") + 1
            parsed_json = json.loads(output_text[start:end])

        return output_schema(**parsed_json)


class CustomAPIAdapter(LLMAdapter):
    """Custom HTTP API adapter"""

    def __init__(self, endpoint: str, auth_header: Optional[str] = None, **kwargs):
        self.endpoint = endpoint
        self.auth_header = auth_header or os.environ.get("CUSTOM_API_AUTH")

    def call(self, system_prompt: str, user_input: str, output_schema: Type) -> Any:
        """Call custom HTTP API"""
        import requests

        headers = {"Content-Type": "application/json"}
        if self.auth_header:
            headers["Authorization"] = self.auth_header

        response = requests.post(
            self.endpoint,
            json={
                "system": system_prompt,
                "user": user_input,
                "schema": output_schema.model_json_schema()
            },
            headers=headers
        )
        response.raise_for_status()

        parsed_json = response.json()
        return output_schema(**parsed_json)


# ============================================================================
# TRACKER ADAPTER INTERFACE
# ============================================================================

class TrackerAdapter(ABC):
    """Base class for project tracker adapters"""

    @abstractmethod
    def create_tracker(self, name: str, share_with: List[str]) -> str:
        """Create tracker and return public URL"""
        pass

    @abstractmethod
    def add_project_overview(self, project_overview: Dict[str, Any]) -> None:
        """Add Project Overview data"""
        pass

    @abstractmethod
    def add_epics(self, epics: List[Dict[str, Any]]) -> None:
        """Add Epic rows"""
        pass

    @abstractmethod
    def add_user_stories(self, stories: List[Dict[str, Any]]) -> None:
        """Add User Story rows"""
        pass

    @abstractmethod
    def add_risks(self, risks: List[Dict[str, Any]]) -> None:
        """Add Risk rows"""
        pass

    @abstractmethod
    def get_url(self) -> str:
        """Return public tracker URL"""
        pass


# ============================================================================
# TRACKER ADAPTER IMPLEMENTATIONS
# ============================================================================

class GoogleSheetsAdapter(TrackerAdapter):
    """Google Sheets adapter (original implementation)"""

    def __init__(self, folder_id: str, credentials_file: Optional[str] = None):
        self.folder_id = folder_id
        self.credentials_file = credentials_file or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        self.spreadsheet_id = None
        self.spreadsheet_url = None

    def create_tracker(self, name: str, share_with: List[str]) -> str:
        """Create Google Sheet"""
        from google.oauth2.service_account import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        # Authenticate
        credentials = Credentials.from_service_account_file(self.credentials_file)
        sheets_service = build("sheets", "v4", credentials=credentials)
        drive_service = build("drive", "v3", credentials=credentials)

        # Create spreadsheet
        spreadsheet = sheets_service.spreadsheets().create(
            body={"properties": {"title": name}}
        ).execute()

        self.spreadsheet_id = spreadsheet["spreadsheetId"]
        self.spreadsheet_url = spreadsheet["spreadsheetUrl"]

        # Move to folder
        drive_service.files().update(
            fileId=self.spreadsheet_id,
            addParents=self.folder_id,
            fields="id, parents"
        ).execute()

        # Share with emails
        for email in share_with:
            drive_service.permissions().create(
                fileId=self.spreadsheet_id,
                body={"type": "user", "role": "editor", "emailAddress": email}
            ).execute()

        return self.spreadsheet_url

    def add_project_overview(self, project_overview: Dict[str, Any]) -> None:
        """Add Project Overview sheet"""
        from googleapiclient.discovery import build

        sheets_service = build("sheets", "v4")

        # Create sheet
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "requests": [{
                    "addSheet": {"properties": {"title": "Project Overview"}}
                }]
            }
        ).execute()

        # Write data
        values = [
            ["Project Name", "Client", "Objective", "Priority"],
            [
                project_overview.get("project_name", ""),
                project_overview.get("client", ""),
                project_overview.get("objective", ""),
                project_overview.get("priority", "")
            ]
        ]

        sheets_service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range="'Project Overview'!A1:D2",
            valueInputOption="RAW",
            body={"values": values}
        ).execute()

    def add_epics(self, epics: List[Dict[str, Any]]) -> None:
        """Add Epics sheet"""
        # Similar implementation: create sheet, write rows
        pass

    def add_user_stories(self, stories: List[Dict[str, Any]]) -> None:
        """Add User Stories sheet"""
        pass

    def add_risks(self, risks: List[Dict[str, Any]]) -> None:
        """Add Risks sheet"""
        pass

    def get_url(self) -> str:
        return self.spreadsheet_url


class JiraAdapter(TrackerAdapter):
    """Atlassian Jira adapter"""

    def __init__(self, domain: str, project_key: str, email: str, api_token: str):
        self.domain = domain  # company.atlassian.net
        self.project_key = project_key
        self.email = email
        self.api_token = api_token
        self.project_id = None
        self.base_url = f"https://{domain}"

    def create_tracker(self, name: str, share_with: List[str]) -> str:
        """Create Jira project (minimal: just get project)"""
        import requests

        # In real use, would create a new project
        # For this example, we assume project already exists
        auth = (self.email, self.api_token)

        response = requests.get(
            f"{self.base_url}/rest/api/3/project/{self.project_key}",
            auth=auth
        )
        response.raise_for_status()

        self.project_id = response.json()["id"]
        return f"{self.base_url}/browse/{self.project_key}"

    def add_project_overview(self, project_overview: Dict[str, Any]) -> None:
        """Create Jira summary issue"""
        import requests

        auth = (self.email, self.api_token)

        requests.post(
            f"{self.base_url}/rest/api/3/issues",
            auth=auth,
            json={
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": f"Project: {project_overview.get('project_name', '')}",
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{
                            "type": "paragraph",
                            "content": [{
                                "type": "text",
                                "text": json.dumps(project_overview, indent=2)
                            }]
                        }]
                    },
                    "issuetype": {"name": "Project"}
                }
            }
        ).execute()

    def add_epics(self, epics: List[Dict[str, Any]]) -> None:
        """Create Epic issues"""
        import requests

        auth = (self.email, self.api_token)

        for epic in epics:
            requests.post(
                f"{self.base_url}/rest/api/3/issues",
                auth=auth,
                json={
                    "fields": {
                        "project": {"key": self.project_key},
                        "summary": epic.get("name", ""),
                        "description": epic.get("description", ""),
                        "issuetype": {"name": "Epic"}
                    }
                }
            ).execute()

    def add_user_stories(self, stories: List[Dict[str, Any]]) -> None:
        """Create Story issues"""
        import requests

        auth = (self.email, self.api_token)

        for story in stories:
            requests.post(
                f"{self.base_url}/rest/api/3/issues",
                auth=auth,
                json={
                    "fields": {
                        "project": {"key": self.project_key},
                        "summary": story.get("story", ""),
                        "description": story.get("acceptance_criteria", ""),
                        "issuetype": {"name": "Story"},
                        "customfield_10000": story.get("story_points", 0)  # Story Points
                    }
                }
            ).execute()

    def add_risks(self, risks: List[Dict[str, Any]]) -> None:
        """Create Risk issues"""
        import requests

        auth = (self.email, self.api_token)

        for risk in risks:
            requests.post(
                f"{self.base_url}/rest/api/3/issues",
                auth=auth,
                json={
                    "fields": {
                        "project": {"key": self.project_key},
                        "summary": f"Risk: {risk.get('risk', '')}",
                        "description": f"Impact: {risk.get('impact', '')}\n\nMitigation: {risk.get('mitigation', '')}",
                        "issuetype": {"name": "Bug"}
                    }
                }
            ).execute()

    def get_url(self) -> str:
        return f"{self.base_url}/browse/{self.project_key}"


class LinearAdapter(TrackerAdapter):
    """Linear.app adapter"""

    def __init__(self, team_id: str, api_key: str):
        self.team_id = team_id
        self.api_key = api_key
        self.project_url = None

    def create_tracker(self, name: str, share_with: List[str]) -> str:
        """Create Linear project"""
        import requests

        query = """
            mutation {
                projectCreate(input: {
                    teamId: "%s"
                    name: "%s"
                }) {
                    project {
                        id
                        slug
                        url
                    }
                }
            }
        """ % (self.team_id, name)

        response = requests.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"query": query}
        )
        response.raise_for_status()

        self.project_url = response.json()["data"]["projectCreate"]["project"]["url"]
        return self.project_url

    def add_project_overview(self, project_overview: Dict[str, Any]) -> None:
        """Add overview as comment"""
        pass

    def add_epics(self, epics: List[Dict[str, Any]]) -> None:
        """Create Linear issues for epics"""
        pass

    def add_user_stories(self, stories: List[Dict[str, Any]]) -> None:
        """Create Linear issues for stories"""
        pass

    def add_risks(self, risks: List[Dict[str, Any]]) -> None:
        """Create Linear issues for risks"""
        pass

    def get_url(self) -> str:
        return self.project_url


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_llm_adapter(provider: str, **kwargs) -> LLMAdapter:
    """Factory function to create LLM adapter by provider name"""
    adapters = {
        "claude": ClaudeAdapter,
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
        "local": LocalLLMAdapter,
        "custom": CustomAPIAdapter
    }

    adapter_class = adapters.get(provider.lower())
    if not adapter_class:
        raise ValueError(f"Unknown LLM provider: {provider}")

    return adapter_class(**kwargs)


def create_tracker_adapter(platform: str, **kwargs) -> TrackerAdapter:
    """Factory function to create tracker adapter by platform name"""
    adapters = {
        "sheets": GoogleSheetsAdapter,
        "jira": JiraAdapter,
        "linear": LinearAdapter,
    }

    adapter_class = adapters.get(platform.lower())
    if not adapter_class:
        raise ValueError(f"Unknown tracker platform: {platform}")

    return adapter_class(**kwargs)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Claude + Sheets
    llm = create_llm_adapter("claude")
    tracker = create_tracker_adapter("sheets", folder_id="folder_123")

    # Example 2: OpenAI + Jira
    llm = create_llm_adapter("openai", model="gpt-4-turbo")
    tracker = create_tracker_adapter("jira", domain="company.atlassian.net",
                                      project_key="PROJ", email="bot@company.com",
                                      api_token="ATATT...")

    # Example 3: Gemini + Linear
    llm = create_llm_adapter("gemini", model="gemini-2.0-flash")
    tracker = create_tracker_adapter("linear", team_id="team_123",
                                      api_key="lin_api_...")

    # Example 4: Local LLM + Airtable (would need AirtableAdapter)
    llm = create_llm_adapter("local", endpoint="http://localhost:11434",
                              model="llama2")
    # tracker = create_tracker_adapter("airtable", ...)

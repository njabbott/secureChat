"""Jira service for creating tickets"""

import logging
from atlassian import Jira

from ..config import settings

logger = logging.getLogger(__name__)


class JiraService:
    """Service for creating Jira tickets via the Atlassian Cloud API"""

    def __init__(self):
        self.jira = Jira(
            url=settings.confluence_base_url,
            username=settings.confluence_email,
            password=settings.confluence_api_key,
            cloud=True,
        )
        self.project_key = settings.jira_project_key
        logger.info(f"Initialized JiraService for project {self.project_key}")

    def create_ticket(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
    ) -> dict:
        """
        Create a Jira issue and return its key and URL.

        Jira Cloud requires Atlassian Document Format (ADF) for the description field.
        """
        issue = self.jira.issue_create(
            fields={
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
            }
        )

        key = issue["key"]
        url = f"{settings.confluence_base_url}/browse/{key}"
        logger.info(f"Created Jira ticket {key} ({issue_type}): {summary}")

        return {
            "key": key,
            "url": url,
            "summary": summary,
            "issue_type": issue_type,
        }

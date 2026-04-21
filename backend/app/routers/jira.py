"""Jira endpoints"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..models.chat import JiraTicket
from ..services import JiraService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jira", tags=["jira"])

# Injected by main.py
jira_service: JiraService = None


class CreateTicketRequest(BaseModel):
    summary: str
    description: str
    issue_type: str = "Task"
    priority: str = "Medium"


@router.get("/issue-types")
async def list_issue_types():
    """List valid issue types for the configured Jira project."""
    if not jira_service:
        raise HTTPException(status_code=500, detail="Jira service not initialized")
    try:
        meta = jira_service.jira.get(f"rest/api/3/project/{jira_service.project_key}/statuses")
        types = {t["name"] for issue_type in meta for t in [issue_type]}
        return [{"name": t["name"]} for t in meta]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects")
async def list_projects():
    """List available Jira projects (useful for finding the correct project key)."""
    if not jira_service:
        raise HTTPException(status_code=500, detail="Jira service not initialized")
    try:
        projects = jira_service.jira.projects()
        return [{"key": p["key"], "name": p["name"]} for p in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-ticket", response_model=JiraTicket)
async def create_ticket(request: CreateTicketRequest):
    """
    Create a Jira ticket directly (used by the frontend offer-button flow).
    """
    if not jira_service:
        raise HTTPException(status_code=500, detail="Jira service not initialized")

    if request.issue_type not in ("Task", "Epic"):
        raise HTTPException(status_code=400, detail="issue_type must be Task, Bug, or Question")

    if request.priority not in ("Low", "Medium", "High"):
        raise HTTPException(status_code=400, detail="priority must be Low, Medium, or High")

    try:
        ticket_data = jira_service.create_ticket(
            summary=request.summary,
            description=request.description,
            issue_type=request.issue_type,
            priority=request.priority,
        )
        return JiraTicket(**ticket_data)
    except Exception as e:
        logger.error(f"Error creating Jira ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create Jira ticket: {str(e)}")

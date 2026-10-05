from __future__ import annotations

import httpx
from mcp.server import MCPServer

from src.config import get_settings

mcp = MCPServer("jira-integration")


def auth() -> tuple[str, str]:
    settings = get_settings()
    if not settings.jira_email or not settings.jira_api_token:
        raise RuntimeError("JIRA_EMAIL and JIRA_API_TOKEN are required")
    return settings.jira_email, settings.jira_api_token


async def jira(method: str, path: str, *, json: dict | None = None, params: dict | None = None):
    settings = get_settings()
    if not settings.jira_base_url:
        raise RuntimeError("JIRA_BASE_URL is required")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            method,
            f"{settings.jira_base_url.rstrip('/')}{path}",
            auth=auth(),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json() if response.content else {"success": True}


@mcp.tool()
async def create_issue(project: str, issue_type: str, data: dict) -> dict:
    """Create a Jira issue."""
    fields = {"project": {"key": project}, "issuetype": {"name": issue_type}, **data}
    return await jira("POST", "/rest/api/3/issue", json={"fields": fields})


@mcp.tool()
async def get_issue(key: str) -> dict:
    """Get a Jira issue by key."""
    return await jira("GET", f"/rest/api/3/issue/{key}")


@mcp.tool()
async def list_issues(project: str, filter: str = "") -> list:
    """Search Jira issues using JQL."""
    jql = f'project = "{project}"'
    if filter:
        jql += f" AND ({filter})"
    data = await jira("GET", "/rest/api/3/search/jql", params={"jql": jql, "maxResults": 50})
    return data.get("issues", [])


@mcp.tool()
async def update_issue(key: str, status: str, fields: dict) -> dict:
    """Update Jira issue fields."""
    return await jira("PUT", f"/rest/api/3/issue/{key}", json={"fields": fields})


@mcp.tool()
async def add_comment(key: str, message: str) -> dict:
    """Add a comment to a Jira issue."""
    return await jira(
        "POST",
        f"/rest/api/3/issue/{key}/comment",
        json={"body": {"type": "doc", "version": 1, "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": message}]}
        ]}},
    )


@mcp.tool()
async def change_status(key: str, new_status: str) -> dict:
    """Transition a Jira issue to a status by looking up its transition id."""
    transitions = await jira("GET", f"/rest/api/3/issue/{key}/transitions")
    match = next(
        (t for t in transitions.get("transitions", [])
         if t.get("to", {}).get("name", "").lower() == new_status.lower()),
        None,
    )
    if not match:
        raise ValueError(f"No transition to status {new_status!r}")
    return await jira(
        "POST",
        f"/rest/api/3/issue/{key}/transitions",
        json={"transition": {"id": match["id"]}},
    )


@mcp.tool()
async def link_issues(key1: str, key2: str, type: str) -> dict:
    """Link two Jira issues."""
    return await jira(
        "POST", "/rest/api/3/issueLink",
        json={"type": {"name": type}, "inwardIssue": {"key": key1}, "outwardIssue": {"key": key2}},
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8104)

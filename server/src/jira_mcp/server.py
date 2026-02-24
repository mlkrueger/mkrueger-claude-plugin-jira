"""MCP server exposing read-only Jira Cloud API operations as tools."""

import os

import requests
from fastmcp import FastMCP

mcp = FastMCP("jira")


def _base_url() -> str:
    url = os.environ.get("JIRA_URL")
    if not url:
        raise RuntimeError("JIRA_URL environment variable is not set")
    url = url.rstrip("/")
    if not url.startswith("https://") and not url.startswith("http://"):
        url = f"https://{url}"
    return url


def _session() -> requests.Session:
    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")
    if not email or not token:
        raise RuntimeError(
            "JIRA_EMAIL and JIRA_API_TOKEN environment variables must be set"
        )
    s = requests.Session()
    s.auth = (email, token)
    s.headers.update({"Accept": "application/json"})
    return s


def _get(path: str, params: dict | None = None) -> dict | list:
    resp = _session().get(f"{_base_url()}{path}", params=params)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Issue Search & Details
# ---------------------------------------------------------------------------


@mcp.tool()
def search_issues(
    jql: str,
    fields: str | None = None,
    max_results: int = 50,
    start_at: int = 0,
) -> dict:
    """Search issues using JQL. Returns paginated results.

    Args:
        jql: JQL query string (e.g. 'project = PROJ AND status = "In Progress"')
        fields: Comma-separated field names to return (default: all navigable fields). Use 'key,summary,status,assignee,priority' for compact results.
        max_results: Maximum results to return (1-100, default 50)
        start_at: Index of first result for pagination (default 0)
    """
    params = {"jql": jql, "maxResults": max_results, "startAt": start_at}
    if fields:
        params["fields"] = fields
    return _get("/rest/api/3/search/jql", params=params)


@mcp.tool()
def get_issue(
    issue_key: str,
    fields: str | None = None,
    expand: str | None = None,
) -> dict:
    """Get full details of a single issue.

    Args:
        issue_key: Issue key (e.g. 'PROJ-123')
        fields: Comma-separated field names to return (default: all)
        expand: Comma-separated expansions (e.g. 'changelog,renderedFields')
    """
    params = {}
    if fields:
        params["fields"] = fields
    if expand:
        params["expand"] = expand
    return _get(f"/rest/api/3/issue/{issue_key}", params=params)


@mcp.tool()
def get_issue_comments(
    issue_key: str,
    max_results: int = 50,
    start_at: int = 0,
    order_by: str = "-created",
) -> dict:
    """Get comments on an issue. Comments often contain blockers, decisions, and context.

    Args:
        issue_key: Issue key (e.g. 'PROJ-123')
        max_results: Maximum comments to return (default 50)
        start_at: Index of first result for pagination (default 0)
        order_by: Sort order ('-created' for newest first, '+created' for oldest first)
    """
    params = {
        "maxResults": max_results,
        "startAt": start_at,
        "orderBy": order_by,
    }
    return _get(f"/rest/api/3/issue/{issue_key}/comment", params=params)


@mcp.tool()
def get_issue_changelog(
    issue_key: str,
    max_results: int = 50,
    start_at: int = 0,
) -> dict:
    """Get the changelog for an issue. Shows status transitions, reassignments, and field changes with timestamps.

    Args:
        issue_key: Issue key (e.g. 'PROJ-123')
        max_results: Maximum entries to return (default 50)
        start_at: Index of first result for pagination (default 0)
    """
    params = {"maxResults": max_results, "startAt": start_at}
    return _get(f"/rest/api/3/issue/{issue_key}/changelog", params=params)


@mcp.tool()
def get_issue_transitions(issue_key: str) -> dict:
    """Get available workflow transitions for an issue. Shows what status changes are possible.

    Args:
        issue_key: Issue key (e.g. 'PROJ-123')
    """
    return _get(f"/rest/api/3/issue/{issue_key}/transitions")


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


@mcp.tool()
def list_projects(
    query: str | None = None,
    max_results: int = 50,
    start_at: int = 0,
) -> dict:
    """List projects visible to the current user.

    Args:
        query: Filter projects by name (case-insensitive substring match)
        max_results: Maximum results to return (default 50)
        start_at: Index of first result for pagination (default 0)
    """
    params = {"maxResults": max_results, "startAt": start_at}
    if query:
        params["query"] = query
    return _get("/rest/api/3/project/search", params=params)


# ---------------------------------------------------------------------------
# Agile: Boards & Sprints
# ---------------------------------------------------------------------------


@mcp.tool()
def list_boards(
    project_key_or_id: str | None = None,
    board_type: str | None = None,
    name: str | None = None,
    max_results: int = 50,
    start_at: int = 0,
) -> dict:
    """List agile boards. Filter by project, type, or name.

    Args:
        project_key_or_id: Filter boards by project key or ID
        board_type: Filter by board type ('scrum', 'kanban', 'simple')
        name: Filter boards by name (substring match)
        max_results: Maximum results to return (default 50)
        start_at: Index of first result for pagination (default 0)
    """
    params = {"maxResults": max_results, "startAt": start_at}
    if project_key_or_id:
        params["projectKeyOrId"] = project_key_or_id
    if board_type:
        params["type"] = board_type
    if name:
        params["name"] = name
    return _get("/rest/agile/1.0/board", params=params)


@mcp.tool()
def list_sprints(
    board_id: int,
    state: str | None = None,
    max_results: int = 50,
    start_at: int = 0,
) -> dict:
    """List sprints for a board.

    Args:
        board_id: The ID of the board
        state: Filter by sprint state ('active', 'closed', 'future'). Comma-separate for multiple.
        max_results: Maximum results to return (default 50)
        start_at: Index of first result for pagination (default 0)
    """
    params = {"maxResults": max_results, "startAt": start_at}
    if state:
        params["state"] = state
    return _get(f"/rest/agile/1.0/board/{board_id}/sprint", params=params)


@mcp.tool()
def get_sprint_issues(
    sprint_id: int,
    fields: str | None = None,
    max_results: int = 50,
    start_at: int = 0,
) -> dict:
    """Get all issues in a sprint.

    Args:
        sprint_id: The ID of the sprint
        fields: Comma-separated field names to return (default: all navigable). Use 'key,summary,status,assignee,priority' for compact results.
        max_results: Maximum results to return (default 50)
        start_at: Index of first result for pagination (default 0)
    """
    params = {"maxResults": max_results, "startAt": start_at}
    if fields:
        params["fields"] = fields
    return _get(f"/rest/agile/1.0/sprint/{sprint_id}/issue", params=params)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@mcp.tool()
def search_users(
    query: str,
    max_results: int = 10,
) -> list:
    """Search for Jira users by name or email. Use this to resolve display names to account IDs for JQL queries.

    Args:
        query: Search string (matches name, email, or username)
        max_results: Maximum results to return (default 10)
    """
    params = {"query": query, "maxResults": max_results}
    return _get("/rest/api/3/user/search", params=params)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()

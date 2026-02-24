# Jira Plugin

Read-only Jira Cloud integration for querying issues, sprints, and team activity from Claude Code.

## Setup

1. Create an API token at https://id.atlassian.com/manage-profile/security/api-tokens

2. Set environment variables:
   ```bash
   export JIRA_URL="https://yourcompany.atlassian.net"
   export JIRA_EMAIL="you@example.com"
   export JIRA_API_TOKEN="your-api-token"
   ```

3. Install dependencies:
   ```bash
   cd jira/server && uv sync
   ```

4. Use with Claude Code:
   ```bash
   claude --plugin-dir ./jira
   ```

## Usage

Once loaded, use `/jira` to query your Jira instance:

- `/jira list my projects`
- `/jira show the active sprint`
- `/jira what's assigned to me?`
- `/jira give me a daily brief`
- `/jira who is blocked?`
- `/jira summarize PROJ-123`

## Tools

The plugin exposes 10 read-only MCP tools:

- **Search** - JQL-powered issue search with pagination
- **Issues** - Full details, comments, changelog, transitions
- **Projects** - List and search projects
- **Boards & Sprints** - List boards, sprints, and sprint issues
- **Users** - Search users to resolve names for JQL queries

---
name: jira
description: Query Jira Cloud issues, sprints, and team activity (read-only)
user_invocable: true
activation:
  prefix: /jira
---

# Jira Cloud (Read-Only)

You have access to a set of MCP tools (prefixed `jira_`) that query a Jira Cloud instance. All tools are **read-only** — no issues are created or modified. Use them to answer questions about tickets, sprints, team workload, blockers, and progress.

## Available Tools

### Issue Search & Details
- `jira_search_issues` - Search issues using JQL with pagination (jql, fields, max_results, start_at)
- `jira_get_issue` - Get full issue details (issue_key, fields, expand). Use `expand=changelog` for history.
- `jira_get_issue_comments` - Get comments on an issue (issue_key, max_results, start_at, order_by)
- `jira_get_issue_changelog` - Get status transitions, reassignments, field changes with timestamps (issue_key, max_results, start_at)
- `jira_get_issue_transitions` - Get available workflow transitions for an issue (issue_key)

### Projects
- `jira_list_projects` - List projects visible to the user (query, max_results, start_at)

### Agile: Boards & Sprints
- `jira_list_boards` - List agile boards, filter by project/type/name (project_key_or_id, board_type, name, max_results, start_at)
- `jira_list_sprints` - List sprints for a board (board_id, state, max_results, start_at). State: 'active', 'closed', 'future'.
- `jira_get_sprint_issues` - Get all issues in a sprint (sprint_id, fields, max_results, start_at)

### Users
- `jira_search_users` - Search users by name or email to resolve account IDs for JQL (query, max_results)

## JQL Quick Reference

JQL (Jira Query Language) is the primary way to query issues. Pass JQL strings to `jira_search_issues`.

### Common Queries
```
# Issues assigned to someone
assignee = "accountId" AND status != Done

# Current sprint issues
sprint in openSprints()

# Blockers / high priority
priority in (Highest, High) AND status != Done

# Recently updated
updated >= -1d ORDER BY updated DESC

# Status changes today (use changelog tool for details)
status CHANGED DURING (startOfDay(), now())

# Issues created this week
created >= startOfWeek()

# Unassigned issues in a project
project = PROJ AND assignee is EMPTY AND status != Done

# Epics
issuetype = Epic AND project = PROJ

# Subtasks of an issue
parent = PROJ-123

# Issues with a specific label
labels = "backend" AND project = PROJ
```

### JQL Functions
- `openSprints()` / `closedSprints()` / `futureSprints()` - Sprint filters
- `startOfDay()` / `endOfDay()` / `startOfWeek()` / `startOfMonth()` - Time functions
- `currentUser()` - The authenticated user
- `membersOf("group")` - Users in a group

### JQL Operators
- `=`, `!=`, `>`, `>=`, `<`, `<=` - Comparison
- `in`, `not in` - List membership
- `~` - Contains text (for summary, description)
- `is EMPTY` / `is not EMPTY` - Null checks
- `CHANGED` / `CHANGED DURING` - Field change history
- `WAS` / `WAS NOT` / `WAS IN` - Historical values
- `ORDER BY field ASC|DESC` - Sorting

## Workflow Guidelines

1. **Resolve users first.** When a user asks about a person by name, use `jira_search_users` to find their `accountId`, then use it in JQL (`assignee = "accountId"`).

2. **Build sprint context step by step.** To analyze a sprint:
   - `jira_list_boards` to find the board
   - `jira_list_sprints` with `state=active` to find the current sprint
   - `jira_get_sprint_issues` to get the issues
   - Group and summarize the results

3. **Use changelog for timing.** To understand how long something was in a status, or when it transitioned, use `jira_get_issue_changelog`. The changelog shows `from` → `to` values with timestamps.

4. **Use compact fields for listings.** When listing many issues, pass `fields=key,summary,status,assignee,priority` to reduce response size. Fetch full details only when needed.

5. **Paginate large results.** All list tools support `start_at` and `max_results`. If `total` exceeds your page size, make additional requests.

6. **Present results clearly.** When showing issues, format as a table or list with key, summary, status, assignee, and priority. Group by status or assignee when relevant.

7. **Combine tools for complex questions.** This plugin provides composable primitives. For example, "who is blocked?" requires searching for blocked issues, then checking comments/changelog for context.

## Common Scenarios

### Daily Brief
1. Search for issues updated since yesterday: `updated >= -1d ORDER BY updated DESC`
2. Search for newly created issues: `created >= -1d`
3. Search for status changes: `status CHANGED DURING (startOfDay(-1d), now())`
4. Summarize: new items, started work, completed, blocked

### Sprint Review
1. Find the board and active sprint
2. Get all sprint issues
3. Group by status (Done, In Progress, To Do)
4. Check for issues that changed status during the sprint via changelog

### Team Workload
1. Search for in-progress issues grouped by assignee: `status = "In Progress" AND project = PROJ`
2. Count issues per person
3. Flag anyone with unusually high or zero WIP

### Issue Deep Dive
1. `jira_get_issue` with full fields
2. `jira_get_issue_comments` for discussion context
3. `jira_get_issue_changelog` for status history and timing
4. `jira_get_issue_transitions` to see what can happen next

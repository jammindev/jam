# Project

## Tickets
- Tracker: GitHub Issues
- Read a ticket: `gh issue view {id} --json title,body,comments --jq '.title, .body, (.comments[] | .author.login + ": " + .body)'`
- List my tickets: `gh issue list --assignee @me`

## Code
- Base branch: main
- Ticket branch: {id}-{slug}
- Tests: `make test`
- Lint: `make lint`
- Run: `make dev`
- Open a PR: `gh pr create --base main`
- **PR state command**: `gh pr view "$JAM_PR" --json state --jq .state`
- **PR size command**: `gh pr view "$JAM_PR" --json additions,deletions,changedFiles --jq '"\(.additions) \(.deletions) \(.changedFiles)"'`

## Sensitive (one extra review pass)
- Payment calculations, accounts and permissions, personal data, migrations

## Review: project checks

## Links
- Agent instructions: CLAUDE.md
- Specs: docs/specs/
- Lint config: pyproject.toml ([tool.ruff])
- PR template: .github/pull_request_template.md

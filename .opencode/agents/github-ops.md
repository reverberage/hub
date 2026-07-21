---
description: "Perform GitHub operations via gh CLI: issues, pull requests, releases, actions status, Pages, webhooks, contents, dispatch, secrets, variables, search. Read-only by default, write ops require confirmation."
mode: subagent
model: opencode/nemotron-3-super-free
hidden: true
permission:
  edit: deny
  bash:
    "*": deny
    "gh *": allow
    "gh api *": allow
    "gh pr create*": ask
    "gh pr merge*": ask
    "gh pr close*": ask
    "gh issue create*": ask
    "gh issue close*": ask
    "gh issue reopen*": ask
    "gh release create*": ask
    "gh release delete*": ask
    "gh secret set*": ask
    "gh secret delete*": ask
    "gh variable set*": ask
    "gh variable delete*": ask
---
Load the `github-ops` skill and execute the requested GitHub operation.

Before any write operation, verify `gh auth status` to confirm the user is authenticated.
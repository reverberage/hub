# SDD Spec: github-ops-upgrade

**Change ID**: `github-ops-upgrade` | **Phase**: 3 — Spec | **Date**: 2026-07-21

---

## 1. Goals

1. **Expand github-ops skill to cover all `gh` CLI capabilities**: The current SKILL.md covers only `gh issue`, `gh pr`, `gh release`, and `gh run`. Expand to cover the full `gh` command tree (43 top-level commands) with emphasis on the most useful operations for satellite repo management.

2. **Add `gh api` workflows**: Document `gh api` as the universal escape hatch for any REST/GraphQL operation not covered by a native `gh` subcommand. Include practical patterns for: Pages, webhooks, contents CRUD, dispatch events, repo settings, secrets, variables.

3. **Document wiki push pattern**: Wikis have zero `gh` subcommands. Document the correct approach: clone wiki repo, add `_Footer.md`/`_Sidebar.md`, commit, push. Note this requires orchestrator or git-ops execution (github-ops agent has `edit: deny`).

4. **Update agent permissions**: Expand github-ops agent bash permissions to allow `gh api *` in addition to `gh *`.

5. **Update orchestrator dispatch rules**: Add dispatch rules for new github-ops capabilities in `n3rverberage.md`.

## 2. Non-Goals

| Item | Reason |
|------|--------|
| Creating a new `github-api` agent | Approach A chosen — expand existing, don't split |
| Splitting SKILL.md into multiple files | Single file is simpler, ~200 lines is acceptable |
| Automating wiki pushes in scaffold script | Separate change — wiki push is orchestrator-level |
| Adding GitHub Actions workflows | Out of scope — focus on `gh` CLI + `gh api` |
| Supporting GitHub Enterprise Server | Focus on github.com only |

## 3. Acceptance Criteria

Every criterion is binary testable (pass/fail).

### AC-1: SKILL.md covers all `gh` native subcommands
**Verify**: Read SKILL.md and confirm it documents workflows for: `gh issue`, `gh pr`, `gh release`, `gh run`, `gh repo`, `gh gist`, `gh secret`, `gh variable`, `gh workflow`, `gh search`, `gh auth`, `gh api`.
**Pass**: All 12 command groups documented with at least one workflow each. **Fail**: Any group missing.

### AC-2: SKILL.md documents `gh api` as universal escape hatch
**Verify**: SKILL.md contains a section explaining that `gh api` can call ANY REST endpoint and ANY GraphQL query, with examples of: GET, POST, PATCH, DELETE, pagination, JQ filtering, raw headers.
**Pass**: Section exists with all 6 patterns documented. **Fail**: Section missing or incomplete.

### AC-3: SKILL.md documents wiki push pattern
**Verify**: SKILL.md contains a workflow for wiki push: clone `.wiki.git`, add `_Footer.md`/`_Sidebar.md`, commit, push. Includes auth token pattern: `git remote set-url origin "https://x-access-token:$(gh auth token)@github.com/OWNER/REPO.wiki.git"`.
**Pass**: Workflow exists with auth pattern. **Fail**: Workflow missing or auth pattern missing.

### AC-4: SKILL.md documents Pages deployment via `gh api`
**Verify**: SKILL.md contains a workflow for Pages: `gh api repos/{owner}/{repo}/pages` (GET), `gh api -X POST repos/{owner}/{repo}/pages` (create), `gh api -X PUT repos/{owner}/{repo}/pages` (update), `gh api -X DELETE repos/{owner}/{repo}/pages` (delete), `gh api -X POST repos/{owner}/{repo}/pages/builds` (trigger build).
**Pass**: All 5 Pages operations documented. **Fail**: Any operation missing.

### AC-5: SKILL.md documents webhook CRUD via `gh api`
**Verify**: SKILL.md contains a workflow for webhooks: list (`GET /repos/{owner}/{repo}/hooks`), create (`POST /repos/{owner}/{repo}/hooks`), update (`PATCH /repos/{owner}/{repo}/hooks/{id}`), delete (`DELETE /repos/{owner}/{repo}/hooks/{id}`), ping (`POST /repos/{owner}/{repo}/hooks/{id}/pings`).
**Pass**: All 5 webhook operations documented. **Fail**: Any operation missing.

### AC-6: SKILL.md documents contents CRUD via `gh api`
**Verify**: SKILL.md contains a workflow for contents: get file (`GET /repos/{owner}/{repo}/contents/{path}`), get raw (`-H 'Accept: application/vnd.github.raw+json'`), create file (`PUT`), update file (`PUT` with SHA), delete file (`DELETE` with SHA).
**Pass**: All 5 contents operations documented. **Fail**: Any operation missing.

### AC-7: SKILL.md documents dispatch events via `gh api`
**Verify**: SKILL.md contains a workflow for dispatch: `gh api -X POST repos/{owner}/{repo}/dispatches -f event_type=deploy -f client_payload[environment]=production`.
**Pass**: Dispatch workflow documented. **Fail**: Workflow missing.

### AC-8: SKILL.md documents repo settings via `gh api`
**Verify**: SKILL.md contains a workflow for repo settings: `gh api -X PATCH repos/{owner}/{repo}` with examples for: name, description, private, has_wiki, has_issues, default_branch, allow_squash_merge, delete_branch_on_merge.
**Pass**: At least 8 settings documented. **Fail**: Fewer than 8.

### AC-9: SKILL.md documents secrets and variables via `gh api`
**Verify**: SKILL.md contains workflows for: `gh secret set/list/delete` (native), `gh variable set/list/delete` (native), and `gh api` patterns for org-level secrets/variables.
**Pass**: Both native and API patterns documented. **Fail**: Either missing.

### AC-10: SKILL.md documents search capabilities
**Verify**: SKILL.md contains workflows for: `gh search repos`, `gh search issues`, `gh search prs`, `gh search code`, `gh search commits`.
**Pass**: All 5 search types documented. **Fail**: Any missing.

### AC-11: Agent permissions updated for `gh api`
**Verify**: Read `.opencode/agents/github-ops.md` and confirm bash permissions include `gh api *: allow`.
**Pass**: Permission present. **Fail**: Permission missing.

### AC-12: Orchestrator dispatch rules updated
**Verify**: Read `.opencode/agents/n3rverberage.md` and confirm it references new github-ops capabilities (wiki, Pages, webhooks, contents, dispatch).
**Pass**: At least 3 new capabilities referenced. **Fail**: Fewer than 3.

### AC-13: Destructive operations require confirmation
**Verify**: SKILL.md states that destructive operations (delete webhook, delete file, delete secret, force push) require explicit confirmation from calling agent.
**Pass**: Destructive ops marked as requiring confirmation. **Fail**: Missing safety rules.

### AC-14: Safety rules preserved
**Verify**: SKILL.md retains existing safety rules: `gh auth status` before operations, never close/merge PRs without instruction, validate CI before merge, report rate limits.
**Pass**: All 4 existing rules present. **Fail**: Any rule missing.

### AC-15: SKILL.md includes official doc references
**Verify**: SKILL.md contains a reference table with official doc URLs for: gh CLI manual, REST API index, Pages API, Webhooks API, Contents API, Repos API, Wiki docs.
**Pass**: At least 7 doc URLs in reference table. **Fail**: Fewer than 7.

### AC-16: All workflows are copy-pasteable
**Verify**: Every workflow in SKILL.md includes a complete `gh` or `gh api` command that can be executed as-is (no placeholders like `<your-repo>` — use `OWNER/REPO` pattern).
**Pass**: All commands use OWNER/REPO pattern, no angle-bracket placeholders in commands. **Fail**: Any command has unresolved placeholders.

### AC-17: No breaking changes to existing workflows
**Verify**: Existing workflows (issues, PRs, releases, CI) remain unchanged in SKILL.md. New content is appended, not modifying existing sections.
**Pass**: Existing workflows untouched. **Fail**: Any existing workflow modified.

## 4. Constraints

1. **Backward compatibility**: Existing `github-ops` workflows must not change. New content is appended.

2. **Agent permissions**: The `github-ops` agent must remain `edit: deny`. Wiki push cannot be executed by this agent — it must be documented as requiring orchestrator or git-ops execution.

3. **Single skill file**: SKILL.md remains a single file. No splitting into multiple files.

4. **No new dependencies**: No new npm packages, Python packages, or external tools.

5. **Convention**: All `gh api` commands use `OWNER/REPO` as the placeholder pattern, not `<owner>/<repo>` or `{owner}/{repo}`.

6. **Safety**: All destructive operations (delete, force push, close, merge) require explicit confirmation.

## 5. Out of Scope

| Item | Reason |
|------|--------|
| New `github-api` agent | Approach A chosen — expand existing |
| Splitting SKILL.md into multiple files | Single file is simpler |
| Automating wiki pushes in scaffold script | Separate change |
| GitHub Actions workflow creation | Focus on `gh` CLI + `gh api` |
| GitHub Enterprise Server support | Focus on github.com |
| MCP server for GitHub operations | YAGNI — `gh` CLI is sufficient |

## 6. Traceability Matrix

| AC | Title | Property Tested |
|:--:|-------|----------------|
| AC-1 | All gh subcommands covered | Completeness |
| AC-2 | gh api universal escape hatch | Completeness |
| AC-3 | Wiki push pattern | Completeness |
| AC-4 | Pages deployment | Completeness |
| AC-5 | Webhook CRUD | Completeness |
| AC-6 | Contents CRUD | Completeness |
| AC-7 | Dispatch events | Completeness |
| AC-8 | Repo settings | Completeness |
| AC-9 | Secrets and variables | Completeness |
| AC-10 | Search capabilities | Completeness |
| AC-11 | Agent permissions updated | Configuration |
| AC-12 | Orchestrator dispatch rules | Configuration |
| AC-13 | Destructive ops require confirmation | Safety |
| AC-14 | Safety rules preserved | Safety |
| AC-15 | Official doc references | Documentation |
| AC-16 | Copy-pasteable commands | Usability |
| AC-17 | No breaking changes | Stability |

# SDD Design: github-ops-upgrade

**Change ID**: `github-ops-upgrade` | **Phase**: 4 — Design | **Date**: 2026-07-21

---

## 1. Files Modified

| File | Action | Lines (est.) | Purpose |
|------|--------|:-----------:|---------|
| `.opencode/skills/github-ops/SKILL.md` | MODIFY | 73 → ~220 | Add new workflows for gh api, wiki, Pages, webhooks, contents, dispatch, repo settings, secrets, search |
| `.opencode/agents/github-ops.md` | MODIFY | 22 → 24 | Add `gh api *: allow` permission |
| `.opencode/agents/n3rverberage.md` | MODIFY | 106 → 115 | Add dispatch rules for new github-ops capabilities |

No new files created. Three existing files modified.

## 2. SKILL.md Structure (New Layout)

The SKILL.md grows from 73 lines to ~220 lines. Structure:

```
---
name: github-ops
description: ...
compatibility: opencode
---

# Skill: github-ops

## When to Use                    ← EXPANDED (add new use cases)
## Safety Rules                   ← PRESERVED (existing + new destructive ops)
## Workflow: Creating a Pull Request     ← PRESERVED (unchanged)
## Workflow: Reviewing a Pull Request    ← PRESERVED (unchanged)
## Workflow: Managing Issues             ← PRESERVED (unchanged)
## Workflow: Releases                    ← PRESERVED (unchanged)
## Workflow: CI/CD Checks                ← PRESERVED (unchanged)

## NEW SECTIONS BELOW:

## Workflow: Repository Management       ← NEW
## Workflow: Wiki Push                   ← NEW
## Workflow: GitHub Pages                ← NEW
## Workflow: Webhooks                    ← NEW
## Workflow: Contents API                ← NEW
## Workflow: Dispatch Events             ← NEW
## Workflow: Secrets & Variables         ← NEW
## Workflow: Search                      ← NEW
## The gh api Escape Hatch               ← NEW (reference section)
## Edge Cases                            ← EXPANDED
## Official Documentation References     ← NEW
```

## 3. New Section Details

### 3.1 When to Use (Expanded)

Add to existing list:
- Managing repository settings (`gh repo edit`, `gh api`)
- Deploying GitHub Pages (`gh api /repos/**/pages`)
- Managing webhooks (`gh api /repos/**/hooks`)
- Creating/updating files via API (`gh api /repos/**/contents`)
- Triggering repository dispatch events (`gh api /repos/**/dispatches`)
- Managing secrets and variables (`gh secret`, `gh variable`, `gh api`)
- Searching repositories, issues, PRs, code (`gh search`)
- Pushing wiki content (clone, edit, push — requires git permissions)
- Any GitHub operation not covered by a native `gh` subcommand (`gh api`)

### 3.2 Safety Rules (Expanded)

Add to REJECT list:
- Destructive operations (delete webhook, delete file, delete secret) without explicit confirmation
- Force push to main/master without explicit rationale
- Modifying repo settings without explicit instruction

### 3.3 Wiki Push Workflow (New)

```markdown
## Workflow: Wiki Push

Wiki content (pages, footer, sidebar) lives in a git repo — not accessible via `gh` CLI or REST API.

**Auth setup:**
git remote set-url origin "https://x-access-token:$(gh auth token)@github.com/OWNER/REPO.wiki.git"

**Push _Footer.md:**
1. Clone: git clone https://github.com/OWNER/REPO.wiki.git /tmp/repo.wiki
2. Auth: git -C /tmp/repo.wiki remote set-url origin "https://x-access-token:$(gh auth token)@github.com/OWNER/REPO.wiki.git"
3. Write: echo "Footer content" > /tmp/repo.wiki/_Footer.md
4. Commit: git -C /tmp/repo.wiki add _Footer.md && git -C /tmp/repo.wiki commit -m "Update footer"
5. Push: git -C /tmp/repo.wiki push origin main

**Note:** This operation requires git permissions (clone, add, commit, push).
The github-ops agent has `edit: deny` — wiki push must be executed by the orchestrator or git-ops agent.
```

### 3.4 Pages Workflow (New)

```markdown
## Workflow: GitHub Pages

**Get pages config:**
gh api repos/OWNER/REPO/pages

**Create pages site (from main branch, root):**
gh api -X POST repos/OWNER/REPO/pages -f source[branch]=main -f source[path]=/

**Update pages config (enable HTTPS, set custom domain):**
gh api -X PUT repos/OWNER/REPO/pages -f cname=example.com -f https_enforced=true

**Trigger a build:**
gh api -X POST repos/OWNER/REPO/pages/builds

**Delete pages site:**
gh api -X DELETE repos/OWNER/REPO/pages
```

### 3.5 Webhooks Workflow (New)

```markdown
## Workflow: Webhooks

**List webhooks:**
gh api repos/OWNER/REPO/hooks

**Create webhook:**
gh api -X POST repos/OWNER/REPO/hooks \
  -f name=web -f active=true \
  -f 'events[]=push' -f 'events[]=pull_request' \
  -f config[url]=https://example.com/hook \
  -f config[content_type]=json

**Update webhook (add events):**
gh api -X PATCH repos/OWNER/REPO/hooks/{hook_id} \
  -f active=true -f 'add_events[]=pull_request'

**Ping webhook:**
gh api -X POST repos/OWNER/REPO/hooks/{hook_id}/pings

**Delete webhook:**
gh api -X DELETE repos/OWNER/REPO/hooks/{hook_id}
```

### 3.6 Contents API Workflow (New)

```markdown
## Workflow: Contents API (create/update/delete files via API)

**Get file contents (base64):**
gh api repos/OWNER/REPO/contents/path/to/file

**Get raw file:**
gh api -H 'Accept: application/vnd.github.raw+json' repos/OWNER/REPO/contents/README.md

**Create file:**
echo -n "file content" | base64 | gh api -X PUT repos/OWNER/REPO/contents/newfile.md \
  -f message="Create file" -f content=@-

**Update file (need SHA from GET):**
gh api -X PUT repos/OWNER/REPO/contents/file.md \
  -f message="Update file" -f content=$(echo -n "new content" | base64) \
  -f sha=current_sha

**Delete file:**
gh api -X DELETE repos/OWNER/REPO/contents/file.md \
  -f message="Delete file" -f sha=current_sha
```

### 3.7 Dispatch Events Workflow (New)

```markdown
## Workflow: Dispatch Events

**Trigger a repository dispatch:**
gh api -X POST repos/OWNER/REPO/dispatches \
  -f event_type=deploy \
  -f client_payload[environment]=production

**Use case:** Trigger GitHub Actions workflows from outside GitHub (e.g., after satellite publish).
```

### 3.8 Secrets & Variables Workflow (New)

```markdown
## Workflow: Secrets & Variables

**List repo secrets:**
gh secret list

**Set repo secret:**
gh secret set MY_SECRET -b"value"

**List repo variables:**
gh variable list

**Set repo variable:**
gh variable set MY_VAR -b"value"

**Org-level secrets (via gh api):**
gh api -X PUT /orgs/{org}/actions/secrets/{secret_name} ...
```

### 3.9 Search Workflow (New)

```markdown
## Workflow: Search

**Search repos:**
gh search repos "query" --limit 10

**Search issues:**
gh search issues "query" --repo OWNER/REPO

**Search PRs:**
gh search prs "query" --state open

**Search code:**
gh search code "query" --repo OWNER/REPO

**Search commits:**
gh search commits "query" --repo OWNER/REPO
```

### 3.10 gh api Escape Hatch (New Reference Section)

```markdown
## The gh api Escape Hatch

`gh api` can call ANY GitHub REST endpoint or GraphQL query. Use it when:
- A native `gh` subcommand doesn't exist (wikis, Pages, webhooks, contents)
- You need advanced features (pagination, JQ filtering, custom headers)
- You need to hit endpoints not yet wrapped by `gh`

**Pattern:** `gh api [METHOD] /repos/{owner}/{repo}/...`

**Key flags:**
- `--method` / `-X` — HTTP method (GET/POST/PATCH/PUT/DELETE)
- `--field` / `-F` — typed parameters (auto-converts booleans, numbers, null)
- `--raw-field` / `-f` — string parameters
- `--header` / `-H` — custom headers
- `--paginate` — auto-fetch all pages
- `--jq` / `-q` — filter JSON output
- `--template` / `-t` — Go template formatting
```

### 3.11 Official Documentation References (New)

```markdown
## Official Documentation References

| Topic | URL |
|-------|-----|
| gh CLI manual | https://cli.github.com/manual/ |
| gh repo edit | https://cli.github.com/manual/gh_repo_edit |
| REST API (repos) | https://docs.github.com/en/rest/repos/repos |
| REST API (contents) | https://docs.github.com/en/rest/repos/contents |
| REST API (pages) | https://docs.github.com/en/rest/pages/pages |
| REST API (webhooks) | https://docs.github.com/en/rest/webhooks/repos |
| REST API (secrets) | https://docs.github.com/en/rest/actions/secrets |
| REST API (variables) | https://docs.github.com/en/rest/actions/variables |
| REST API (dispatches) | https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event |
| Wiki docs | https://docs.github.com/en/communities/documenting-your-project-with-wikis |
| Wiki footer/sidebar | https://docs.github.com/en/communities/documenting-your-project-with-wikis/creating-a-footer-or-sidebar-for-your-wiki |
| REST API index | https://docs.github.com/en/rest |
```

## 4. Agent Permission Changes

### github-ops.md (before)
```yaml
permission:
  edit: deny
  bash:
    "*": deny
    "gh *": allow
    "gh pr create*": ask
    "gh pr merge*": ask
    "gh pr close*": ask
    "gh issue create*": ask
    "gh issue close*": ask
    "gh issue reopen*": ask
    "gh release create*": ask
    "gh release delete*": ask
```

### github-ops.md (after)
```yaml
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
```

Key addition: `gh api *: allow` enables all REST/GraphQL operations. Secrets/variables write operations require confirmation.

## 5. Orchestrator Dispatch Rules (n3rverberage.md)

Add to the "When to Dispatch" section:

```markdown
- **User says "wiki", "footer", "sidebar"** → Execute wiki push pattern directly (requires git permissions)
- **User says "pages", "deploy pages"** → Dispatch `github-ops` for Pages API operations
- **User says "webhook", "hook"** → Dispatch `github-ops` for webhook CRUD
- **User says "create file", "update file"** via API → Dispatch `github-ops` for contents API
- **User says "dispatch", "trigger workflow"** → Dispatch `github-ops` for dispatch events
- **User says "search"** → Dispatch `github-ops` for search operations
- **User says "secret", "variable"** → Dispatch `github-ops` for secrets/variables
```

## 6. Data Flow

```
User: "deploy pages for reverberage/hub"
  │
  ▼
Orchestrator: recognizes "pages" → dispatch github-ops
  │
  ▼
github-ops agent:
  1. gh auth status (verify auth)
  2. gh api -X POST repos/reverberage/hub/pages -f source[branch]=main
  3. Report success/failure to orchestrator
```

## 7. Error Handling

| Condition | Detection | Response |
|-----------|-----------|----------|
| Not authenticated | `gh auth status` fails | Report to calling agent, do not proceed |
| Rate limited | HTTP 403/429 from `gh api` | Report rate limit, suggest retry |
| Wiki push failed (git error) | Non-zero exit from git push | Report git error, suggest checking permissions |
| Pages not enabled | 404 from Pages API | Report that Pages is not enabled for this repo |
| Webhook already exists | 422 from webhook create | Report existing webhook, suggest update instead |
| File SHA mismatch | 422 from contents API | Re-fetch SHA, retry update |
| Invalid JSON response | `jq` parse error | Report malformed response, suggest checking endpoint |

## 8. Testing Strategy

Since this is a documentation + configuration change (no code), testing is:

1. **SKILL.md content review**: Verify all workflows are present and accurate
2. **Agent permissions review**: Verify `gh api *: allow` is present
3. **Orchestrator rules review**: Verify new dispatch rules are present
4. **Copy-paste test**: Try each `gh` and `gh api` command against a real repo (dry-run where possible)
5. **Backward compatibility**: Verify existing workflows unchanged

---
name: github-ops
description: "GitHub operations via gh CLI: issues, PRs, releases, Pages, webhooks, contents, dispatch, secrets, variables, search. Destructive ops require confirmation."
compatibility: opencode
---

# Skill: github-ops

## When to Use

Use this skill when:
- Managing pull requests (`gh pr list`, `gh pr view`, `gh pr create`)
- Managing issues (`gh issue list`, `gh issue view`, `gh issue create`)
- Creating or managing releases (`gh release list`, `gh release create`)
- Checking CI/CD status (`gh run list`, `gh run view`)
- Managing repository settings (`gh repo edit`, `gh api`)
- Deploying GitHub Pages (`gh api /repos/**/pages`)
- Managing webhooks (`gh api /repos/**/hooks`)
- Creating/updating files via API (`gh api /repos/**/contents`)
- Triggering repository dispatch events (`gh api /repos/**/dispatches`)
- Managing secrets and variables (`gh secret`, `gh variable`, `gh api`)
- Searching repositories, issues, PRs, code (`gh search`)
- Pushing wiki content (clone, edit, push — requires git permissions)
- Any GitHub operation not covered by a native `gh` subcommand (`gh api`)

## Safety Rules

REQUIRE:
- Run `gh auth status` before any operation — report to calling agent if not authenticated
- Never close or merge PRs without explicit instruction
- Never delete releases without explicit confirmation
- Validate that a PR has passed CI before merging (check `gh pr checks`)
- Report rate-limit errors clearly with retry-after information

REJECT if:
- The user is not authenticated (`gh auth status` fails)
- The operation targets a branch/repo the calling agent didn't specify
- CI checks are failing on a PR that should be merged
- Destructive operations (delete webhook, delete file, delete secret) without explicit confirmation
- Force push to main/master without explicit rationale
- Modifying repo settings without explicit instruction

## Workflow: Creating a Pull Request

1. `gh pr status` — check for existing PRs on the current branch
2. `git log --oneline origin/main..HEAD` — review commits to include
3. `gh pr create --title "<title>" --body "$(cat <<'EOF' ... EOF)"` — create the PR
4. Report PR URL to calling agent

## Workflow: Reviewing a Pull Request

1. `gh pr list --state open` — list open PRs
2. `gh pr view <number>` — view PR details
3. `gh pr diff <number>` — view PR changes
4. `gh pr checks <number>` — check CI status
5. `gh pr review <number> --approve|--comment|--request-changes` — submit review

## Workflow: Managing Issues

- `gh issue list --state open` — list open issues
- `gh issue view <number>` — view issue details
- `gh issue create --title "<title>" --body "<body>"` — create issue
- `gh issue close <number>` — close issue
- `gh issue reopen <number>` — reopen issue

## Workflow: Releases

- `gh release list` — list releases
- `gh release view <tag>` — view release details
- `gh release create <tag> --title "<title>" --notes "<notes>"` — create release

## Workflow: CI/CD Checks

- `gh run list --limit 10` — recent workflow runs
- `gh run view <run-id>` — view run details
- `gh run watch <run-id>` — follow a running job

## Workflow: Repository Management

- `gh repo view OWNER/REPO` — view repo details
- `gh repo edit OWNER/REPO --description "new desc"` — update description
- `gh repo edit OWNER/REPO --homepage https://example.com` — set homepage
- `gh repo edit OWNER/REPO --default-branch main` — set default branch
- `gh repo list --limit 10` — list repos

## Workflow: Wiki Push

Wiki content (pages, footer, sidebar) lives in a git repo — not accessible via `gh` CLI or REST API.

**Auth setup:**
```bash
git remote set-url origin "https://x-access-token:$(gh auth token)@github.com/OWNER/REPO.wiki.git"
```

**Push _Footer.md:**
1. Clone: `git clone https://github.com/OWNER/REPO.wiki.git /tmp/repo.wiki`
2. Auth: `git -C /tmp/repo.wiki remote set-url origin "https://x-access-token:$(gh auth token)@github.com/OWNER/REPO.wiki.git"`
3. Write: `echo "Footer content" > /tmp/repo.wiki/_Footer.md`
4. Commit: `git -C /tmp/repo.wiki add _Footer.md && git -C /tmp/repo.wiki commit -m "Update footer"`
5. Push: `git -C /tmp/repo.wiki push origin main`

**Note:** This operation requires git permissions (clone, add, commit, push). The github-ops agent has `edit: deny` — wiki push must be executed by the orchestrator or git-ops agent.

## Workflow: GitHub Pages

**Get pages config:**
```bash
gh api repos/OWNER/REPO/pages
```

**Create pages site (from main branch, root):**
```bash
gh api -X POST repos/OWNER/REPO/pages -f source[branch]=main -f source[path]=/
```

**Update pages config (enable HTTPS, set custom domain):**
```bash
gh api -X PUT repos/OWNER/REPO/pages -f cname=example.com -f https_enforced=true
```

**Trigger a build:**
```bash
gh api -X POST repos/OWNER/REPO/pages/builds
```

**Delete pages site:**
```bash
gh api -X DELETE repos/OWNER/REPO/pages
```

## Workflow: Webhooks

**List webhooks:**
```bash
gh api repos/OWNER/REPO/hooks
```

**Create webhook:**
```bash
gh api -X POST repos/OWNER/REPO/hooks \
  -f name=web -f active=true \
  -f 'events[]=push' -f 'events[]=pull_request' \
  -f config[url]=https://example.com/hook \
  -f config[content_type]=json
```

**Update webhook (add events):**
```bash
gh api -X PATCH repos/OWNER/REPO/hooks/{hook_id} \
  -f active=true -f 'add_events[]=pull_request'
```

**Ping webhook:**
```bash
gh api -X POST repos/OWNER/REPO/hooks/{hook_id}/pings
```

**Delete webhook:**
```bash
gh api -X DELETE repos/OWNER/REPO/hooks/{hook_id}
```

## Workflow: Contents API (create/update/delete files via API)

**Get file contents (base64):**
```bash
gh api repos/OWNER/REPO/contents/path/to/file
```

**Get raw file:**
```bash
gh api -H 'Accept: application/vnd.github.raw+json' repos/OWNER/REPO/contents/README.md
```

**Create file:**
```bash
echo -n "file content" | base64 | gh api -X PUT repos/OWNER/REPO/contents/newfile.md \
  -f message="Create file" -f content=@-
```

**Update file (need SHA from GET):**
```bash
gh api -X PUT repos/OWNER/REPO/contents/file.md \
  -f message="Update file" -f content=$(echo -n "new content" | base64) \
  -f sha=current_sha
```

**Delete file:**
```bash
gh api -X DELETE repos/OWNER/REPO/contents/file.md \
  -f message="Delete file" -f sha=current_sha
```

## Workflow: Dispatch Events

**Trigger a repository dispatch:**
```bash
gh api -X POST repos/OWNER/REPO/dispatches \
  -f event_type=deploy \
  -f client_payload[environment]=production
```

**Use case:** Trigger GitHub Actions workflows from outside GitHub (e.g., after satellite publish).

## Workflow: Secrets & Variables

**List repo secrets:**
```bash
gh secret list
```

**Set repo secret:**
```bash
gh secret set MY_SECRET -b"value"
```

**List repo variables:**
```bash
gh variable list
```

**Set repo variable:**
```bash
gh variable set MY_VAR -b"value"
```

**Org-level secrets (via gh api):**
```bash
gh api -X PUT /orgs/{org}/actions/secrets/{secret_name} ...
```

## Workflow: Search

**Search repos:**
```bash
gh search repos "query" --limit 10
```

**Search issues:**
```bash
gh search issues "query" --repo OWNER/REPO
```

**Search PRs:**
```bash
gh search prs "query" --state open
```

**Search code:**
```bash
gh search code "query" --repo OWNER/REPO
```

**Search commits:**
```bash
gh search commits "query" --repo OWNER/REPO
```

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

**Examples:**

```bash
# GET with JQ filter
gh api repos/OWNER/REPO/issues --jq '.[].title'

# GET with pagination
gh api repos/OWNER/REPO/issues --paginate --slurp

# POST with typed fields
gh api -X POST repos/OWNER/REPO/dispatches \
  -f event_type=deploy -f client_payload[environment]=production

# PATCH with typed fields
gh api -X PATCH repos/OWNER/REPO -f description="new desc" -f private=true

# DELETE
gh api -X DELETE repos/OWNER/REPO/hooks/{hook_id}

# GraphQL
gh api graphql -F owner='OWNER' -F name='REPO' -f query='
  query($name: String!, $owner: String!) {
    repository(owner: $owner, name: $name) {
      nameWithOwner
      hasWikiEnabled
    }
  }
'
```

## Edge Cases

- **Not authenticated**: `gh auth status` returns non-zero. Report to calling agent, do not proceed.
- **Rate limited**: `gh` outputs HTTP 403/429. Report rate limit message and suggest retry delay.
- **No remote configured**: `git remote -v` shows no `origin`. Report to calling agent.
- **Missing gh CLI**: `command not found: gh`. Report that github-ops requires the GitHub CLI (`brew install gh` / `apt install gh`).
- **PR already exists for branch**: `gh pr status` shows existing PR. Report to calling agent instead of creating duplicate.
- **Wiki push failed (git error)**: Non-zero exit from `git push`. Report git error, suggest checking permissions.
- **Pages not enabled**: 404 from Pages API. Report that Pages is not enabled for this repo.
- **Webhook already exists**: 422 from webhook create. Report existing webhook, suggest update instead.
- **File SHA mismatch**: 422 from contents API. Re-fetch SHA, retry update.
- **Invalid JSON response**: `jq` parse error. Report malformed response, suggest checking endpoint.

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

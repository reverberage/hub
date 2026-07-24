#!/usr/bin/env python3
"""Initialize a satellite wiki on GitHub using the refs/wiki/master trick.

Usage:
    python init-satellite-wiki.py <owner/repo> [--name <satellite-name>] [--push <local-path>]

Creates a wiki for the given GitHub repository by:
  1. Creating a refs/wiki/master ref in the main repo (triggers wiki repo creation)
  2. Waiting for the .wiki.git repo to materialize
  3. Pushing wiki content (Home.md, _Sidebar.md, _Footer.md)
  4. Optionally pushing additional pages from a local path

Suppress the "not working dir" warning: use -P at the start or set GIT_CEILING_DIRECTORIES.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def eprint(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


def run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        eprint(f"Command failed: {' '.join(cmd)}")
        eprint(result.stderr.strip() if result.stderr else "(no stderr)")
    return result


def gh_api(
    method: str,
    endpoint: str,
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | list[Any]:
    """Call gh api and return parsed JSON."""
    cmd = ["gh", "api", "--method", method, endpoint]
    if data is not None:
        cmd.extend(["--input", "-"])
        result = subprocess.run(
            cmd,
            input=json.dumps(data),
            capture_output=True,
            text=True,
        )
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        eprint(f"gh api {method} {endpoint} failed:")
        eprint(result.stderr.strip())
        sys.exit(1)

    if result.stdout.strip():
        return json.loads(result.stdout)
    return {}


def resolve_satellite_name(repo_name: str) -> str:
    """Derive the satellite name from the GitHub repo name.

    E.g., rvrb-my-scout -> my-scout
    """
    if repo_name.startswith("rvrb-"):
        return repo_name[5:]
    return repo_name


WORKFLOW_CONTENT = r"""name: Sync Wiki

on:
  push:
    branches: [main]
    paths:
      - 'docs/**'

concurrency:
  group: wiki-${{ github.ref }}
  cancel-in-progress: true

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: reverberage/.github/actions/sync-wiki@main
        with:
          token: ${{ github.token }}
          path: docs
"""


def init_wiki(
    owner_repo: str,
    satellite_name: str | None = None,
    push_path: str | None = None,
    add_workflow: bool = False,
) -> None:
    """Initialize a wiki for the given GitHub repository."""
    _owner, repo = owner_repo.split("/", 1)
    name = satellite_name or resolve_satellite_name(repo)

    eprint(f"=== Initializing wiki for {owner_repo} ===")

    # ------------------------------------------------------------------
    # Step 1: Verify we have gh and auth
    # ------------------------------------------------------------------
    auth = run(["gh", "auth", "status"])
    if auth.returncode != 0:
        eprint("FATAL: gh CLI not authenticated. Run 'gh auth login' first.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 2: Prepare wiki page content
    # ------------------------------------------------------------------
    home_content = f"# {repo}\n\nreverberage satellite: **{name}**.\n\n"

    sidebar_content = """* [Home](Home)
* [Architecture](Architecture)
* [CLI Reference](CLI-Reference)
* [Getting Started](Getting-Started)
* [Development](Development)
* [FAQ](FAQ)
* [MCP Server](MCP-Server)
* [Python API](Python-API)

---

* [Hub Wiki](https://github.com/reverberage/hub/wiki)
"""

    footer_content = "reverberage — Apache-2.0"

    # ------------------------------------------------------------------
    # Step 3: Create refs/wiki/master via tree + commit + ref
    # This triggers GitHub to materialize the .wiki.git repository.
    # ------------------------------------------------------------------

    # Check if refs/wiki/master already exists
    existing = run(["gh", "api", f"repos/{owner_repo}/git/refs/wiki"])
    if existing.returncode == 0:
        eprint("INFO: refs/wiki/master already exists. Skipping ref creation.")
    else:
        eprint("Creating refs/wiki/master to trigger wiki repo creation...")

        # Create tree with wiki pages
        tree_payload = {
            "base_tree": None,
            "tree": [
                {
                    "path": "Home.md",
                    "mode": "100644",
                    "type": "blob",
                    "content": home_content,
                },
                {
                    "path": "_Sidebar.md",
                    "mode": "100644",
                    "type": "blob",
                    "content": sidebar_content,
                },
                {
                    "path": "_Footer.md",
                    "mode": "100644",
                    "type": "blob",
                    "content": footer_content,
                },
            ],
        }
        tree = gh_api("POST", f"repos/{owner_repo}/git/trees", tree_payload)
        tree_sha: str = tree["sha"]

        # Create commit
        commit = gh_api(
            "POST",
            f"repos/{owner_repo}/git/commits",
            {"message": "Initial wiki", "tree": tree_sha, "parents": []},
        )
        commit_sha: str = commit["sha"]

        # Create refs/wiki/master
        gh_api(
            "POST",
            f"repos/{owner_repo}/git/refs",
            {"ref": "refs/wiki/master", "sha": commit_sha},
        )
        eprint(f"  Created refs/wiki/master at {commit_sha[:12]}")

    # ------------------------------------------------------------------
    # Step 4: Wait for the .wiki.git repo to materialize
    # ------------------------------------------------------------------
    wiki_clone_url = f"https://github.com/{owner_repo}.wiki.git"
    eprint("Waiting for wiki git repo to materialize...")

    for attempt in range(1, 13):  # up to ~60 seconds
        time.sleep(5)
        result = run(
            ["git", "ls-remote", wiki_clone_url, "HEAD"],
            env={**os.environ, "GIT_CEILING_DIRECTORIES": "/tmp"},
        )
        if result.returncode == 0 and result.stdout.strip():
            eprint(f"  Wiki repo ready! (attempt {attempt})")
            break
        eprint(f"  Not ready yet... (attempt {attempt}/12)")
    else:
        eprint("ERROR: Wiki git repo did not materialize within 60 seconds.")
        eprint(f"  Try visiting https://github.com/{owner_repo}/wiki/new in a browser.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 5: Push full wiki content
    # ------------------------------------------------------------------
    tmpdir = Path("/tmp") / f"wiki-{repo}-{int(time.time())}"
    tmpdir.mkdir(parents=True, exist_ok=True)

    token = run(["gh", "auth", "token"]).stdout.strip()
    auth_url = wiki_clone_url.replace("https://", f"https://x-access-token:{token}@")

    eprint("Cloning wiki repo...")
    clone = run(["git", "clone", auth_url, str(tmpdir / "wiki")])
    if clone.returncode != 0:
        eprint("ERROR: Failed to clone wiki repo.")
        sys.exit(1)

    wiki_dir = tmpdir / "wiki"

    # Home.md might already exist (from refs/wiki/master), update it
    (wiki_dir / "Home.md").write_text(home_content)
    (wiki_dir / "_Sidebar.md").write_text(sidebar_content)
    (wiki_dir / "_Footer.md").write_text(footer_content)

    # If push_path is provided, copy .md files from there into the wiki
    if push_path:
        src = Path(push_path)
        if src.exists() and src.is_dir():
            for md_file in sorted(src.glob("*.md")):
                dest = wiki_dir / md_file.name
                # Skip sidebar/footer — those are managed by this script
                if md_file.name in ("_Sidebar.md", "_Footer.md"):
                    continue
                dest.write_text(md_file.read_text())
                eprint(f"  Copied {md_file.name}")

    # Commit and push
    eprint("Pushing wiki content...")
    run(["git", "-C", str(wiki_dir), "add", "."])
    run(["git", "-C", str(wiki_dir), "commit", "-m", "Populate wiki"])
    push = run(["git", "-C", str(wiki_dir), "push", "origin", "master"])
    if push.returncode != 0:
        eprint("ERROR: Failed to push wiki content.")
        eprint(push.stderr.strip())
        sys.exit(1)

    eprint(f"✅ Wiki initialized: https://github.com/{owner_repo}/wiki")
    eprint(f"   Clone URL: {wiki_clone_url}")

    # ------------------------------------------------------------------
    # Step 6: Optionally add the sync-wiki.yml workflow
    # ------------------------------------------------------------------
    if add_workflow:
        eprint("Adding sync-wiki.yml workflow...")
        encoded = base64.b64encode(WORKFLOW_CONTENT.encode()).decode()
        result = run(
            [
                "gh",
                "api",
                f"repos/{owner_repo}/contents/.github/workflows/sync-wiki.yml",
                "--method",
                "PUT",
                "--field",
                "message=feat(ci): add wiki sync workflow",
                "--field",
                f"content={encoded}",
            ]
        )
        if result.returncode == 0:
            eprint("✅ sync-wiki.yml workflow added — docs/ will auto-sync to wiki on push")
        else:
            eprint("WARNING: Could not add sync-wiki.yml workflow.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize a satellite wiki on GitHub via refs/wiki/master trick",
    )
    parser.add_argument(
        "repo",
        help="GitHub repository (e.g., reverberage/rvrb-my-satellite)",
    )
    parser.add_argument(
        "--name",
        help="Satellite name (derived from repo name if omitted)",
    )
    parser.add_argument(
        "--push",
        help="Path to directory with .md files to push as wiki pages",
    )
    parser.add_argument(
        "--workflow",
        action="store_true",
        help="Add .github/workflows/sync-wiki.yml for auto-sync on push",
    )
    args = parser.parse_args()

    if "/" not in args.repo:
        eprint("ERROR: repo must be in format <owner>/<repo>")
        sys.exit(1)

    init_wiki(args.repo, args.name, args.push, add_workflow=args.workflow)


if __name__ == "__main__":
    main()

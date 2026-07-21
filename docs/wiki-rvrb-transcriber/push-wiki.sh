#!/bin/bash
# Push wiki pages to rvrb-transcriber GitHub wiki
#
# Prerequisites:
#   1. Go to https://github.com/reverberage/rvrb-transcriber/wiki
#   2. Click "Create the first page" (any content, just to initialize the repo)
#   3. Save the page
#   4. Run this script from hub repo root

set -euo pipefail

WIKI_DIR="docs/wiki-rvrb-transcriber"
WIKI_REPO="https://github.com/reverberage/rvrb-transcriber.wiki.git"
TMP_DIR=$(mktemp -d)

echo "==> Cloning wiki repo..."
git clone "$WIKI_REPO" "$TMP_DIR"

echo "==> Copying wiki pages..."
cp "$WIKI_DIR"/*.md "$TMP_DIR/"

echo "==> Committing and pushing..."
cd "$TMP_DIR"
git add -A
git commit -m "docs: complete wiki with 10 pages (Home, Getting Started, CLI, Python API, Engines, Output Formats, MCP, Architecture, Development, FAQ)"
git push

echo "==> Done! Wiki updated at: https://github.com/reverberage/rvrb-transcriber/wiki"
rm -rf "$TMP_DIR"

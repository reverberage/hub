#!/usr/bin/env bash
# dev-setup.sh — Bootstrap all reverberage satellite editable installs
#
# Usage:
#   scripts/dev-setup.sh          # Install all satellites
#   scripts/dev-setup.sh --check  # Check status only, no changes
#   scripts/dev-setup.sh --nuke   # Remove all rvrb-* packages first

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

say()    { echo -e "$@"; }
ok()     { echo -e "  ${GREEN}✓${NC} $1"; }
fail()   { echo -e "  ${RED}✗${NC} $1"; }
warn()   { echo -e "  ${YELLOW}⚠${NC} $1"; }

# ---------------------------------------------------------------------------
# Discover satellites
# ---------------------------------------------------------------------------
discover() {
    local dirs=()
    for d in "$WORKSPACE"/../rvrb-*; do
        [ -d "$d" ] && [ -f "$d/pyproject.toml" ] && dirs+=("$(realpath "$d")")
    done
    printf '%s\n' "${dirs[@]}"
}

# ---------------------------------------------------------------------------
# Remove stale / wrong-path editable installs
# ---------------------------------------------------------------------------
clean_stale() {
    say "${YELLOW}Removing stale rvrb-* editable installs...${NC}"
    local stale
    stale=$(pip3 list --editable 2>/dev/null | awk '/^rvrb-/ {print $1}' || true)
    if [ -z "$stale" ]; then
        ok "No stale rvrb-* packages found"
        return
    fi
    for pkg in $stale; do
        say "  Uninstalling $pkg..."
        pip3 uninstall -y "$pkg" 2>/dev/null || true
    done
    ok "Stale packages removed"
}

# ---------------------------------------------------------------------------
# Install all active satellites
# ---------------------------------------------------------------------------
install_all() {
    local dirs
    mapfile -t dirs < <(discover)
    local ok_count=0
    local fail_count=0

    say "${YELLOW}Installing satellites...${NC}"
    for dir in "${dirs[@]}"; do
        local name
        name=$(basename "$dir")
        # Derive import name: rvrb-see → rvrb_see
        local import_name="${name//-/_}"
        echo -n "  $name... "

        if pip3 install -e "$dir" --break-system-packages >/dev/null 2>&1; then
            # Verify import
            if python3 -c "import $import_name" 2>/dev/null; then
                ok "$name installed ($import_name)"
                ok_count=$((ok_count + 1))
            else
                fail "$name: install succeeded but import $import_name failed"
                fail_count=$((fail_count + 1))
            fi
        else
            fail "$name: pip install failed"
            fail_count=$((fail_count + 1))
        fi
    done

    echo ""
    say "Installed: ${GREEN}$ok_count${NC} / Failed: ${RED}$fail_count${NC}"
    return $fail_count
}

# ---------------------------------------------------------------------------
# Check-only mode
# ---------------------------------------------------------------------------
check_status() {
    local dirs
    mapfile -t dirs < <(discover)
    local total=0 ok_count=0

    say "Satellite status:"
    for dir in "${dirs[@]}"; do
        local name import_name pip_path
        name=$(basename "$dir")
        import_name="${name//-/_}"

        # Check pip
        pip_path=$(pip3 show "$name" 2>/dev/null | awk '/^Editable project location:/ {getline; print $0}' || true)
        if [ -z "$pip_path" ]; then
            pip_path=$(pip3 show "$name" 2>/dev/null | awk '/^Location:/ {print $2}' || echo "NOT INSTALLED")
        fi

        # Check import
        if python3 -c "import $import_name" 2>/dev/null; then
            echo "  $name: installed + importable"
            ok_count=$((ok_count + 1))
        else
            if [ -n "$pip_path" ]; then
                echo "  $name: installed but import BROKEN (pip: $pip_path, import: $import_name)"
            else
                echo "  $name: NOT INSTALLED"
            fi
        fi
        total=$((total + 1))
    done

    echo ""
    say "Importable: ${GREEN}$ok_count${NC} / $total"
    [ "$ok_count" -eq "$total" ]
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
case "${1:-}" in
    --check)
        check_status
        ;;
    --nuke)
        clean_stale
        install_all
        ;;
    *)
        clean_stale
        install_all
        ;;
esac

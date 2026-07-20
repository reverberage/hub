#!/usr/bin/env bash
# quality-gate.sh — Run quality checks across all reverberage satellites
#
# Usage:
#   scripts/quality-gate.sh              # All satellites
#   scripts/quality-gate.sh --quick      # Fast: ruff + mypy only, no tests
#   scripts/quality-gate.sh --sat rvrb-see  # Single satellite
#   scripts/quality-gate.sh --json       # Machine-readable JSON output

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

run_tests=true
json_out=false
single=""

# ---------------------------------------------------------------------------
# CLI parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --quick)  run_tests=false ;;
        --json)   json_out=true ;;
        --sat)    single="$2"; shift ;;
        --sat=*)  single="${1#--sat=}" ;;
        *) echo "Unknown flag: $1"; exit 2 ;;
    esac
    shift
done

# ---------------------------------------------------------------------------
# Discover satellites
# ---------------------------------------------------------------------------
discover() {
    if [ -n "$single" ]; then
        local d="$WORKSPACE/../$single"
        if [ -d "$d" ] && [ -f "$d/pyproject.toml" ]; then
            echo "$(realpath "$d")"
        else
            echo "ERROR: satellite '$single' not found at $d" >&2
            exit 1
        fi
        return
    fi
    for d in "$WORKSPACE"/../rvrb-*; do
        [ -d "$d" ] && [ -f "$d/pyproject.toml" ] && realpath "$d"
    done | sort
}

# ---------------------------------------------------------------------------
# Check runner
# ---------------------------------------------------------------------------
PASS=0
FAIL=0
RESULTS=()

check() {
    local dir="$1"
    local name; name=$(basename "$dir")
    local ruff_ok=true mypy_ok=true import_ok=true tests_ok=true tests_collect=true
    local tests_found=0

    # All checks run from within the package directory so they pick up pyproject.toml config
    # --- ruff ---
    if (cd "$dir" && ruff check src/ tests/ --output-format concise >/dev/null 2>&1); then
        ruff_ok=true
    else
        ruff_ok=false
    fi

    # --- mypy ---
    if (cd "$dir" && mypy src/ >/dev/null 2>&1); then
        mypy_ok=true
    else
        mypy_ok=false
    fi

    # --- import ---
    local import_name="${name//-/_}"
    if python3 -c "import $import_name" 2>/dev/null; then
        import_ok=true
    else
        import_ok=false
    fi

    # --- tests (collect + run) ---
    if [ "$run_tests" = true ]; then
        # Check if tests are collectable
        local collected
        collected=$(python3 -m pytest "$dir/tests/" --co -q 2>/dev/null | grep -oP '\d+(?= tests collected)' || echo "0")
        tests_found=$collected
        if [ "$collected" -gt 0 ] 2>/dev/null; then
            # Run them
            if python3 -m pytest "$dir/tests/" -q --tb=short >/dev/null 2>&1; then
                tests_ok=true
            else
                tests_ok=false
            fi
        else
            tests_collect=false
            tests_ok=false
        fi
    fi

    # Aggregate
    local total_failures=0
    [ "$ruff_ok" = true ]   || total_failures=$((total_failures + 1))
    [ "$mypy_ok" = true ]   || total_failures=$((total_failures + 1))
    [ "$import_ok" = true ] || total_failures=$((total_failures + 1))
    if [ "$run_tests" = true ]; then
        [ "$tests_collect" = false ] && total_failures=$((total_failures + 1))
        [ "$tests_ok" = false ] && [ "$tests_collect" = true ] && total_failures=$((total_failures + 1))
    fi

    if [ "$total_failures" -eq 0 ]; then
        PASS=$((PASS + 1))
        local verdict="PASS"
    else
        FAIL=$((FAIL + 1))
        local verdict="FAIL"
    fi

    if [ "$json_out" = true ]; then
        RESULTS+=("{\"name\":\"$name\",\"verdict\":\"$verdict\",\"checks\":{\"ruff\":$ruff_ok,\"mypy\":$mypy_ok,\"import\":$import_ok,\"tests\":{\"collected\":$tests_found,\"passed\":$tests_ok}}}")
    else
        # Human-readable
        local icon=""
        [ "$verdict" = "PASS" ] && icon="${GREEN}✓${NC}" || icon="${RED}✗${NC}"
        printf "  %s %-25s" "$icon" "$name"
        [ "$ruff_ok" = true ]  && printf " ${GREEN}ruff${NC}"  || printf " ${RED}ruff${NC}"
        [ "$mypy_ok" = true ] && printf " ${GREEN}mypy${NC}" || printf " ${RED}mypy${NC}"
        [ "$import_ok" = true ] && printf " ${GREEN}import${NC}" || printf " ${RED}import${NC}"
        if [ "$run_tests" = true ]; then
            if [ "$tests_collect" = true ]; then
                [ "$tests_ok" = true ] && printf " ${GREEN}tests(%s)${NC}" "$tests_found" || printf " ${RED}tests(%s)${NC}" "$tests_found"
            else
                printf " ${RED}collect${NC}"
            fi
        fi
        echo ""
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    local dirs
    mapfile -t dirs < <(discover)

    if [ "$json_out" = false ]; then
        echo ""
        echo "${BOLD}Quality Gate${NC}"
        echo "─────────────"
    fi

    for dir in "${dirs[@]}"; do
        check "$dir"
    done

    if [ "$json_out" = true ]; then
        echo "{"
        echo "  \"pass\": $PASS,"
        echo "  \"fail\": $FAIL,"
        echo "  \"results\": ["
        local last=$(( ${#RESULTS[@]} - 1 ))
        for i in "${!RESULTS[@]}"; do
            local comma=","
            [ "$i" -eq "$last" ] && comma=""
            echo "    ${RESULTS[$i]}$comma"
        done
        echo "  ]"
        echo "}"
    else
        echo ""
        local total=$((PASS + FAIL))
        echo "  ${GREEN}$PASS pass${NC} / ${RED}$FAIL fail${NC} / $total total"
        echo ""
    fi

    return $FAIL
}

main

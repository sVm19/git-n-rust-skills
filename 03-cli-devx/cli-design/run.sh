#!/usr/bin/env bash
# run.sh — Entry point for cli-design skill
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/src"

case "${1:-help}" in
  run)
    shift
    python "$SRC/main.py" "$@"
    ;;
  analyze)
    shift
    python "$SRC/main.py" analyze "$@"
    ;;
  compare)
    shift
    python "$SRC/main.py" compare "$@"
    ;;
  export)
    shift
    python "$SRC/main.py" export "$@"
    ;;
  test)
    cd "$SCRIPT_DIR" && python -m pytest tests/ -v
    ;;
  help|--help|-h)
    echo "cli-design skill — Stageira CLI"
    echo ""
    echo "Usage: ./run.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  analyze <repo>    Analyze git repo"
    echo "  compare           Compare time periods"
    echo "  export            Export metrics"
    echo "  test              Run tests"
    ;;
  *)
    echo "Unknown: $1"
    exit 1
    ;;
esac

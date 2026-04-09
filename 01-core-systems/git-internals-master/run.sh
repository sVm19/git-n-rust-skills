#!/usr/bin/env bash
# run.sh — Entry point for git-internals-master skill
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/src"

case "${1:-help}" in
  analyze)
    shift
    python "$SRC/scanner.py" "$@"
    ;;
  test)
    cd "$SCRIPT_DIR" && python -m pytest tests/ -v
    ;;
  help|--help|-h)
    echo "git-internals-master"
    echo ""
    echo "Usage: ./run.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  analyze <repo-path>   Scan commits and extract data"
    echo "  test                  Run unit tests"
    echo "  help                  Show this message"
    ;;
  *)
    echo "Unknown command: $1"
    exit 1
    ;;
esac

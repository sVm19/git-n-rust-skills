#!/usr/bin/env bash
# activate.git-n-rust-skills.sh
# ============================================================
# Stageira Skills — Universal MCP Activator (macOS / Linux)
# ============================================================
#
# LOCAL mode:
#     bash activate.git-n-rust-skills.sh
#
# GITHUB mode:
#     bash activate.git-n-rust-skills.sh --github-repo you/git-n-rust-skills
#     bash activate.git-n-rust-skills.sh --github-repo you/repo --branch main
#     bash activate.git-n-rust-skills.sh --github-repo you/repo --token ghp_xxx
#
# Registers with ALL detected MCP-compatible agents:
#   Claude Desktop | Cursor | Windsurf | VS Code (Cline) | Zed | Continue.dev
# ============================================================

set -euo pipefail

SKILLS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SKILLS_ROOT/mcp_server/server.py"
REQUIREMENTS="$SKILLS_ROOT/mcp_server/requirements.txt"
GITHUB_REPO=""
BRANCH="main"
GITHUB_TOKEN=""
DRY_RUN=false

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --github-repo) GITHUB_REPO="$2"; shift 2 ;;
        --branch)      BRANCH="$2"; shift 2 ;;
        --token)       GITHUB_TOKEN="$2"; shift 2 ;;
        --dry-run)     DRY_RUN=true; shift ;;
        *) shift ;;
    esac
done

IS_GITHUB=false
[[ -n "$GITHUB_REPO" ]] && IS_GITHUB=true
MODE_LABEL=$( $IS_GITHUB && echo "GitHub ($GITHUB_REPO @ $BRANCH)" || echo "Local ($SKILLS_ROOT)" )

# Colors
G='\033[0;32m'; Y='\033[1;33m'; C='\033[0;36m'; R='\033[0;31m'; X='\033[0m'; D='\033[2;37m'

echo ""
echo -e "${C}  ╔══════════════════════════════════════════════════╗${X}"
echo -e "${C}  ║  git-n-rust-skills — Universal MCP Activator    ║${X}"
echo -e "${C}  ║  Mode: $MODE_LABEL${X}"
echo -e "${C}  ╚══════════════════════════════════════════════════╝${X}"
echo ""

# ── Python ───────────────────────────────────────────────────────────────────
echo -e "${Y}[1/4] Checking Python...${X}"
PYTHON_CMD=""
for c in python3 python python3.11 python3.10; do
    if command -v "$c" &>/dev/null && [[ "$($c --version 2>&1)" == Python\ 3* ]]; then
        PYTHON_CMD="$c"; break
    fi
done
[[ -z "$PYTHON_CMD" ]] && { echo -e "${R}  ✗ Python 3 not found${X}"; exit 1; }
echo -e "${G}  ✓ $PYTHON_CMD $($PYTHON_CMD --version 2>&1)${X}"
PYTHON_PATH=$(command -v "$PYTHON_CMD")

# ── Install deps ──────────────────────────────────────────────────────────────
echo -e "${Y}[2/4] Installing dependencies...${X}"
[[ "$DRY_RUN" == false ]] && $PYTHON_CMD -m pip install -q -r "$REQUIREMENTS"
echo -e "${G}  ✓ mcp, pyyaml, pydantic ready${X}"

# ── Build server args ─────────────────────────────────────────────────────────
echo -e "${Y}[3/4] Building server configuration...${X}"
if $IS_GITHUB; then
    SERVER_ARGS="[\"$PYTHON_PATH\", \"$SERVER_SCRIPT\", \"--github-repo\", \"$GITHUB_REPO\", \"--branch\", \"$BRANCH\"]"
else
    SERVER_ARGS="[\"$PYTHON_PATH\", \"$SERVER_SCRIPT\", \"--skills-root\", \"$SKILLS_ROOT\"]"
fi
echo -e "${G}  ✓ Args built${X}"

# ── Merge helper (Python handles JSON safely) ─────────────────────────────────
merge_mcp_config() {
    local cfg_path="$1"
    local agent_name="$2"
    local extra_env="${3:-}"

    mkdir -p "$(dirname "$cfg_path")"

    $PYTHON_CMD - <<PYEOF
import json, os, pathlib

cfg_path = pathlib.Path("$cfg_path")
try:
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
except Exception:
    cfg = {}

cfg.setdefault("mcpServers", {})
entry = {
    "command": "$PYTHON_PATH",
    "args": ["$SERVER_SCRIPT"],
    "env": {"PYTHONPATH": "$SKILLS_ROOT"}
}
if "$IS_GITHUB" == "true":
    entry["args"] += ["--github-repo", "$GITHUB_REPO", "--branch", "$BRANCH"]
else:
    entry["args"] += ["--skills-root", "$SKILLS_ROOT"]
if "$GITHUB_TOKEN":
    entry["env"]["GITHUB_TOKEN"] = "$GITHUB_TOKEN"

cfg["mcpServers"]["stageira-skills"] = entry
if "$DRY_RUN" == "false":
    cfg_path.write_text(json.dumps(cfg, indent=2))
print("ok")
PYEOF
    echo -e "${G}  ✓ $agent_name  →  $cfg_path${X}"
}

# ── Detect config dirs ────────────────────────────────────────────────────────
echo -e "${Y}[4/4] Detecting agents...${X}"
echo ""

REGISTERED=0

# Claude Desktop
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CFG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    CLAUDE_APP="/Applications/Claude.app"
else
    CLAUDE_CFG="$HOME/.config/Claude/claude_desktop_config.json"
    CLAUDE_APP="/usr/bin/claude"
fi
if [[ -d "$(dirname "$CLAUDE_CFG")" ]] || [[ -e "$CLAUDE_APP" ]]; then
    merge_mcp_config "$CLAUDE_CFG" "Claude Desktop"
    REGISTERED=$((REGISTERED+1))
else
    echo -e "${D}  –  Claude Desktop     not detected (skipped)${X}"
fi

# Cursor
CURSOR_CFG="$HOME/.cursor/mcp.json"
if [[ -d "$HOME/.cursor" ]] || command -v cursor &>/dev/null; then
    merge_mcp_config "$CURSOR_CFG" "Cursor"
    REGISTERED=$((REGISTERED+1))
else
    echo -e "${D}  –  Cursor             not detected (skipped)${X}"
fi

# Windsurf
WINDSURF_CFG="$HOME/.codeium/windsurf/mcp_server_config.json"
if [[ -d "$HOME/.codeium/windsurf" ]]; then
    merge_mcp_config "$WINDSURF_CFG" "Windsurf"
    REGISTERED=$((REGISTERED+1))
else
    echo -e "${D}  –  Windsurf           not detected (skipped)${X}"
fi

# VS Code + Cline
if [[ "$OSTYPE" == "darwin"* ]]; then
    CLINE_CFG="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
else
    CLINE_CFG="$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
fi
if [[ -d "$(dirname "$(dirname "$(dirname "$(dirname "$CLINE_CFG")")")")" ]]; then
    merge_mcp_config "$CLINE_CFG" "VS Code / Cline"
    REGISTERED=$((REGISTERED+1))
else
    echo -e "${D}  –  VS Code / Cline    not detected (skipped)${X}"
fi

# Continue.dev
CONTINUE_CFG="$HOME/.continue/config.json"
if [[ -d "$HOME/.continue" ]]; then
    merge_mcp_config "$CONTINUE_CFG" "Continue.dev"
    REGISTERED=$((REGISTERED+1))
else
    echo -e "${D}  –  Continue.dev       not detected (skipped)${X}"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
SKILL_COUNT=$(find "$SKILLS_ROOT" -name "SKILL.md" | wc -l | tr -d ' ')

echo ""
echo -e "${G}  ══════════════════════════════════════════════════${X}"
echo -e "${G}  ✅  Registered with $REGISTERED agents | $SKILL_COUNT skills${X}"
echo -e "${G}  ══════════════════════════════════════════════════${X}"
echo ""
echo -e "  Mode: ${C}$MODE_LABEL${X}"
$IS_GITHUB && echo -e "  Source: ${C}https://github.com/$GITHUB_REPO${X}"
echo ""
echo -e "${Y}  NEXT STEP: Restart all open editors to activate.${X}"
echo ""
echo "  Tools available in every agent:"
echo -e "    ${C}list_skills()${X}          — Browse all skills"
echo -e "    ${C}search_skills('query')${X} — Find by keyword"
echo -e "    ${C}read_skill('name')${X}     — Load full instructions"
echo -e "    ${C}reload_skills()${X}        — Pull latest from GitHub"
echo ""
[[ "$DRY_RUN" == true ]] && echo -e "${Y}  [DRY RUN] No files were modified.${X}"

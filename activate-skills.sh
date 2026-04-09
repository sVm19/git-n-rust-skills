#!/usr/bin/env bash
# activate-skills.sh
# ============================================================
# Stageira Skills — One-Command MCP Activation (macOS / Linux)
# ============================================================
# Run from the git-n-rust-skills project directory:
#
#     bash activate-skills.sh
#
# What this does:
#   1. Checks Python 3 is available
#   2. Installs mcp + pyyaml packages
#   3. Finds your Claude Desktop config
#   4. Registers the stageira-skills MCP server
#   5. Tells you to restart Claude Desktop
# ============================================================

set -euo pipefail

SKILLS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SKILLS_ROOT/mcp_server/server.py"
REQUIREMENTS="$SKILLS_ROOT/mcp_server/requirements.txt"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}  ╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║   Stageira Skills — MCP Activator        ║${NC}"
echo -e "${CYAN}  ╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Check Python ─────────────────────────────────────────────────────
echo -e "${YELLOW}[1/4] Checking Python...${NC}"

PYTHON_CMD=""
for candidate in python3 python python3.11 python3.10; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" --version 2>&1)
        if [[ $version == Python\ 3* ]]; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}  ✗ Python 3 not found. Install from https://python.org${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ Found: $($PYTHON_CMD --version)${NC}"

# ── Step 2: Install Python deps ──────────────────────────────────────────────
echo -e "${YELLOW}[2/4] Installing MCP + dependencies...${NC}"

$PYTHON_CMD -m pip install -q -r "$REQUIREMENTS"
echo -e "${GREEN}  ✓ Dependencies installed (mcp, pyyaml, pydantic)${NC}"

# ── Step 3: Find Claude Desktop config ───────────────────────────────────────
echo -e "${YELLOW}[3/4] Locating Claude Desktop config...${NC}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
else
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
fi

CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
mkdir -p "$CLAUDE_CONFIG_DIR"
echo -e "${GREEN}  ✓ Config directory: $CLAUDE_CONFIG_DIR${NC}"

# ── Step 4: Register MCP server ──────────────────────────────────────────────
echo -e "${YELLOW}[4/4] Registering stageira-skills MCP server...${NC}"

PYTHON_PATH=$(command -v "$PYTHON_CMD")

# Read existing config or start fresh
if [ -f "$CLAUDE_CONFIG" ]; then
    EXISTING=$(cat "$CLAUDE_CONFIG")
    echo -e "${GREEN}  ✓ Loaded existing config (preserving other servers)${NC}"
else
    EXISTING='{"mcpServers":{}}'
fi

# Inject our server using Python (avoids jq dependency)
$PYTHON_CMD - <<PYEOF
import json, sys, pathlib

config_path = pathlib.Path("$CLAUDE_CONFIG")
existing = json.loads("""$EXISTING""")
if "mcpServers" not in existing:
    existing["mcpServers"] = {}

existing["mcpServers"]["stageira-skills"] = {
    "command": "$PYTHON_PATH",
    "args": ["$SERVER_SCRIPT", "--skills-root", "$SKILLS_ROOT"],
    "env": {"PYTHONPATH": "$SKILLS_ROOT"}
}

config_path.write_text(json.dumps(existing, indent=2))
print("  Config written.")
PYEOF

echo -e "${GREEN}  ✓ Registered 'stageira-skills' in Claude config${NC}"

# ── Count skills ─────────────────────────────────────────────────────────────
SKILL_COUNT=$(find "$SKILLS_ROOT" -name "SKILL.md" | wc -l | tr -d ' ')
echo ""
echo -e "${CYAN}  📚 Skills detected: $SKILL_COUNT SKILL.md files${NC}"

# ── Success ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}  ══════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅  ACTIVATION COMPLETE${NC}"
echo -e "${GREEN}  ══════════════════════════════════════════${NC}"
echo ""
echo "  Config: $CLAUDE_CONFIG"
echo ""
echo -e "${YELLOW}  NEXT STEP: Restart Claude Desktop${NC}"
echo ""
echo "  Claude will then have:"
echo -e "    ${CYAN}list_skills()${NC}         — See all $SKILL_COUNT skills"
echo -e "    ${CYAN}search_skills(query)${NC}  — Find skills fast"
echo -e "    ${CYAN}read_skill(name)${NC}      — Load full instructions"
echo -e "    ${CYAN}reload_skills()${NC}       — Pick up new SKILL.md files"
echo ""

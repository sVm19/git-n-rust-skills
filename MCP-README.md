# git-n-rust-skills — Universal MCP Setup

> One command activates all your skills in **every** coding agent on your machine.

## Quick Installation

### MCP Server (Claude Desktop, Cursor, Windsurf, VS Code, Zed, Continue.dev)

Registers skills as an MCP server — every connected agent gets `list_skills`, `search_skills`, `read_skill`, and `reload_skills` tools.

```bash
npx -y github:sVm19/git-n-rust-skills
```

### Project-Level Files (Claude Code, Codex)

Generate `CLAUDE.md` + `.claude/rules/` and `AGENTS.md` + `.codex/` in any project directory. Agents auto-discover the skills on session start — no server required.

```bash
npx -y github:sVm19/git-n-rust-skills -- --init .
```

| Agent | What Gets Created | Agent Behavior |
|-------|-------------------|----------------|
| **Claude Code** | `CLAUDE.md` + `.claude/rules/<skill>.md` | Reads rules on session start, scopes by directory |
| **Codex** | `AGENTS.md` + `.codex/<skill>.md` | Merges instructions hierarchically from root down |

Commit the generated files so every teammate's agent picks them up automatically.

---

## Agents Supported

| Agent | Method | Config Location |
|-------|--------|----------------|
| **Claude Desktop** | MCP Server | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Claude Code** | Project files | `CLAUDE.md` + `.claude/rules/` |
| **Cursor** | MCP Server | `~\.cursor\mcp.json` |
| **Windsurf** | MCP Server | `~\.codeium\windsurf\mcp_server_config.json` |
| **VS Code + Cline** | MCP Server | VS Code globalStorage / `cline_mcp_settings.json` |
| **Zed** | MCP Server | `%APPDATA%\Zed\settings.json` (context_servers) |
| **Continue.dev** | MCP Server | `~\.continue\config.json` |
| **OpenAI Codex CLI** | Project files | `AGENTS.md` + `.codex/` |
| **Antigravity (Gemini)** | MCP Server | `~\.gemini\antigravity\mcp_config.json` |

---

## What Every Agent Gets

Once activated via MCP, every coding agent has **4 new tools**:

```
list_skills()             → See all skills grouped by category
search_skills("churn")    → Find skills by keyword (ranked)
read_skill("git-internals-master")  → Load full SKILL.md instructions
reload_skills()           → Reload skills inside the agent
```

For **Claude Code** and **Codex**, the agent reads the skill index file on session start and loads the matching rule file automatically — no tool invocations needed.

---

## Add a New Skill

```bash
# Generate boilerplate
python skill-creator/generate_skill.py 01-core-systems my-new-skill

# Edit SKILL.md, commit, push
git add . && git commit -m "add: my-new-skill" && git push

# Tell any MCP agent to reload
# Agent calls: reload_skills()

# For project-level users, re-run init to regenerate files
npx -y github:sVm19/git-n-rust-skills -- --init .
```

---

## Deactivate

To remove the MCP server, uninstall the package and edit out the config entry:

```bash
pip uninstall git-n-rust-skills
```

To remove project-level files, delete `CLAUDE.md`, `AGENTS.md`, `.claude/`, and `.codex/`.

---

## Test Without an Agent

```bash
python mcp_server/test_server.py
```

Verifies all SKILL.md files parse and the registry works.

---

## File Map

```
package.json            ← npx entry point
pyproject.toml          ← Python package definition and data mappings
README.md               ← Main documentation
MCP-README.md           ← This file

bin/
└── activate.js         ← npx wrapper (installs pip package + runs activator)

mcp_server/
├── activator.py        ← Registers MCP server + generates project-level files
├── server.py           ← MCP server (stdio, works with any MCP client)
├── skill_registry.py   ← Local filesystem scanner
└── test_server.py      ← Smoke test (no agent needed)

<skill-categories>/     ← E.g. 01-core-systems, containing SKILL.md files bundled into the install
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Missing python` | You must have Python installed and on your PATH. |
| `ModuleNotFoundError: mcp` | The installation failed. Try running `python -m pip install git+https://github.com/sVm19/git-n-rust-skills` manually. |
| Skills not updating | Agent calls `reload_skills()` or restart the agent |
| `.claude/` or `.codex/` files missing skills | Re-run `npx -y github:sVm19/git-n-rust-skills -- --init .` |

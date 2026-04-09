# git-n-rust-skills — Universal MCP Setup

> One command activates all your skills in **every** coding agent on your machine.

## Quick Installation

Installing the package automatically pulls down all local skills and gives you access to the cross-platform unified activator.

```bash
# 1. Install directly from GitHub
pip install git+https://github.com/sVm19/git-n-rust-skills

# 2. Activate into all detected coding agents
git-n-rust-skills-activate
```

*(Note: Ensure your Python environment paths are set so that pip console scripts are available in your shell).*

---

## Agents Supported

The `git-n-rust-skills-activate` script auto-detects which agents are installed and configures **all of them**:

| Agent | Config Location |
|-------|----------------|
| **Claude Desktop** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Cursor** | `~\.cursor\mcp.json` |
| **Windsurf** | `~\.codeium\windsurf\mcp_server_config.json` |
| **VS Code + Cline** | VS Code globalStorage / `cline_mcp_settings.json` |
| **Zed** | `%APPDATA%\Zed\settings.json` (context_servers) |
| **Continue.dev** | `~\.continue\config.json` |

---

## What Every Agent Gets

Once activated, every coding agent has **4 new tools**:

```
list_skills()             → See all skills grouped by category
search_skills("churn")    → Find skills by keyword (ranked)
read_skill("git-internals-master")  → Load full SKILL.md instructions
reload_skills()           → Reload skills inside the agent
```

---

## Add a New Skill

```bash
# Generate boilerplate
python skill-creator/generate_skill.py 01-core-systems my-new-skill

# Edit SKILL.md, commit, push
git add . && git commit -m "add: my-new-skill" && git push

# Tell any agent to reload
# Agent calls: reload_skills()
```

---

## Deactivate

To remove the skills, simply uninstall the package and manually edit out the configuration from your agent's config file:

```bash
pip uninstall git-n-rust-skills
```

Removes `stageira-skills` from your machine.

---

## Test Without an Agent

```bash
python mcp_server/test_server.py
```

Verifies all SKILL.md files parse and the registry works.

---

## File Map

```
pyproject.toml          ← Package definition and data mappings
README.md               ← Main documentation
MCP-README.md           ← This file

mcp_server/
├── activator.py        ← Python script to inject into Claude/Cursor/Windsurf configs
├── server.py           ← MCP server (stdio, works with any MCP client)
├── skill_registry.py   ← Local filesystem scanner
└── test_server.py      ← Smoke test (no agent needed)

<skill-categories>/     ← E.g. 01-core-systems, containing SKILL.md files bundled into the install
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `git-n-rust-skills-activate: command not found` | Your pip install path isn't in your `PATH`. Alternatively, run `python -m mcp_server.activator`. |
| `ModuleNotFoundError: mcp` | The installation failed. Try running `pip install git+https://github.com/sVm19/git-n-rust-skills` again. |
| Skills not updating | Agent calls `reload_skills()` or restart the agent |

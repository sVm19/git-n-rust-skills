# git-n-rust-skills — Universal MCP Setup

> One command activates all your skills in **every** coding agent on your machine.

## Activate (Windows — all agents at once)

```powershell
# Local mode (reads from this folder)
.\activate.git-n-rust-skills.ps1

# GitHub mode (fetch from your repo — no local clone needed)
.\activate.git-n-rust-skills.ps1 -GithubRepo "yourusername/git-n-rust-skills"

# GitHub + private repo
.\activate.git-n-rust-skills.ps1 -GithubRepo "you/repo" -GithubToken "ghp_xxx"

# Preview changes without writing anything
.\activate.git-n-rust-skills.ps1 -GithubRepo "you/repo" -DryRun
```

## Activate (macOS / Linux)

```bash
# Local mode
bash activate.git-n-rust-skills.sh

# GitHub mode
bash activate.git-n-rust-skills.sh --github-repo yourusername/git-n-rust-skills

# Private repo
bash activate.git-n-rust-skills.sh --github-repo you/repo --token ghp_xxx
```

---

## Agents Supported

The script auto-detects which agents are installed and configures **all of them**:

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
reload_skills()           → Pull fresh skills from GitHub (no restart needed)
```

---

## GitHub Mode Flow

```
.\activate.git-n-rust-skills.ps1 -GithubRepo "alice/git-n-rust-skills"
         │
         ├─ Registers all agents with: python server.py --github-repo alice/...
         │
         └─ On every session start, MCP server:
              [1] GET github.com API → list of all SKILL.md paths (1 call)
              [2] GET raw.githubusercontent.com → content of each skill
              [3] Caches to ~/.cache/stageira-skills/
              [4] Serves to Claude / Cursor / Windsurf / etc.

You push a new SKILL.md → agent calls reload_skills() → done.
```

---

## Add a New Skill

```bash
# Generate boilerplate
python skill-creator/generate_skill.py 01-core-systems my-new-skill

# Edit SKILL.md, commit, push
git add . && git commit -m "add: my-new-skill" && git push

# Tell any agent to reload (no restart)
# Agent calls: reload_skills()
```

---

## Deactivate

```powershell
.\deactivate.git-n-rust-skills.ps1
```

Removes `stageira-skills` from all agent configs. No files deleted.

---

## Test Without an Agent

```powershell
python mcp_server/test_server.py
```

Verifies all SKILL.md files parse and the registry works.

---

## File Map

```
activate.git-n-rust-skills.ps1    ← Windows (all agents)
activate.git-n-rust-skills.sh     ← macOS / Linux (all agents)
deactivate.git-n-rust-skills.ps1  ← Remove from all agents

mcp_server/
├── server.py           ← MCP server (stdio, works with any MCP client)
├── skill_registry.py   ← Local filesystem scanner
├── github_registry.py  ← GitHub-backed registry (same interface)
├── github_fetcher.py   ← GitHub API + raw content fetcher with cache
├── test_server.py      ← Smoke test (no agent needed)
└── requirements.txt    ← mcp, pyyaml, pydantic
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Agent not detected | Run with `-DryRun` to see what would be configured |
| `ModuleNotFoundError: mcp` | `pip install mcp pyyaml` |
| GitHub rate limit hit | Add `-GithubToken` or set `GITHUB_TOKEN` env var |
| Skills not updating | Agent calls `reload_skills()` or restart the agent |
| 0 skills found on GitHub | Check repo is public, branch name is correct |

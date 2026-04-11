import json
import os
import sys
import platform
import shutil
import re
import textwrap
from pathlib import Path

def get_python_exe():
    return sys.executable

def install_codex_skills(home: Path) -> str:
    codex_skills_dir = home / ".codex" / "skills" / "git-n-rust-skills"
    
    # Locate skills root
    installed_data = Path(sys.prefix) / "git-n-rust-skills-data"
    if installed_data.exists():
        skills_root = installed_data
    else:
        skills_root = Path(__file__).parent.parent
        
    skill_files = []
    for d in skills_root.iterdir():
        if d.is_dir() and d.name[0].isdigit():
            skill_files.extend(list(d.rglob("*.md")))
            
    if not skill_files:
        return "[--] No skills found locally"
        
    try:
        if codex_skills_dir.exists():
            shutil.rmtree(codex_skills_dir)
        codex_skills_dir.mkdir(parents=True, exist_ok=True)
        
        for sf in skill_files:
            rel_path = sf.relative_to(skills_root)
            dest = codex_skills_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sf, dest)
            
        return f"[OK] Copied {len(skill_files)} skills"
    except Exception as e:
        return f"[FAIL] Error copying skills: {e}"


def _find_skills_root() -> Path:
    """Locate the directory containing numbered skill folders."""
    installed_data = Path(sys.prefix) / "git-n-rust-skills-data"
    if installed_data.exists():
        return installed_data
    return Path(__file__).parent.parent


def _parse_skill_frontmatter(skill_path: Path) -> dict:
    """Extract YAML-ish frontmatter from a SKILL.md file."""
    text = skill_path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {"name": skill_path.parent.name, "description": "", "body": text}
    block = m.group(1)
    meta = {"body": text[m.end():]}
    for line in block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"')
    meta.setdefault("name", skill_path.parent.name)
    meta.setdefault("description", "")
    return meta


def _collect_skills() -> list[dict]:
    """Return a list of {name, description, category, path, body} for every SKILL.md."""
    root = _find_skills_root()
    skills = []
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name[0].isdigit():
            for skill_md in d.rglob("SKILL.md"):
                meta = _parse_skill_frontmatter(skill_md)
                meta["category"] = d.name
                meta["path"] = str(skill_md)
                skills.append(meta)
    return skills


# ── Project-level generators ──────────────────────────────────────────

def init_claude_project(project_dir: Path) -> str:
    """Generate .claude/ directory with CLAUDE.md and per-skill rule files."""
    skills = _collect_skills()
    if not skills:
        return "[--] No skills found"

    rules_dir = project_dir / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    # Build the top-level CLAUDE.md
    lines = [
        "# Stageira Skills\n",
        "This project includes an AI skill library. "
        "Scoped rules live in `.claude/rules/` — Claude Code reads them automatically.\n",
        "## Available Skills\n",
    ]
    for s in skills:
        lines.append(f"- **{s['name']}** ({s['category']}): {s['description'][:120]}")

    lines.append("\n## How To Use\n")
    lines.append("Just describe what you need. Claude Code will match your request ")
    lines.append("to the right skill via the rule files in `.claude/rules/`.\n")

    claude_md = project_dir / "CLAUDE.md"
    claude_md.write_text("\n".join(lines), encoding="utf-8")

    # Write one rule file per skill
    for s in skills:
        safe_name = s["name"]
        rule_file = rules_dir / f"{safe_name}.md"
        rule_file.write_text(s["body"], encoding="utf-8")

    return f"[OK] CLAUDE.md + {len(skills)} rule files"


def init_codex_project(project_dir: Path) -> str:
    """Generate AGENTS.md + .codex/ directory with per-skill instruction files."""
    skills = _collect_skills()
    if not skills:
        return "[--] No skills found"

    codex_dir = project_dir / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)

    # Build the root AGENTS.md (Codex reads this automatically)
    lines = [
        "# Stageira Skills — Agent Instructions\n",
        "This project includes an AI skill library. "
        "Codex reads this file and the per-skill files inside `.codex/` automatically.\n",
        "## Skill Index\n",
    ]
    for s in skills:
        lines.append(f"- **{s['name']}** ({s['category']}): {s['description'][:120]}")
        lines.append(f"  → Full instructions: `.codex/{s['name']}.md`")

    lines.append("\n## How To Use\n")
    lines.append("Describe your task. The right skill will be matched automatically. ")
    lines.append("If you need a specific skill, reference its name directly.\n")

    agents_md = project_dir / "AGENTS.md"
    agents_md.write_text("\n".join(lines), encoding="utf-8")

    # Write one file per skill inside .codex/
    for s in skills:
        skill_file = codex_dir / f"{s['name']}.md"
        # Reconstruct the full SKILL.md content
        header = f"---\nname: {s['name']}\ndescription: {s['description']}\n---\n"
        skill_file.write_text(header + s["body"], encoding="utf-8")

    return f"[OK] AGENTS.md + {len(skills)} skill files"

def merge_mcp_config(config_path: Path, server_key: str, entry: dict):
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {"mcpServers": {}}
    else:
        config = {"mcpServers": {}}
        
    if "mcpServers" not in config:
        config["mcpServers"] = {}
        
    config["mcpServers"][server_key] = entry
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def merge_zed_config(config_path: Path, server_key: str, entry: dict):
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
    else:
        config = {}
        
    if "context_servers" not in config:
        config["context_servers"] = {}
        
    config["context_servers"][server_key] = entry
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="git-n-rust-skills activator")
    parser.add_argument("--init", metavar="DIR",
                        help="Generate .claude/ and .codex/ project-level skill dirs in DIR")
    args = parser.parse_args()

    print("")
    print("  +==================================================+")
    print("  |  git-n-rust-skills -- Universal MCP Activator   |")
    print("  +==================================================+")
    print("")

    # ── Project-level init (--init <dir>) ─────────────────────────────
    if args.init:
        project_dir = Path(args.init).resolve()
        print(f"[init] Generating project-level skill dirs in {project_dir}\n")

        claude_status = init_claude_project(project_dir)
        codex_status = init_codex_project(project_dir)

        print(f"  Claude Code  (.claude/)   {claude_status}")
        print(f"  Codex        (.codex/)    {codex_status}")
        print(f"\n  Files written to: {project_dir}")
        print("  Commit these to your repo so agents auto-discover them.\n")
        return
    
    python_exe = get_python_exe()
    
    # We use python -m mcp_server.server to ensure it is run in this exact python environment
    server_args = ["-m", "mcp_server.server"]
    env_vars = {}
    
    server_entry = {
        "command": python_exe,
        "args": server_args,
        "env": env_vars
    }
    
    zed_entry = {
        "command": {
            "path": python_exe,
            "args": server_args,
            "env": env_vars
        }
    }
    
    # ── Global MCP registration flow ────────────────────────────────
    print("[1/1] Detecting and registering with coding agents...\n")
    
    results = []
    
    # Paths depend on OS
    system = platform.system()
    home = Path.home()
    
    # Defaults for Windows
    appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    localappdata = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
    
    if system == "Darwin":
        claude_config = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        cursor_config = home / ".cursor" / "mcp.json"
        windsurf_config = home / ".codeium" / "windsurf" / "mcp_server_config.json"
        cline_config = home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        zed_config = home / ".config" / "zed" / "settings.json"
    elif system == "Linux":
        # Rough equivalents, Claude desktop unofficial
        claude_config = home / ".config" / "Claude" / "claude_desktop_config.json"
        cursor_config = home / ".cursor" / "mcp.json"
        windsurf_config = home / ".codeium" / "windsurf" / "mcp_server_config.json"
        cline_config = home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        zed_config = home / ".config" / "zed" / "settings.json"
    else: # Windows
        claude_config = appdata / "Claude" / "claude_desktop_config.json"
        cursor_config = home / ".cursor" / "mcp.json"
        windsurf_config = home / ".codeium" / "windsurf" / "mcp_server_config.json"
        cline_config = appdata / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        zed_config = appdata / "Zed" / "settings.json"

    # Claude Desktop
    if claude_config.parent.exists():
        merge_mcp_config(claude_config, "stageira-skills", server_entry)
        results.append(("Claude Desktop", "[OK] Registered", claude_config))
    else:
        results.append(("Claude Desktop", "[--] Not found", ""))
        
    # Cursor
    if cursor_config.parent.exists() or (home / ".cursor").exists():
        merge_mcp_config(cursor_config, "stageira-skills", server_entry)
        results.append(("Cursor", "[OK] Registered", cursor_config))
    else:
        results.append(("Cursor", "[--] Not found", ""))

    # Windsurf
    if windsurf_config.parent.exists() or (home / ".codeium" / "windsurf").exists():
        merge_mcp_config(windsurf_config, "stageira-skills", server_entry)
        results.append(("Windsurf", "[OK] Registered", windsurf_config))
    else:
        results.append(("Windsurf", "[--] Not found", ""))
        
    # VS Code Cline
    if cline_config.parent.parent.exists():
        merge_mcp_config(cline_config, "stageira-skills", server_entry)
        results.append(("VS Code / Cline", "[OK] Registered", cline_config))
    else:
        results.append(("VS Code / Cline", "[--] Not found", ""))
        
    # Zed
    if zed_config.parent.exists():
        merge_zed_config(zed_config, "stageira-skills", zed_entry)
        results.append(("Zed", "[OK] Registered", zed_config))
    else:
        results.append(("Zed", "[--] Not found", ""))

    # Codex (direct file copy, no MCP required)
    if (home / ".codex").exists():
        status = install_codex_skills(home)
        results.append(("Codex", status, home / ".codex" / "skills"))
    else:
        results.append(("Codex", "[--] Not found", ""))

    # Antigravity (Google Deepmind)
    antigravity_config = home / ".gemini" / "antigravity" / "mcp_config.json"
    if antigravity_config.parent.exists():
        merge_mcp_config(antigravity_config, "stageira-skills", server_entry)
        results.append(("Antigravity (Gemini)", "[OK] Registered", antigravity_config))
    else:
        results.append(("Antigravity (Gemini)", "[--] Not found", ""))

    # Continue.dev
    continue_config = home / ".continue" / "config.json"
    if continue_config.parent.exists():
        try:
            with open(continue_config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
        if "mcpServers" not in cfg:
            cfg["mcpServers"] = []
            
        mcp_servers = [s for s in cfg["mcpServers"] if isinstance(s, dict) and s.get("name") != "stageira-skills"]
        mcp_servers.append({
            "name": "stageira-skills",
            "command": python_exe,
            "args": server_args,
            "env": env_vars
        })
        cfg["mcpServers"] = mcp_servers
        
        continue_config.parent.mkdir(parents=True, exist_ok=True)
        with open(continue_config, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
            
        results.append(("Continue.dev", "[OK] Registered", continue_config))
    else:
        results.append(("Continue.dev", "[--] Not found", ""))

    print("  ==================================================")
    registered_count = sum(1 for r in results if "[OK]" in r[1])
    print(f"  DONE -- Registered with {registered_count} / {len(results)} agents")
    print("  ==================================================\n")
    
    for agent, status, path in results:
        print(f"  {agent:<20} {status}")
        
    print("\n  NEXT STEP: Restart all open editors/agents to activate.\n")

if __name__ == "__main__":
    main()

"""
server.py — Stageira Skills MCP Server

Supports two modes:
  --skills-root /path    Read SKILL.md files from local directory
  --github-repo u/repo   Fetch SKILL.md files from GitHub (with local cache)

Usage:
    # Local
    python server.py --skills-root C:/rust-git-skills

    # GitHub
    python server.py --github-repo alice/git-n-rust-skills

    # GitHub with specific branch
    python server.py --github-repo alice/git-n-rust-skills --branch develop
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print(
        "[stageira-skills] ERROR: 'mcp' package not found.\n"
        "Run: pip install mcp pyyaml\n"
        "Or run activate-skills.ps1 to install everything automatically.",
        file=sys.stderr,
    )
    sys.exit(1)

THIS_DIR = Path(__file__).parent
DEFAULT_SKILLS_ROOT = THIS_DIR.parent


# ── Registry factory — local or GitHub ───────────────────────────────────────

def build_registry(args):
    """Create the appropriate SkillRegistry based on CLI args."""
    if args.github_repo:
        from .github_registry import GitHubSkillRegistry
        parts = args.github_repo.split("/", 1)
        if len(parts) != 2:
            print(f"[stageira-skills] ERROR: --github-repo must be 'owner/repo', got: {args.github_repo}", file=sys.stderr)
            sys.exit(1)
        owner, repo = parts
        branch = getattr(args, "branch", "main") or "main"
        print(f"[stageira-skills] Mode: GitHub | {owner}/{repo}@{branch}", file=sys.stderr)
        return GitHubSkillRegistry(owner=owner, repo=repo, branch=branch)
    else:
        from .skill_registry import SkillRegistry
        root = Path(args.skills_root) if args.skills_root else DEFAULT_SKILLS_ROOT
        print(f"[stageira-skills] Mode: Local | {root}", file=sys.stderr)
        return SkillRegistry(root)


# ── MCP Server ────────────────────────────────────────────────────────────────

def create_server(registry) -> Server:
    server = Server("stageira-skills")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="list_skills",
                description=(
                    "List all available Stageira development skills. "
                    "Shows name, category, and description. "
                    "Call this first to find the right skill."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter by category, e.g. '01-core-systems'",
                        }
                    },
                    "required": [],
                },
            ),
            types.Tool(
                name="read_skill",
                description=(
                    "Read the full SKILL.md for a specific skill — all instructions, "
                    "code patterns, and examples. Use after list_skills() or search_skills()."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Skill name, e.g. 'git-internals-master'"},
                    },
                    "required": ["name"],
                },
            ),
            types.Tool(
                name="search_skills",
                description=(
                    "Search skills by keyword across names and descriptions. "
                    "Returns ranked results. Use when you know what you need but not the skill name."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keywords, e.g. 'code churn'"},
                        "max_results": {"type": "integer", "default": 5},
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="reload_skills",
                description=(
                    "Refresh skills from GitHub (or rescan local directory). "
                    "Use after pushing new SKILL.md files to your repo."
                ),
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

        if name == "list_skills":
            category_filter = (arguments.get("category") or "").lower()
            skills = registry.summary_list()
            if category_filter:
                skills = [s for s in skills if category_filter in s["category"].lower()]

            by_cat: dict[str, list] = {}
            for s in skills:
                by_cat.setdefault(s["category"], []).append(s)

            lines = [f"# Stageira Skills ({len(skills)} total)\n"]
            for cat, cat_skills in sorted(by_cat.items()):
                lines.append(f"\n## {cat}")
                for s in cat_skills:
                    compat = f"  `{s['compatibility']}`" if s.get("compatibility") else ""
                    lines.append(f"- **{s['name']}**{compat}")
                    lines.append(f"  {s['description']}")
            return [types.TextContent(type="text", text="\n".join(lines))]

        elif name == "read_skill":
            skill_name = (arguments.get("name") or "").strip()
            skill = registry.find_by_name(skill_name)
            if skill is None:
                matches = registry.search(skill_name, max_results=3)
                suggestions = ", ".join(f"`{m.name}`" for m in matches) if matches else "none"
                return [types.TextContent(
                    type="text",
                    text=f"Skill '{skill_name}' not found.\nClosest matches: {suggestions}\nUse list_skills() to browse all."
                )]
            content = skill.load_body()
            return [types.TextContent(
                type="text",
                text=f"# {skill.name}\n**{skill.category}/{skill.skill_folder}**\n\n---\n\n{content}"
            )]

        elif name == "search_skills":
            query = arguments.get("query", "")
            max_r = int(arguments.get("max_results", 5))
            results = registry.search(query, max_results=max_r)
            if not results:
                return [types.TextContent(type="text", text=f"No skills matched '{query}'. Try list_skills().")]
            lines = [f"# Results for '{query}'\n"]
            for s in results:
                lines.append(f"## {s.name}  ({s.category})")
                lines.append(s.description)
                lines.append(f"\n*Call `read_skill(\"{s.name}\")` for full details.*\n")
            return [types.TextContent(type="text", text="\n".join(lines))]

        elif name == "reload_skills":
            count = registry.reload()
            source = getattr(registry, 'source_label', 'local directory')
            return [types.TextContent(type="text", text=f"✅ Reloaded {count} skills from {source}")]

        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri=f"skill://{s.name}",
                name=s.name,
                description=s.short_description,
                mimeType="text/markdown",
            )
            for s in registry.skills
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        skill_name = uri.replace("skill://", "")
        skill = registry.find_by_name(skill_name)
        return skill.load_body() if skill else f"Not found: {skill_name}"

    return server


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Stageira Skills MCP Server")
    parser.add_argument("--skills-root", default=None, help="Local skills directory")
    parser.add_argument("--github-repo", default=None, help="GitHub repo: owner/repo-name")
    parser.add_argument("--branch", default="main", help="GitHub branch (default: main)")
    args, _ = parser.parse_known_args()

    registry = build_registry(args)
    server = create_server(registry)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

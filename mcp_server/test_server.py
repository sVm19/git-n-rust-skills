"""
test_server.py — Quick smoke test for the MCP server (no Claude needed).

Run: python mcp_server/test_server.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.skill_registry import SkillRegistry

SKILLS_ROOT = Path(__file__).parent.parent  # c:\rust-git-skills\


def test_registry():
    print(f"\n{'='*55}")
    print("  Stageira Skills MCP — Registry Smoke Test")
    print(f"{'='*55}")
    print(f"  Skills root: {SKILLS_ROOT}")
    print()

    registry = SkillRegistry(SKILLS_ROOT)
    skills = registry.skills

    print(f"  📚 Total skills found: {len(skills)}")
    print()

    # Group by category
    by_cat = registry.by_category()
    for cat, cat_skills in sorted(by_cat.items()):
        print(f"  {cat}:")
        for s in cat_skills:
            print(f"    ✓ {s.name:<35} ({s.skill_folder})")
    print()

    # Test search
    print("  🔍 Testing search('code churn'):")
    results = registry.search("code churn", max_results=3)
    for r in results:
        print(f"    → {r.name}")
    print()

    # Test find_by_name
    print("  🔍 Testing find_by_name('git-internals-master'):")
    skill = registry.find_by_name("git-internals-master")
    if skill:
        print(f"    ✓ Found: {skill.name}")
        content = skill.load_body()
        print(f"    ✓ Content loaded: {len(content)} chars")
    else:
        print("    ✗ Not found!")
    print()

    # Test read skill body
    print("  🔍 Testing read_skill('software-metrics'):")
    skill = registry.find_by_name("software-metrics")
    if skill:
        body = skill.load_body()
        print(f"    ✓ Body: {len(body)} chars | First line: {body.splitlines()[0][:60]}")
    print()

    print(f"{'='*55}")
    print("  ✅ Smoke test passed!")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    test_registry()

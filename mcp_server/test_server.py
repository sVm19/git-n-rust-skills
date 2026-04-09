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

    print(f"  Total skills found: {len(skills)}")
    print()

    # Group by category
    by_cat = registry.by_category()
    for cat, cat_skills in sorted(by_cat.items()):
        print(f"  {cat}:")
        for s in cat_skills:
            print(f"    [OK] {s.name:<35} ({s.skill_folder})")
    print()

    # Test search
    print("  Testing search('code churn'):")
    results = registry.search("code churn", max_results=3)
    for r in results:
        print(f"    -> {r.name}")
    print()

    # Test find_by_name
    print("  Testing find_by_name('git-internals-master'):")
    skill = registry.find_by_name("git-internals-master")
    if skill:
        print(f"    [OK] Found: {skill.name}")
    else:
        print("    [FAIL] Not found!")
    print()

    # Test read ALL skill bodies to ensure no parsing errors
    print("  Testing payload loading for ALL skills:")
    failed = 0
    for s in skills:
        try:
            body = s.load_body()
            if len(body) > 0:
                print(f"    [OK] {s.name:<30} -> {len(body):>6} bytes")
            else:
                print(f"    [FAIL] {s.name:<30} -> EMPTY BODY!")
                failed += 1
        except Exception as e:
            print(f"    [FAIL] {s.name:<30} -> ERROR: {e}")
            failed += 1
            
    if failed > 0:
        print(f"\n  [FAIL] {failed} skills failed to load properly.")
        sys.exit(1)
    else:
        print(f"\n  [OK] All {len(skills)} skills loaded perfectly.")

    print(f"{'='*55}")
    print("  [OK] Smoke test passed!")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    test_registry()

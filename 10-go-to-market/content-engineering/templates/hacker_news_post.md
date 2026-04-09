# Show HN: Stageira — Analyze your git history in 2 seconds, completely offline

Hey HN. I built a CLI tool that gives you code churn, bus factor, and contributor analytics on any git repo — without GitHub API access, OAuth tokens, or any internet connection.

## Why I built it

My last two jobs were at companies where GitHub Insights was blocked by InfoSec (financial services). Engineers wanted "which files change the most?" and "who's the single person who maintains this module?" — basic questions — and there was no tool that worked offline.

## How it works

Every git repo has a `.git/` folder. `libgit2` can read that directly. No API calls at any step:

```
.git/objects/ → libgit2 → Polars DataFrame → JSON/CSV
```

The entire pipeline runs in < 2 seconds on a 100K-commit repo (Rust binary, single executable).

## What it computes

- **Code churn**: files edited most frequently (bug risk signal)
- **Bus factor**: minimum authors needed for 50% ownership per file (key-person risk)
- **Temporal coupling**: files that always change together (hidden dependency detector)
- **Contributor distribution**: who's doing what, how evenly
- **Commit frequency trends**: compare Q1 vs Q2 velocity

## Current state

[describe your current release state here]

## Target

Enterprise security teams who can't use cloud-based analytics. But it's free for OSS projects.

Try it:

```bash
# Install
cargo install stageira  # or brew install stageira

# Run
stageira analyze /path/to/any/git/repo
```

Happy to answer questions about the technical implementation (the Polars + libgit2 combo is surprisingly fast).



# Project Architect — Blueprint Before You Build

Converts a raw project description into a precise, implementation-ready blueprint that every downstream skill can use without guessing.

## The Core Problem This Solves

Agents that start coding directly from a description will:
- Invent a directory structure that doesn't match the tech stack
- Pick dependencies that conflict
- Miss implicit requirements (auth, error handling, config management)
- Generate a module that has no clear owner or boundary

This skill forces a **full architecture pass before line 1 of code**.

---

## Phase 0 — Intake & Normalization

Before any analysis, normalize the input:

```
INPUT NORMALIZATION
===================
Input format detected:    [ ] Plain text  [ ] Markdown  [ ] Bullet list  [ ] Mixed
Approximate length:       ___ words
Language/domain:          e.g. "Rust CLI tool", "Python web API", "TypeScript fullstack app"
Explicit requirements:
  - ...
Implicit requirements (inferred):
  - ...
Missing information (must ask before proceeding):
  - ...
```

**Rule**: If critical information is missing (e.g. target OS, language, who the users are), ask exactly those questions — nothing else — before continuing.

---

## Phase 1 — Project Autopsy (read the description fully)

Extract every stated and implied decision:

```
PROJECT AUTOPSY
===============
Project name:         ...
One-line purpose:     What it does in one sentence
Core user action:     What does a user actually DO with this? (e.g. "runs a CLI command", "opens a dashboard")
Primary language:     ...
Runtime/platform:     ...

What it DOES:
  - ...

What it explicitly does NOT do (scope limit):
  - ...

Who uses it:
  - Primary: ...
  - Secondary: ...

Non-functional requirements (latency, offline, security, size):
  - ...

Distribution method:  binary / package / web app / library / ...
```

---

## Phase 2 — Technology Decision Record

For each tech decision, state the choice AND the reason. Lock the stack before touching structure.

```
TECHNOLOGY DECISION RECORD
===========================

Language:         [choice] — [reason in one line]
Build system:     [choice] — [reason]
Core libraries:   [lib] — [what it does] — [why not alternatives]
Test framework:   [choice] — [reason]
Config format:    [choice] — [reason]
Data format (IO): [choice] — [reason]
CI/CD:            [choice] — [reason]

REJECTED alternatives (document why, to prevent re-asking):
  - [rejected lib/tool] — rejected because: [reason]
```

---

## Phase 3 — Canonical Directory Structure

Produce the FULL tree. Every directory and file must have a one-line purpose.
Use this exact format so downstream skills (token-saver, task-orchestrator) can parse it.

```
PROJECT STRUCTURE: <ProjectName>
=================================

<project-root>/
├── src/
│   ├── main.rs              [ENTRY]  CLI entry point — parses args, dispatches subcommands
│   ├── lib.rs               [CORE]   Public API exposed to tests and integrations
│   ├── scanner/
│   │   ├── mod.rs           [CORE]   Git repository walker
│   │   └── commit.rs        [CORE]   Commit struct + parsing logic
│   ├── analytics/
│   │   ├── mod.rs           [CORE]   Aggregation orchestrator
│   │   ├── churn.rs         [CORE]   Code churn metric computation
│   │   └── bus_factor.rs    [CORE]   Bus factor computation
│   └── export/
│       ├── mod.rs           [SUPPORT] Export dispatcher
│       ├── json.rs          [SUPPORT] JSON serialization
│       └── csv.rs           [SUPPORT] CSV serialization
├── tests/
│   ├── integration/
│   │   └── analyze_test.rs  [TEST]   End-to-end CLI tests
│   └── fixtures/
│       └── sample_repo/     [TEST]   Minimal .git/ fixture for deterministic tests
├── Cargo.toml               [CONFIG] Dependencies, features, binary targets
├── Cargo.lock               [CONFIG] Pinned dependency tree (commit this)
├── README.md                [DOCS]   User-facing quickstart
├── SKILL.md                 [META]   This project's skill card (if applicable)
└── .github/
    └── workflows/
        └── ci.yml           [CI]     Build + test on push
```

**Rules for the tree:**
- Every leaf file gets a `[ROLE]` tag: `ENTRY`, `CORE`, `SUPPORT`, `TEST`, `CONFIG`, `DOCS`, `CI`, `META`
- No placeholder files — if a file appears in the tree, it has a real purpose
- Keep test fixtures minimal — one fixture repo per integration test suite

---

## Phase 4 — Module Dependency Graph

Show which modules import which. This prevents circular dependencies from being designed in.

```
MODULE DEPENDENCY GRAPH
=======================
Direction: A --> B means "A imports B"

main.rs
  --> scanner/mod.rs
  --> analytics/mod.rs
  --> export/mod.rs

scanner/mod.rs
  --> scanner/commit.rs

analytics/mod.rs
  --> analytics/churn.rs
  --> analytics/bus_factor.rs
  --> scanner/mod.rs      [reads scanner output as input]

export/mod.rs
  --> export/json.rs
  --> export/csv.rs
  --> analytics/mod.rs    [serializes analytics output]

CIRCULAR DEPENDENCY CHECK: [ ] None detected
```

---

## Phase 5 — Interface Contracts (APIs between modules)

Before any code is written, define what each module RECEIVES and RETURNS.
This is the contract every implementation task will be grounded in.

```
INTERFACE CONTRACTS
===================

scanner::scan(repo_path: &Path) -> Result<Vec<Commit>, ScanError>
  Input:  path to a .git directory or repo root
  Output: ordered list of Commit structs (newest first)
  Error:  ScanError::NotARepo | ScanError::PermissionDenied

analytics::compute(commits: &[Commit]) -> AnalyticsReport
  Input:  slice of Commit structs from scanner
  Output: AnalyticsReport { churn: f64, bus_factor: u32, ... }

export::write(report: &AnalyticsReport, format: ExportFormat, dest: &Path) -> Result<(), ExportError>
  Input:  computed report, target format (Json | Csv), output path
  Output: writes file, returns Ok(()) or error
```

---

## Phase 6 — Milestone Plan

Divide the build into milestones with clear "done" definitions.
Each milestone must be independently shippable.

```
MILESTONE PLAN
==============

Milestone 0 — Skeleton (Day 1)
  Goal:    Repo compiles, CI passes, no logic yet
  Done:    `cargo build` succeeds, `cargo test` runs 0 tests, CI is green
  Skills:  task-orchestrator (scaffold tasks)

Milestone 1 — Scanner (Day 2-3)
  Goal:    Can read commits from any local git repo
  Done:    `scanner::scan(".")` returns correct commit count on test fixture
  Skills:  git-internals-master, task-orchestrator

Milestone 2 — Analytics Core (Day 4-6)
  Goal:    Can compute churn and bus factor from commit data
  Done:    `analytics::compute(commits)` matches known values on fixture
  Skills:  data-processing-polars, software-metrics, task-orchestrator

Milestone 3 — Export (Day 7)
  Goal:    Can write JSON and CSV output
  Done:    `export::write(report, Json, "out.json")` produces valid JSON
  Skills:  task-orchestrator

Milestone 4 — CLI (Day 8-9)
  Goal:    Full end-to-end: `stageira analyze .` produces report
  Done:    Integration test passes on fixture repo
  Skills:  cli-design, task-orchestrator

Milestone 5 — Polish & Ship (Day 10)
  Goal:    README, release binary, CI publishes artifact
  Done:    GitHub Release created, binary runs on fresh machine
  Skills:  task-orchestrator
```

---

## Phase 7 — Skill Orchestration Plan

Map each milestone to the skills that will execute it.
This is the handoff document for `task-orchestrator`.

```
SKILL ORCHESTRATION
===================

Before coding anything:
  1. [THIS SKILL]        project-architect   → Produce this blueprint
  2. token-saver         → Scan any existing code before adding to it

For each milestone:
  3. task-orchestrator   → Decompose milestone into atomic agent tasks
  4. [domain skill]      → Execute the implementation (see milestone plan)
  5. task-orchestrator   → Verify milestone is done before proceeding

Recommended skill sequence for this project:
  M0: task-orchestrator
  M1: git-internals-master → task-orchestrator
  M2: data-processing-polars → software-metrics → task-orchestrator
  M3: task-orchestrator
  M4: cli-design → task-orchestrator
  M5: task-orchestrator
```

---

## Phase 8 — Risk Register

Before writing code, surface every risk that could invalidate the architecture.

```
RISK REGISTER
=============

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| libgit2 API surface differs from docs | Medium | High | Read git2-rs crate source before writing scanner |
| Polars Rust API != Python API | High | Medium | Use token-saver to read Polars Rust docs page first |
| Test fixture .git dir gets corrupted | Low | High | Commit fixture as binary, add integrity check in CI |
| Bus factor algorithm gives wrong results on repos with renames | Medium | Medium | Add rename-tracking flag as explicit config option |
```

---

## Output Checklist

Before handing off to `task-orchestrator`, verify:

- [ ] Phase 0 complete — all ambiguities resolved or explicit questions asked
- [ ] Phase 1 complete — every stated + implied requirement listed
- [ ] Phase 2 complete — tech stack locked with reasons
- [ ] Phase 3 complete — full directory tree with `[ROLE]` tags on every file
- [ ] Phase 4 complete — dependency graph shows no cycles
- [ ] Phase 5 complete — interface contracts defined for all public APIs
- [ ] Phase 6 complete — at least 3 independently-shippable milestones defined
- [ ] Phase 7 complete — every milestone mapped to specific skills
- [ ] Phase 8 complete — top risks documented with mitigations

**Do not pass this blueprint to `task-orchestrator` until all boxes are checked.**

---

## Example: Applying This Skill to the Stageira Project

**Input** (the project-plan.md or a short description like):
> "Build a local git repository analytics tool in Rust. Uses libgit2 to read .git directly.
> Outputs JSON/CSV. No network calls. Targets enterprises who can't use GitHub API."

**What this skill produces:**
- Phase 1: Extracts "local-first", "no OAuth", "single binary", "enterprise compliance" as hard requirements
- Phase 2: Locks `git2-rs + polars + clap + serde_json` — rejects `octocrab` (network), `gitpython` (Python runtime)
- Phase 3: The full `src/scanner/ | analytics/ | export/` tree above
- Phase 4: `analytics` depends on `scanner` output — no cycles
- Phase 5: `scan()` returns `Vec<Commit>`, `compute()` returns `AnalyticsReport`
- Phase 6: 5 milestones, each shippable independently
- Phase 7: `git-internals-master` handles M1, `data-processing-polars` handles M2
- Phase 8: "Polars Rust API != Python API" flagged as high-likelihood risk

Then `task-orchestrator` takes the Phase 6 + 7 output and decomposes each milestone into grounded agent prompts.

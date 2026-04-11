---
name: task-orchestrator
description: Read a project requirement carefully, decompose it into atomic sequential tasks, and write precise grounded prompts for each agent so they don't hallucinate. Use this skill BEFORE starting any multi-step coding work, feature implementation, or bug fix. Triggers whenever the user says "implement this", "build X", "add feature Y", "fix Z", or pastes a requirement, spec, or issue description with more than one moving part. Always run this skill first — it prevents agents from inventing APIs, hallucinating file paths, or drifting off-task.
---


# Task Orchestrator — Sequential Agent Decomposer

Prevents hallucination by grounding every agent task in facts before any code is written.

## Why Agents Hallucinate

Agents hallucinate when they are:
1. Given **vague goals** → they fill gaps with invented assumptions
2. Given **too much at once** → they lose track of constraints mid-task
3. Given **no verification step** → they don't know when to stop
4. Working on **files they haven't read** → they invent function signatures

This skill fixes all four by decomposing requirements into small, grounded, verifiable tasks.

---

## Phase 1 — Requirement Autopsy (do this before ANY decomposition)

Read the requirement and extract:

```
REQUIREMENT AUTOPSY
===================
What is explicitly stated:
  - [ ] ...

What is implied but not stated:
  - [ ] ...

What is unknown / needs to be looked up:
  - [ ] ...

Files that will be touched (verify these exist):
  - [ ] ...

Files that must NOT be touched:
  - [ ] ...

Definition of done (how will we know it's complete?):
  - [ ] ...

Risks of hallucination:
  - [ ] (e.g. "agent might invent a function that doesn't exist")
```

**Rule**: Do not write a single task until this autopsy is complete.

---

## Phase 2 — Task List (dependency-ordered)

Break the requirement into atomic tasks. Each task must:

- ✅ Have **one clear output** (a file change, a test result, a config update)
- ✅ Be **completable without guessing** (all needed context is specified)
- ✅ Have a **verification step** the agent can run itself
- ❌ Never span multiple concerns ("write the function AND update the tests AND change the config")

### Dependency ordering rule

```
If Task B needs something Task A produces → A comes before B.
If tasks can run independently → keep them separate but ordered.
Never order by "seems natural" — order by data flow.
```

### Task List Template

```
TASK LIST: <Requirement Title>
===============================
Total tasks: N
Estimated complexity: Low / Medium / High

Task 1: [Verify / Read phase]
Task 2: [Core implementation]
Task 3: [Integration / wiring]
Task 4: [Tests]
Task 5: [Verification]
```

---

## Phase 3 — Per-Task Agent Prompt

For each task, write a self-contained prompt using this template:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT TASK [N of TOTAL]: <Task Title>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONTEXT (read these files first, before any other action):
  - <file path> — reason you need it

WHAT YOU KNOW FOR CERTAIN:
  - <fact grounded in the codebase>
  - <fact grounded in the codebase>

YOUR ONE JOB:
  <single, precise action>

EXACT EXPECTED OUTPUT:
  - File: <path>
  - Change: <what changes — function added, line modified, etc.>
  - Nothing else changes.

DO NOT:
  - Do not create new files unless listed above
  - Do not call functions you haven't verified exist
  - Do not import modules not already in requirements.txt
  - Do not change <protected file>

VERIFY SUCCESS BY:
  1. <concrete check — e.g. "run python scanner.py . — should print commit count">
  2. <concrete check — e.g. "check no new imports appear in requirements.txt">

HAND OFF TO TASK [N+1]:
  Produce: <what the next agent needs from your output>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Anti-Hallucination Rules (enforce in every task)

### Rule 1 — Read Before Write
Every agent task must start with reading the files it will modify.
> "Before writing any code, read `src/scanner.py` fully."

### Rule 2 — Cite, Don't Invent
Every function call, class name, or import must be cited from a file already read.
> ❌ "Call `repo.get_commits()`" (invented)
> ✅ "Call `repo.iter_commits('HEAD')` — line 42 of scanner.py"

### Rule 3 — One Output Contract
Each task declares exactly one output. Agents that produce multiple outputs drift.
> ❌ "Update scanner.py and fix the tests and update the README"
> ✅ Task 2: "Add `iter_commits()` to scanner.py" | Task 3: "Update test_scanner.py"

### Rule 4 — Verify Before Handoff
Every task ends with a concrete verification step the agent runs itself.
> "Run `python mcp_server/test_server.py` — must print ✅ before marking done."

### Rule 5 — Explicit Scope Fence
Every task says what is OUT OF SCOPE.
> "Do not modify `exporter.py`. Do not change any test files."

---

## Example: Decomposing a Real Stageira Feature

**Requirement**: "Add temporal coupling to the analyze command output"

### Requirement Autopsy

```
What is stated:    Add temporal coupling metric to `analyze` CLI output
What is implied:   It needs to appear in JSON export too
What is unknown:   Does temporal_coupling.py already exist? What's its API?
Files to touch:    temporal_coupling.py, analytics.py, commands/analyze.py, exporter.py
Files to protect:  scanner.py, tests/ (don't break existing tests)
Definition of done: `stageira analyze .` JSON includes "temporal_coupling" key
Hallucination risk: Agent might invent function signature for temporal_coupling()
```

### Task List

```
Task 1: Read & map existing code         ← no writes, pure discovery
Task 2: Verify temporal_coupling.py API  ← read only
Task 3: Wire into analytics.py           ← one function call added
Task 4: Add to exporter.py              ← one key added to JSON output
Task 5: Expose in analyze command        ← one line in analyze.py
Task 6: Verify end-to-end               ← run stageira analyze, check JSON
```

### Task 1 Prompt (example)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT TASK [1 of 6]: Read & Map Existing Code

CONTEXT (read these, nothing else):
  - 02-analytics-engineering/software-metrics/src/temporal_coupling.py
  - 01-core-systems/data-processing-polars/src/analytics.py
  - 03-cli-devx/cli-design/src/commands/analyze.py

YOUR ONE JOB:
  Report the exact public API (function names + signatures) of each file above.
  Do not write any code.

EXACT EXPECTED OUTPUT:
  A markdown list of function names, their parameters, and return types
  from each of the 3 files. Nothing else.

DO NOT:
  - Do not modify anything
  - Do not run any code
  - Do not read any other files

VERIFY SUCCESS BY:
  Confirm you have listed at least one function from each of the 3 files.

HAND OFF TO TASK 2:
  Produce: function signatures for temporal_coupling(), compute_churn(), and the analyze command body
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Sequencing Checklist

Before handing tasks to agents, verify:

- [ ] Task 1 is always a **read-only discovery task** (never write first)
- [ ] Each task has exactly **one output** named explicitly
- [ ] No task references a function not verified in a prior task
- [ ] Every task has a `VERIFY SUCCESS BY` step that can be run programmatically
- [ ] `DO NOT` section covers the most likely hallucination in that task
- [ ] Handoff clause connects each task's output to the next task's input
- [ ] Final task is always a **full end-to-end verification**

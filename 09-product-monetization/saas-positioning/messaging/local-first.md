---
name: saas-positioning
description: Craft messaging and positioning strategy for Stageira as a local-first, non-SaaS developer tool. Use when writing marketing copy, explaining to customers why Stageira is better than GitHub Insights or CodeClimate, creating pitch decks, pricing pages, or any messaging about privacy, speed, and compliance. Triggers on "marketing", "positioning", "why local-first", "competitive advantage", "pitch", "messaging", "vs GitHub Insights", "vs SonarQube".
---

# SaaS Positioning — Local-First Messaging

Stageira is NOT a SaaS tool. This is its superpower. Here's how to communicate that.

## The One-Line Pitch

> "Analyze your entire git history in 2 seconds, completely offline. No OAuth. No API tokens. No data leaves your machine."

## Positioning vs Competitors

| Them | Stageira Advantage |
|------|-------------------|
| **GitHub Insights** | Works on GitLab, Bitbucket, internal repos — not just GitHub |
| **CodeClimate** | No code scanning = no data sent out. Air-gap compatible. |
| **SonarQube** | 10x faster, single binary, no Java runtime, no server to maintain |
| **git-quick-stats** | Real data science (Polars DataFrames), not bash scripts |

## Message by Audience

### For Enterprise Security Teams

> "Every commit in your codebase lives in `.git/`. Stageira reads that folder directly — the same data your Git client reads every day. Nothing is transmitted. Our source code is open for audit."

### For Engineering Managers

> "Get bus factor, code churn, and contributor stats for your entire history in under 2 seconds. No dashboards to set up. No integrations to configure. Just `stageira analyze .`"

### For Compliance Officers

> "Zero data exfiltration. Works in air-gapped environments. No OAuth grants, no API keys, no third-party access. Our compliance checker script runs in your CI pipeline."

### For Developers (Technical)

> "It's libgit2 + Polars in a single binary. Reads `.git/objects/` directly. No GitHub API rate limits. Works on any git repo — GitHub, GitLab, Bitbucket, or self-hosted."

## Feature Tier Messaging

```
Free  → "Start in 30 seconds. No signup."
Pro   → "Every metric your board meeting needs."  
Enterprise → "The analytics tool your security team will actually approve."
```

## Objection Responses

| Objection | Response |
|-----------|----------|
| "Git has insights built in" | "git log is not analytics. Stageira gives you trend lines, anomaly detection, and bus factor risk scores — in 2 seconds." |
| "We'll build it internally" | "Our core is open source. You'll end up rebuilding a Polars analytics engine + CLI + export system. The maintenance cost > subscription cost." |
| "GitHub Insights covers us" | "Only if everything is on GitHub. 35% of enterprises use GitLab or self-hosted. And GitHub Insights doesn't work air-gapped." |

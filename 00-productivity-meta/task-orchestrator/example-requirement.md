# chore: add temporal coupling to analyze command output

## Requirement

When a user runs `stageira analyze .`, the JSON output should include a
`temporal_coupling` key containing the top 20 file pairs that change together
most frequently.

This is a Pro-tier feature. It must not break the existing `churn` and
`bus_factor` outputs. Should respect the `window_days` config.

## Acceptance Criteria

1. `stageira analyze . --format json` includes `"temporal_coupling": [...]`
2. Each entry has `file_a`, `file_b`, `co_change_count`
3. No existing tests break
4. Runs in < 2s on a 10K-commit repo

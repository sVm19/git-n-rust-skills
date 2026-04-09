# [TITLE: Choose one]
# "How We Computed Code Churn on 1 Million Commits Without GitHub API"
# "The Hidden Cost of Bus Factor: A Data-Driven Analysis"
# "Why libgit2 + Polars is the Best Stack for Git Analytics"

## Introduction

[Hook: start with the pain point — security teams blocking SaaS tools, or a surprising metric you found]

## The Problem

Engineering teams need git analytics but can't use cloud-based tools due to:
- Compliance requirements (HIPAA, SOC2, PCI-DSS)
- Air-gapped environments (defense, finance)
- No GitHub API access (GitLab, Bitbucket, self-hosted)

## The Technical Approach

### Reading .git/ directly

Every git repository stores its entire history in `.git/objects/`. Using `libgit2`, we can read this without any network calls:

```rust
let repo = git2::Repository::open(".").unwrap();
let mut revwalk = repo.revwalk().unwrap();
revwalk.push_head().unwrap();

for oid in revwalk {
    let commit = repo.find_commit(oid.unwrap()).unwrap();
    // process commit data...
}
```

### Analytics with Polars

Once we have commit records, Polars DataFrames make aggregation efficient:

```python
churn = (
    df.explode("files_changed")
    .group_by("files_changed")
    .agg(pl.len().alias("edit_count"))
    .sort("edit_count", descending=True)
)
```

## Results

[Insert benchmark: X commits analyzed in Y seconds on Z hardware]

## What We Learned

[3-5 interesting findings from running this on open source repos]

## Conclusion

[Call to action: try Stageira, star on GitHub, etc.]

---
*Stageira is open source. Try it: `cargo install stageira`*

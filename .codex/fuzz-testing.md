---
name: fuzz-testing
description: Apply fuzz testing to Stageira's git parsing code using cargo-fuzz (Rust) and Hypothesis (Python). Use when hardening edge cases in the scanner, handling malformed .git/ directories, testing with corrupted commit data, or preparing for production release. Triggers on "fuzz", "cargo-fuzz", "edge cases", "malformed git", "corrupted repo", "hypothesis testing", or "security hardening".
---


# Fuzz Testing — Stageira Reliability

Stageira reads untrusted `.git/` directories in enterprise environments. Fuzz testing finds the edge cases that unit tests miss.

> ⚠️ `cargo-fuzz` requires nightly Rust. Pin it separately from the stable build.

## cargo-fuzz (Rust)

```bash
# Install
cargo install cargo-fuzz

# Initialize fuzz targets (run once)
cargo fuzz init

# Add a target
cargo fuzz add fuzz_git_scanner
```

### Fuzz target for git object parsing

```rust
// fuzz/fuzz_targets/fuzz_git_scanner.rs
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // Write random bytes to a temp dir and try to parse as git repo
    if let Ok(tmpdir) = tempfile::tempdir() {
        let git_dir = tmpdir.path().join(".git");
        let objects_dir = git_dir.join("objects");
        let _ = std::fs::create_dir_all(&objects_dir);
        
        // Write fuzz input as a fake git object
        if let Ok(_) = std::fs::write(objects_dir.join("fuzz_object"), data) {
            // Must not panic — just return an error
            let _ = stageira::scanner::scan_repo(tmpdir.path().to_str().unwrap());
        }
    }
});
```

```bash
# Run fuzz (with nightly)
rustup override set nightly
cargo fuzz run fuzz_git_scanner -- -max_total_time=60

# Minimize a corpus
cargo fuzz tmin fuzz_git_scanner <crash_file>
```

## Hypothesis (Python)

```python
# src/git_fuzzer.py
from hypothesis import given, settings, strategies as st
import polars as pl
from stageira.analytics import compute_churn, compute_bus_factor
from datetime import datetime

# Strategy: generate random commit-like records
commit_strategy = st.fixed_dictionaries({
    "sha": st.text(alphabet="0123456789abcdef", min_size=40, max_size=40),
    "author": st.text(min_size=1, max_size=100),
    "email": st.emails(),
    "timestamp": st.datetimes(min_value=datetime(2000, 1, 1)),
    "files_changed": st.lists(
        st.text(min_size=1, max_size=200),
        min_size=0,
        max_size=50,
    ),
    "insertions": st.integers(min_value=0, max_value=100_000),
    "deletions": st.integers(min_value=0, max_value=100_000),
})

@given(st.lists(commit_strategy, min_size=0, max_size=200))
@settings(max_examples=500, deadline=5000)
def test_churn_never_crashes(commits):
    """compute_churn must not raise on any valid commit structure."""
    if not commits:
        return
    df = pl.DataFrame(commits)
    try:
        result = compute_churn(df)
        assert isinstance(result, pl.DataFrame)
    except Exception as e:
        # Only schema errors are acceptable, not logic crashes
        assert "schema" in str(e).lower() or "null" in str(e).lower()

@given(st.lists(commit_strategy, min_size=1, max_size=100))
@settings(max_examples=200)
def test_bus_factor_bounded(commits):
    """Bus factor must always be >= 1."""
    df = pl.DataFrame(commits)
    result = compute_bus_factor(df)
    if len(result) > 0 and "bus_factor" in result.columns:
        assert result["bus_factor"].min() >= 1
```

```bash
# Run Hypothesis tests
pytest src/git_fuzzer.py -v --hypothesis-show-statistics
```

## Edge Cases to Always Test

| Case | Expected behavior |
|------|-----------------|
| Empty repository (0 commits) | Return empty metrics, exit 0 |
| Root commit (no parent) | No diff computed, no crash |
| Binary files in diff | Skip gracefully |
| Very long author names (>1000 chars) | Truncate or handle |
| Commits with no files changed | Include in frequency, 0 churn |
| Identical timestamps (clock skew) | Sort deterministically |
| Repo with only merge commits | `--first-parent` handles it |
| Unicode in file paths | Handle correctly (Rust: use `OsStr`) |

## CI Integration

```yaml
# In .github/workflows/test.yml, add:
  fuzz:
    name: Fuzz (nightly, 60s)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@nightly
      - run: cargo install cargo-fuzz
      - run: cargo fuzz run fuzz_git_scanner -- -max_total_time=60
```

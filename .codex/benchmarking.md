---
name: benchmarking
description: Measure and optimize Stageira's runtime performance and memory usage. Use when profiling slow analysis runs, measuring if the <2s target is met, tracking memory consumption on large repos, or writing benchmark scripts. Triggers on "benchmark", "profiling", "memory usage", "performance measurement", "how fast is", "2 second target", or "optimize speed".
---


# Benchmarking — Stageira Performance Measurement

**Target**: Analyze a 100K-commit repo in < 2 seconds with < 500MB memory.

## Python Profiling

```python
# src/profiler.py
import time
import cProfile
import pstats
from io import StringIO
from pathlib import Path

def profile_analysis(repo_path: str, output_html: Path = None):
    """Profile the full analysis pipeline and report top bottlenecks."""
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    # --- run the thing being profiled ---
    from .scanner import scan_repo
    from .analytics import compute_all_metrics
    
    t0 = time.perf_counter()
    records = scan_repo(repo_path)
    scan_time = time.perf_counter() - t0
    
    t1 = time.perf_counter()
    metrics = compute_all_metrics(records)
    analyze_time = time.perf_counter() - t1
    
    profiler.disable()
    
    # Report
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(20)
    
    print(f"\n⏱  Scan:    {scan_time:.3f}s")
    print(f"⏱  Analyze: {analyze_time:.3f}s")
    print(f"⏱  Total:   {scan_time + analyze_time:.3f}s")
    print(f"\nTop 20 functions:\n{stream.getvalue()}")
```

## Memory Tracking

```python
# src/memory_tracker.py
import tracemalloc
import gc

def track_memory(func, *args, **kwargs):
    """Measure peak memory usage of a function call."""
    gc.collect()
    tracemalloc.start()
    
    result = func(*args, **kwargs)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"📦 Memory: current={current/1024/1024:.1f}MB, peak={peak/1024/1024:.1f}MB")
    return result
```

## Cargo Benchmarks (Rust)

```rust
// benches/scan_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use stageira::scanner::scan_repo;

fn bench_scan(c: &mut Criterion) {
    c.bench_function("scan_100k_commits", |b| {
        b.iter(|| {
            scan_repo(black_box("/path/to/large-repo"))
                .expect("scan failed")
        })
    });
}

criterion_group!(benches, bench_scan);
criterion_main!(benches);
```

```bash
cargo bench
# Results in target/criterion/
```

## Benchmark Runner Script

```bash
#!/usr/bin/env bash
# run.sh benchmark mode
REPO="${1:-/path/to/test-repo}"
RUNS=5

echo "Benchmarking Stageira on: $REPO"
echo "Runs: $RUNS"
echo "---"

total=0
for i in $(seq 1 $RUNS); do
    t=$( { time stageira analyze "$REPO" --quiet; } 2>&1 | grep real | awk '{print $2}' )
    echo "Run $i: $t"
done
```

## Target Benchmarks

| Repo Size | Target Time | Target Memory |
|-----------|-------------|---------------|
| 1K commits | < 0.1s | < 50MB |
| 10K commits | < 0.5s | < 100MB |
| 100K commits | < 2.0s | < 500MB |
| 1M commits | < 30s | < 2GB |

## Optimization Checklist

- [ ] Run `cargo bench` and identify hotspots
- [ ] Profile Python layer with `cProfile`
- [ ] Check memory with `tracemalloc` — peak < 500MB for 100K commits
- [ ] Ensure no unnecessary `.collect()` calls in Polars chains
- [ ] Verify `--first-parent` is used for merge-heavy repos
- [ ] Confirm streaming is used for export (not full in-memory buffer)

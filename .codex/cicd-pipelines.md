---
name: cicd-pipelines
description: Set up and configure GitHub Actions and GitLab CI pipelines for Stageira: multi-platform Rust builds, automated testing, coverage reports, and crates.io releases. Use when working on .github/workflows/, adding CI jobs, setting up cross-compilation, configuring release automation, or troubleshooting pipeline failures. Triggers on \"github actions\", \"CI pipeline\", \"workflow\", \"release automation\", \"cross-compile\", \"cargo-release\".
---


# CI/CD Pipelines for Stageira

Stageira runs in enterprise CI/CD behind firewalls — so the release pipeline must be airtight and the binary must be self-contained.

## Pipeline Overview

```
Push to main branch:
└── test.yml         → cargo test (Linux + macOS + Windows)

Push tag v*:
└── release.yml      → cross-compile → GitHub Release → crates.io publish
```

## test.yml — Test on Every Push

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test:
    name: Test on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
      
      - name: Cache cargo
        uses: Swatinem/rust-cache@v2
      
      - name: Build
        run: cargo build --all-features
      
      - name: Test
        run: cargo test --all-features
  
  coverage:
    name: Coverage (Linux only)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - name: Install tarpaulin
        run: cargo install cargo-tarpaulin
      - name: Coverage
        run: cargo tarpaulin --out Xml --all-features
      - name: Upload to Codecov
        uses: codecov/codecov-action@v3
```

## release.yml — Cross-Compile and Publish

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags: ["v*"]

jobs:
  build:
    name: Build ${{ matrix.target }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu
          - os: ubuntu-latest
            target: aarch64-unknown-linux-gnu
          - os: macos-latest
            target: x86_64-apple-darwin
          - os: macos-latest
            target: aarch64-apple-darwin
          - os: windows-latest
            target: x86_64-pc-windows-msvc
    
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}
      
      - name: Install cross (for Linux ARM)
        if: matrix.target == 'aarch64-unknown-linux-gnu'
        run: cargo install cross
      
      - name: Build
        run: |
          if [[ "${{ matrix.target }}" == "aarch64-unknown-linux-gnu" ]]; then
            cross build --release --target ${{ matrix.target }}
          else
            cargo build --release --target ${{ matrix.target }}
          fi
        shell: bash
      
      - name: Package
        run: |
          cd target/${{ matrix.target }}/release
          tar -czf stageira-${{ matrix.target }}.tar.gz stageira*
      
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: stageira-${{ matrix.target }}
          path: target/${{ matrix.target }}/release/stageira-*.tar.gz
  
  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: "**/*.tar.gz"
          generate_release_notes: true
      
      - name: Publish to crates.io
        run: cargo publish --token ${{ secrets.CRATES_IO_TOKEN }}
```

## cargo-release Setup

```toml
# release.toml
sign-commit = false
sign-tag = false
push = true
publish = true
pre-release-commit-message = "chore: prepare release {{version}}"
tag-message = "Release {{version}}"
```

```bash
# Bump patch version, create tag, push
cargo release patch --execute

# Bump minor (new feature)
cargo release minor --execute
```

## Key Warnings (from project-plan.md)

- `cargo-tarpaulin` → Linux only, always run on `ubuntu-latest`
- `cargo-fuzz` → requires nightly; pin separately: `rustup override set nightly`
- `cross-rs` → needs Docker on the runner; `ubuntu-latest` runners support this
- Polars Rust API ≠ Python API — most online examples are Python

---
name: distribution
description: Handle Stageira's package distribution: publishing to crates.io, creating Homebrew tap formulas, and managing GitHub Releases. Use when preparing a release, writing a homebrew formula, setting up crates.io publishing, bump versions with cargo-release, or cross-compiling for multiple platforms. Triggers on \"publish\", \"crates.io\", \"homebrew\", \"distribution\", \"release\", \"cross-compile\", \"package\".
---


# Distribution — Publishing Stageira

## Release Workflow

```
1. cargo release patch/minor/major --execute  → bumps version, tags, pushes
2. GitHub Actions release.yml triggers        → cross-compiles 5 targets
3. GitHub Release created automatically       → with release notes
4. Publish to crates.io                       → developers can `cargo install stageira`
5. Update Homebrew tap                        → macOS users can `brew install stageira`
```

## crates.io Publishing

```bash
# First time: login
cargo login <your-token>

# Publish (automated in CI via CRATES_IO_TOKEN secret)
cargo publish

# Check before publishing
cargo publish --dry-run
```

**Cargo.toml metadata required:**

```toml
[package]
name = "stageira"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <you@example.com>"]
description = "Local-first git repository analytics. No GitHub API required."
license = "MIT OR Apache-2.0"
repository = "https://github.com/yourusername/stageira"
homepage = "https://stageira.dev"
documentation = "https://docs.rs/stageira"
keywords = ["git", "analytics", "metrics", "cli", "developer-tools"]
categories = ["command-line-utilities", "development-tools"]
readme = "README.md"
```

## Homebrew Formula

```ruby
# src/homebrew_formula.rb
# Formula for: brew install stageira
class Stageira < Formula
  desc "Local-first git repository analytics. No GitHub API required."
  homepage "https://stageira.dev"
  version "0.1.0"
  
  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/yourusername/stageira/releases/download/v#{version}/stageira-aarch64-apple-darwin.tar.gz"
      sha256 "REPLACE_WITH_SHA256"
    else
      url "https://github.com/yourusername/stageira/releases/download/v#{version}/stageira-x86_64-apple-darwin.tar.gz"
      sha256 "REPLACE_WITH_SHA256"
    end
  end
  
  on_linux do
    url "https://github.com/yourusername/stageira/releases/download/v#{version}/stageira-x86_64-unknown-linux-gnu.tar.gz"
    sha256 "REPLACE_WITH_SHA256"
  end
  
  def install
    bin.install "stageira"
  end
  
  test do
    system "#{bin}/stageira", "--version"
  end
end
```

**Publish to Homebrew tap:**

```bash
# Create your tap
brew tap-new yourusername/stageira

# After formula is ready
brew install --build-from-source ./stageira.rb
brew audit --strict stageira
brew test stageira
```

## PyPI Publishing (Python analytics layer)

```python
# src/pypi_publish.py
"""Helper script to build and publish the Python package."""
import subprocess
import sys

def publish():
    subprocess.run([sys.executable, "-m", "build"], check=True)
    subprocess.run([sys.executable, "-m", "twine", "upload", "dist/*"], check=True)

if __name__ == "__main__":
    publish()
```

## Version Bump Checklist

- [ ] `cargo release minor --execute` (or `patch` / `major`)
- [ ] CI passes on all platforms
- [ ] GitHub Release created with binaries attached
- [ ] SHA256 hashes computed for Homebrew formula
- [ ] Homebrew formula updated and tested
- [ ] `CHANGELOG.md` updated
- [ ] Announce on HN / LinkedIn / Discord

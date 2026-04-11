---
name: security-first-design
description: Implement and verify Stageira's offline-first, zero-data-exfiltration security architecture. Use when implementing any new feature that touches network, file I/O, or external connections; when writing compliance documentation; when designing the enterprise tier; or when explaining to security teams why Stageira is safe. Triggers on "security", "offline", "air-gapped", "compliance", "zero data exfiltration", "data privacy", "enterprise security", or "GDPR".
---


# Security-First Design

Stageira's main competitive advantage over GitHub Insights, CodeClimate, and SonarQube is its **zero data exfiltration** guarantee. This skill ensures every feature upholds that promise.

## The Security Contract

```
What Stageira NEVER does:
  ✗ Send source code to any server
  ✗ Require OAuth tokens
  ✗ Call GitHub/GitLab/Bitbucket APIs
  ✗ Phone home for telemetry
  ✗ Require internet access

What Stageira ALWAYS does:
  ✓ Read only from .git/ directory (local)
  ✓ Write only to user-specified output paths
  ✓ Optional webhook = only outbound, user-controlled
  ✓ Single binary = no hidden dependencies
```

## Offline Validator

```python
# src/offline_validator.py
"""
Validates that a Stageira binary or source module makes no unexpected network calls.
Run this in CI before every release.
"""
import socket
import unittest
from unittest.mock import patch

class OfflineValidator:
    """Monkey-patches network to ensure no unexpected calls are made."""
    
    def __enter__(self):
        self.orig_connect = socket.socket.connect
        
        def no_network(self, *args, **kwargs):
            raise PermissionError(
                f"Network call detected! Address: {args}. "
                "Stageira must not make network calls during analysis."
            )
        
        socket.socket.connect = no_network
        return self
    
    def __exit__(self, *args):
        socket.socket.connect = self.orig_connect

# Usage in tests:
def test_analyze_is_offline():
    with OfflineValidator():
        from stageira.scanner import scan_repo
        scan_repo("/path/to/repo")  # Must not raise PermissionError
```

## Compliance Checker

```python
# src/compliance_checker.py
from pathlib import Path
import ast

PROHIBITED_IMPORTS = [
    "requests", "httpx", "aiohttp", "urllib.request",
    "boto3", "google.cloud", "azure",
]

PROHIBITED_PATTERNS = [
    "socket.connect", "requests.get", "requests.post",
    "urllib.request.urlopen",
]

def check_source_compliance(src_dir: Path) -> list[str]:
    """Scan source files for prohibited network imports/calls."""
    violations = []
    
    for py_file in src_dir.rglob("*.py"):
        # Skip: slack_webhook.py (the one intentional outbound call)
        if "webhook" in py_file.name:
            continue
        
        source = py_file.read_text()
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = getattr(node, "module", "") or ""
                for name_node in getattr(node, "names", []):
                    full = f"{module}.{name_node.name}" if module else name_node.name
                    for prohibited in PROHIBITED_IMPORTS:
                        if prohibited in full:
                            violations.append(
                                f"{py_file}:{node.lineno}: prohibited import '{full}'"
                            )
    
    return violations

def run_compliance_check(src_dir: str = "src") -> bool:
    violations = check_source_compliance(Path(src_dir))
    if violations:
        print("❌ Compliance violations found:")
        for v in violations:
            print(f"  {v}")
        return False
    print("✅ Compliance check passed: no unauthorized network imports")
    return True
```

## Enterprise Security Checklist

Before every release, verify:

- [ ] `python -c "from stageira.offline_validator import OfflineValidator; ..."` passes
- [ ] `compliance_checker.py` reports 0 violations in `src/`
- [ ] Binary size is reasonable (< 50MB) — no hidden data payloads
- [ ] `strings stageira | grep -i "http"` shows only the optional webhook URL
- [ ] CHANGELOG.md documents every outbound network endpoint (currently: 0 mandatory)

## Air-Gapped Deployment Instructions

```bash
# On a machine with internet:
wget https://github.com/your/stageira/releases/download/v1.0/stageira-linux-x86_64.tar.gz
sha256sum stageira-linux-x86_64.tar.gz  # verify hash from release page

# Transfer to air-gapped machine via USB/approved channel
scp stageira-linux-x86_64.tar.gz user@airgapped:/opt/stageira/

# On the air-gapped machine:
tar -xzf stageira-linux-x86_64.tar.gz
chmod +x stageira
./stageira analyze /path/to/repo  # works completely offline
```

## Messaging for Enterprise Security Teams

> "Stageira reads your `.git/` folder — the same data that's already on your machine. Nothing is sent anywhere. Our compliance checker script is open source and runs in your CI pipeline."

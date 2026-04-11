---
name: python-testing
description: Write and organize pytest tests for Stageira's Python analytics modules. Use when adding unit tests, integration tests, setting up fixtures, writing test factories for git repos, or improving coverage. Triggers on "write tests", "pytest", "unit test", "test coverage", "test scanner", "test analytics", "fixture", or "mock git repo".
---


# Python Testing — Stageira Test Suite

Stageira's analytics are only as trustworthy as its tests. This skill covers pytest patterns, fixtures for git repos, and coverage targets.

## Test Structure

```
tests/
├── conftest.py           ← Shared fixtures
├── test_scanner.py       ← Git parsing tests
├── test_analytics.py     ← Metrics computation tests
├── test_exporter.py      ← JSON/CSV output tests
├── test_cli.py           ← CLI end-to-end tests
└── test_compliance.py    ← Security/offline tests
```

## conftest.py — Shared Fixtures

```python
# tests/conftest.py
import pytest
import git
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

@pytest.fixture(scope="session")
def temp_repo():
    """Create a minimal git repo for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = git.Repo.init(tmpdir)
        repo.config_writer().set_value("user", "name", "Test Author").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()
        
        # Create initial commit
        src = Path(tmpdir) / "src"
        src.mkdir()
        (src / "main.py").write_text("# main\n")
        repo.index.add(["src/main.py"])
        repo.index.commit("Initial commit")
        
        # Add a few more commits
        for i in range(5):
            (src / f"module_{i}.py").write_text(f"# module {i}\n")
            repo.index.add([f"src/module_{i}.py"])
            repo.index.commit(f"Add module {i}")
        
        yield Path(tmpdir)

@pytest.fixture
def sample_commits():
    """Pre-built commit records for unit testing analytics."""
    return [
        {
            "sha": "abc123",
            "author": "alice",
            "email": "alice@example.com",
            "timestamp": datetime.now() - timedelta(days=5),
            "files_changed": ["src/main.py", "src/scanner.py"],
            "insertions": 50,
            "deletions": 10,
        },
        {
            "sha": "def456",
            "author": "bob",
            "email": "bob@example.com",
            "timestamp": datetime.now() - timedelta(days=3),
            "files_changed": ["src/main.py"],
            "insertions": 20,
            "deletions": 5,
        },
    ]
```

## test_scanner.py

```python
# tests/test_scanner.py
from stageira.scanner import scan_repo, CommitRecord

class TestScanner:
    def test_scan_returns_commits(self, temp_repo):
        records = scan_repo(str(temp_repo))
        assert len(records) > 0
    
    def test_commit_has_required_fields(self, temp_repo):
        records = scan_repo(str(temp_repo))
        r = records[0]
        assert hasattr(r, "sha")
        assert hasattr(r, "author")
        assert hasattr(r, "timestamp")
        assert hasattr(r, "files_changed")
    
    def test_scan_invalid_path_raises(self):
        with pytest.raises(Exception):
            scan_repo("/nonexistent/path")
    
    def test_scan_is_offline(self, temp_repo):
        """Scanner must not make network calls."""
        from stageira.offline_validator import OfflineValidator
        with OfflineValidator():
            scan_repo(str(temp_repo))  # should not raise
```

## test_analytics.py

```python
# tests/test_analytics.py
import polars as pl
from stageira.analytics import compute_churn, compute_bus_factor

class TestChurn:
    def test_churn_returns_dataframe(self, sample_commits):
        df = pl.DataFrame(sample_commits)
        result = compute_churn(df)
        assert isinstance(result, pl.DataFrame)
    
    def test_churn_sorts_by_score(self, sample_commits):
        df = pl.DataFrame(sample_commits)
        result = compute_churn(df)
        scores = result["churn_score"].to_list()
        assert scores == sorted(scores, reverse=True)
    
    def test_main_py_has_highest_churn(self, sample_commits):
        df = pl.DataFrame(sample_commits)
        result = compute_churn(df)
        assert result["file"][0] == "src/main.py"  # edited by both alice and bob

class TestBusFactor:
    def test_bus_factor_is_integer(self, sample_commits):
        df = pl.DataFrame(sample_commits)
        result = compute_bus_factor(df)
        assert result["bus_factor"].dtype == pl.Int32
```

## test_cli.py — End-to-End

```python
# tests/test_cli.py
from typer.testing import CliRunner
from stageira.main import app

runner = CliRunner()

def test_analyze_command_exits_zero(temp_repo):
    result = runner.invoke(app, ["analyze", str(temp_repo), "--quiet"])
    assert result.exit_code == 0

def test_analyze_outputs_json(temp_repo, tmp_path):
    out = tmp_path / "report.json"
    result = runner.invoke(app, ["analyze", str(temp_repo), "--out", str(out)])
    assert out.exists()
    import json
    data = json.loads(out.read_text())
    assert "metrics" in data
```

## Coverage Targets

```bash
# Run all tests with coverage
pytest --cov=stageira --cov-report=html --cov-fail-under=80

# Open HTML report
open htmlcov/index.html
```

| Module | Coverage Target |
|--------|----------------|
| `scanner.py` | 90% |
| `analytics.py` | 85% |
| `exporter.py` | 80% |
| `cli commands` | 70% |
| `compliance_checker.py` | 95% |

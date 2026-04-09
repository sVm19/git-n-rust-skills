"""Tests for git-internals-master scanner."""
import tempfile
from pathlib import Path
import pytest
import git


@pytest.fixture(scope="module")
def temp_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = git.Repo.init(tmpdir)
        repo.config_writer().set_value("user", "name", "Test").release()
        repo.config_writer().set_value("user", "email", "test@test.com").release()
        p = Path(tmpdir) / "file.py"
        p.write_text("# initial\n")
        repo.index.add(["file.py"])
        repo.index.commit("Initial commit")
        yield Path(tmpdir)


class TestScanner:
    def test_scan_returns_records(self, temp_repo):
        from src.scanner import scan_repo
        records = scan_repo(str(temp_repo))
        assert len(records) >= 1

    def test_commit_fields_present(self, temp_repo):
        from src.scanner import scan_repo
        r = scan_repo(str(temp_repo))[0]
        assert r.sha
        assert r.author_name
        assert isinstance(r.files_changed, list)

    def test_invalid_path_raises(self):
        from src.scanner import scan_repo
        import git
        with pytest.raises(Exception):
            scan_repo("/nonexistent/repo")

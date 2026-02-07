"""Unit tests for scripts/supervisor_loop.py (stdlib unittest)."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from supervisor_loop import infer_allowed_globs, parse_owner_repo  # noqa: E402


class TestSupervisorLoop(unittest.TestCase):
    def test_parse_owner_repo_https(self):
        self.assertEqual(parse_owner_repo("https://github.com/owner/repo"), "owner/repo")
        self.assertEqual(parse_owner_repo("https://github.com/owner/repo.git"), "owner/repo")

    def test_parse_owner_repo_ssh(self):
        self.assertEqual(parse_owner_repo("git@github.com:owner/repo.git"), "owner/repo")

    def test_parse_owner_repo_owner_repo(self):
        self.assertEqual(parse_owner_repo("owner/repo"), "owner/repo")

    def test_parse_owner_repo_invalid(self):
        with self.assertRaises(ValueError):
            parse_owner_repo("owner")

    def test_infer_allowed_globs_explicit(self):
        issue = {"title": "x", "body": "Allowed paths: docs/**, README.md"}
        self.assertEqual(infer_allowed_globs(issue), ["docs/**", "README.md"])

    def test_infer_allowed_globs_backticks(self):
        issue = {"title": "Update `README.md` and `scripts/a.py`", "body": ""}
        self.assertEqual(infer_allowed_globs(issue), ["README.md", "scripts/a.py"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

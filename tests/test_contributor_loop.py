"""Unit tests for scripts/contributor_loop.py (stdlib unittest)."""

from pathlib import Path
import os
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from contributor_loop import build_work_command, resolve_allow_patterns  # noqa: E402


class TestContributorLoop(unittest.TestCase):
    def test_resolve_allow_patterns_uses_scope_and_work_dir(self):
        task = {"scope": {"allowed_globs": ["src/**", "README.md"]}}
        self.assertEqual(resolve_allow_patterns(task), ["src/**", "README.md", "work/**"])

    def test_build_work_command_default_is_python_not_touch(self):
        old = os.environ.pop("AGENT_EXEC_CMD", None)
        try:
            cmd, summary = build_work_command("issue-1", Path("work/requests/issue-1.json"))
            self.assertEqual(cmd[0], sys.executable)
            self.assertIn("-c", cmd)
            self.assertIn("placeholder artifact", summary)
        finally:
            if old is not None:
                os.environ["AGENT_EXEC_CMD"] = old

    def test_build_work_command_uses_hook(self):
        old = os.environ.get("AGENT_EXEC_CMD")
        os.environ["AGENT_EXEC_CMD"] = "echo run {task_id} with {task_file}"
        try:
            cmd, summary = build_work_command("issue-2", Path("work/requests/issue-2.json"))
            if os.name == "nt":
                self.assertIn("/c", cmd)
            else:
                self.assertIn("-lc", cmd)
            self.assertIn("issue-2", summary)
            self.assertIn("work/requests/issue-2.json", summary.replace("\\", "/"))
        finally:
            if old is None:
                del os.environ["AGENT_EXEC_CMD"]
            else:
                os.environ["AGENT_EXEC_CMD"] = old


if __name__ == "__main__":
    unittest.main(verbosity=2)

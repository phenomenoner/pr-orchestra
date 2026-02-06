"""Unit tests for scripts/create_next_tasks.py (stdlib unittest)."""

from pathlib import Path
import sys
import unittest

# Make scripts importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from create_next_tasks import (  # noqa: E402
    build_issue_payload,
    load_tasks_from_json,
    normalize_labels,
    parse_markdown_tasks,
    parse_repo,
)


class TestCreateNextTasks(unittest.TestCase):
    def test_parse_markdown_tasks(self):
        md = """
        ## Task One
        Do the thing.

        ## Task Two
        - Bullet A
        - Bullet B
        """
        tasks = parse_markdown_tasks(md)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["title"], "Task One")
        self.assertIn("Do the thing", tasks[0]["body"])
        self.assertEqual(tasks[1]["title"], "Task Two")
        self.assertIn("Bullet A", tasks[1]["body"])

    def test_parse_markdown_tasks_requires_heading(self):
        with self.assertRaises(ValueError):
            parse_markdown_tasks("No headings here")

    def test_load_tasks_from_json_list(self):
        data = [{"title": "T1", "body": "B1"}, {"title": "T2"}]
        tasks = load_tasks_from_json(data)
        self.assertEqual([t["title"] for t in tasks], ["T1", "T2"])

    def test_load_tasks_from_json_object(self):
        data = {"tasks": [{"title": "T1", "labels": ["x"]}]}
        tasks = load_tasks_from_json(data)
        self.assertEqual(tasks[0]["labels"], ["x"])

    def test_build_issue_payload_merges_labels(self):
        payload = build_issue_payload(
            {"title": "T1", "labels": ["custom", "agent-task"]},
            ["agent-task"],
        )
        self.assertEqual(payload["title"], "T1")
        self.assertEqual(payload["labels"], ["agent-task", "custom"])

    def test_parse_repo(self):
        self.assertEqual(parse_repo("owner/repo"), ("owner", "repo"))
        self.assertEqual(parse_repo("https://github.com/owner/repo"), ("owner", "repo"))
        with self.assertRaises(ValueError):
            parse_repo("invalid")

    def test_normalize_labels(self):
        self.assertEqual(
            normalize_labels(["agent-task", ""], ["custom", "agent-task", "custom"]),
            ["agent-task", "custom"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

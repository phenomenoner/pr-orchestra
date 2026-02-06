"""Unit tests for scripts/meeting_packet.py (stdlib unittest)."""

from pathlib import Path
import sys
import unittest

# Make scripts importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from meeting_packet import (  # noqa: E402
    PRPacketItem,
    build_questions,
    detect_dependencies,
    detect_missing_sections,
    recommended_order,
)


class TestMeetingPacket(unittest.TestCase):
    def test_detect_missing_sections_none_missing(self):
        body = """
        ## Intent
        fix bug

        ## Approach
        changed X

        ## Risk/Impact
        low

        ## Test Plan
        - python -m unittest

        ## Docs/Notes
        updated readme
        """
        self.assertEqual(detect_missing_sections(body), [])

    def test_detect_missing_sections_partial(self):
        body = """
        ## Intent
        text

        ## Approach
        text
        """
        missing = detect_missing_sections(body)
        self.assertIn("Risk/Impact", missing)
        self.assertIn("Test Plan", missing)
        self.assertIn("Docs/Notes", missing)

    def test_detect_dependencies(self):
        body = "depends on #12 and blocked by #9 then after #12"
        self.assertEqual(detect_dependencies(body), [9, 12])

    def test_build_questions(self):
        qs = build_questions(["Test Plan"], "failure", "L2", [33])
        joined = "\n".join(qs)
        self.assertIn("missing PR section", joined)
        self.assertIn("CI is failing", joined)
        self.assertIn("rollback", joined)
        self.assertIn("#33", joined)

    def test_recommended_order_prefers_green_low_risk_non_draft(self):
        items = [
            PRPacketItem(
                number=2,
                title="B",
                url="",
                author="a",
                draft=False,
                labels=[],
                ci_state="success",
                files_changed=2,
                additions=20,
                deletions=2,
                risk_level="L1",
                risk_reasons=[],
                missing_sections=[],
                questions=[],
            ),
            PRPacketItem(
                number=1,
                title="A",
                url="",
                author="a",
                draft=False,
                labels=[],
                ci_state="pending",
                files_changed=1,
                additions=5,
                deletions=1,
                risk_level="L0",
                risk_reasons=[],
                missing_sections=[],
                questions=[],
            ),
            PRPacketItem(
                number=3,
                title="C",
                url="",
                author="a",
                draft=True,
                labels=[],
                ci_state="success",
                files_changed=1,
                additions=1,
                deletions=0,
                risk_level="L0",
                risk_reasons=[],
                missing_sections=[],
                questions=[],
            ),
        ]

        ordered = recommended_order(items)
        self.assertEqual([x.number for x in ordered], [2, 1, 3])


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Tests for the File Organizer Agent skeleton.

Run from the project root:
    python -m unittest discover -s tests -v
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from organizer import OrganizerAgent, classify


class TestClassify(unittest.TestCase):
    def test_known_extensions(self):
        self.assertEqual(classify("photo.jpg"), "Images")
        self.assertEqual(classify("report.pdf"), "Documents")
        self.assertEqual(classify("backup.zip"), "Archives")
        self.assertEqual(classify("main.py"), "Code")

    def test_extension_is_case_insensitive(self):
        self.assertEqual(classify("PHOTO.JPG"), "Images")

    def test_unknown_and_missing_extensions_go_to_others(self):
        self.assertEqual(classify("mystery.xyz"), "Others")
        self.assertEqual(classify("noextension"), "Others")


class TestAgentRunOnce(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="organizer_test_"))
        for name in ["a.jpg", "b.txt", "c.mp3"]:
            (self.dir / name).write_text("x", encoding="utf-8")
        self.agent = OrganizerAgent(self.dir)

    def test_files_land_in_category_folders(self):
        self.agent.run_once()
        self.assertTrue((self.dir / "Images" / "a.jpg").exists())
        self.assertTrue((self.dir / "Documents" / "b.txt").exists())
        self.assertTrue((self.dir / "Audio" / "c.mp3").exists())
        # nothing loose left behind except the log
        loose = [p.name for p in self.dir.iterdir() if p.is_file()]
        self.assertEqual(loose, ["organizer_log.txt"])

    def test_never_overwrites_existing_destination(self):
        (self.dir / "Images").mkdir()
        (self.dir / "Images" / "a.jpg").write_text("ORIGINAL", encoding="utf-8")
        actions = self.agent.run_once()
        # the existing file is untouched and the new one stayed put
        self.assertEqual(
            (self.dir / "Images" / "a.jpg").read_text(encoding="utf-8"), "ORIGINAL"
        )
        self.assertTrue((self.dir / "a.jpg").exists())
        self.assertTrue(any(a.startswith("SKIPPED a.jpg") for a in actions))

    def test_every_action_is_logged(self):
        self.agent.run_once()
        log = (self.dir / "organizer_log.txt").read_text(encoding="utf-8")
        self.assertIn("MOVED a.jpg -> Images/", log)
        self.assertIn("MOVED b.txt -> Documents/", log)
        self.assertIn("MOVED c.mp3 -> Audio/", log)


if __name__ == "__main__":
    unittest.main()

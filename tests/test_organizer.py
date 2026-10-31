"""Tests for the File Organizer Agent.

Run from the project root:
    python -m unittest discover -s tests -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from organizer import OrganizerAgent, classify


def make_agent(files=(), config=None):
    """Fresh temp folder + agent. files: names to create inside."""
    folder = Path(tempfile.mkdtemp(prefix="organizer_test_"))
    if config is not None:
        (folder / "rules.json").write_text(json.dumps(config), encoding="utf-8")
    for name in files:
        (folder / name).write_text("x", encoding="utf-8")
    return folder, OrganizerAgent(folder)


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

    def test_name_rules_beat_extension_rules(self):
        self.assertEqual(classify("invoice_march.pdf"), "Finance")
        self.assertEqual(classify("invoice_photo.jpg"), "Finance")
        self.assertEqual(classify("screenshot_01.png"), "Images")


class TestRunOnce(unittest.TestCase):
    def test_files_land_in_category_folders(self):
        folder, agent = make_agent(["a.jpg", "b.txt", "c.mp3"])
        agent.run_once()
        self.assertTrue((folder / "Images" / "a.jpg").exists())
        self.assertTrue((folder / "Documents" / "b.txt").exists())
        self.assertTrue((folder / "Audio" / "c.mp3").exists())
        loose = [p.name for p in folder.iterdir() if p.is_file()]
        self.assertEqual(loose, ["organizer_log.txt"])

    def test_never_overwrites_existing_destination(self):
        folder, agent = make_agent(["a.jpg"])
        (folder / "Images").mkdir()
        (folder / "Images" / "a.jpg").write_text("ORIGINAL", encoding="utf-8")
        actions = agent.run_once()
        self.assertEqual(
            (folder / "Images" / "a.jpg").read_text(encoding="utf-8"), "ORIGINAL"
        )
        self.assertTrue((folder / "a.jpg").exists())
        self.assertTrue(any(a.startswith("SKIPPED a.jpg") for a in actions))

    def test_every_action_is_logged(self):
        folder, agent = make_agent(["a.jpg", "b.txt", "c.mp3"])
        agent.run_once()
        log = (folder / "organizer_log.txt").read_text(encoding="utf-8")
        self.assertIn("MOVED a.jpg -> Images/a.jpg", log)
        self.assertIn("MOVED b.txt -> Documents/b.txt", log)
        self.assertIn("MOVED c.mp3 -> Audio/c.mp3", log)

    def test_agent_never_moves_its_own_config(self):
        folder, agent = make_agent(
            ["a.jpg"], config={"categories": {"Pics": [".jpg"]}}
        )
        agent.run_once()
        self.assertTrue((folder / "rules.json").exists())  # stayed put
        self.assertTrue((folder / "Pics" / "a.jpg").exists())


class TestDryRun(unittest.TestCase):
    def test_dry_run_moves_nothing_but_logs(self):
        folder, agent = make_agent(["a.jpg"])
        actions = agent.run_once(dry_run=True)
        self.assertTrue((folder / "a.jpg").exists())
        self.assertFalse((folder / "Images").exists())
        self.assertTrue(actions[0].startswith("WOULD MOVE a.jpg"))
        log = (folder / "organizer_log.txt").read_text(encoding="utf-8")
        self.assertIn("WOULD MOVE a.jpg", log)


class TestAskMode(unittest.TestCase):
    def setUp(self):
        self.folder, self.agent = make_agent(["a.jpg"])
        (self.folder / "Images").mkdir()
        (self.folder / "Images" / "a.jpg").write_text("ORIGINAL", encoding="utf-8")

    def test_ask_rename_keeps_both_files(self):
        self.agent.run_once(ask=True, input_fn=lambda prompt: "r")
        self.assertEqual(
            (self.folder / "Images" / "a.jpg").read_text(encoding="utf-8"),
            "ORIGINAL",
        )
        self.assertTrue((self.folder / "Images" / "a (1).jpg").exists())

    def test_ask_overwrite_replaces_only_on_request(self):
        self.agent.run_once(ask=True, input_fn=lambda prompt: "o")
        self.assertEqual(
            (self.folder / "Images" / "a.jpg").read_text(encoding="utf-8"), "x"
        )

    def test_ask_skip_leaves_everything(self):
        self.agent.run_once(ask=True, input_fn=lambda prompt: "s")
        self.assertTrue((self.folder / "a.jpg").exists())
        self.assertEqual(
            (self.folder / "Images" / "a.jpg").read_text(encoding="utf-8"),
            "ORIGINAL",
        )


class TestUndo(unittest.TestCase):
    def test_undo_restores_the_mess(self):
        folder, agent = make_agent(["a.jpg", "b.txt"])
        agent.run_once()
        agent.undo()
        self.assertTrue((folder / "a.jpg").exists())
        self.assertTrue((folder / "b.txt").exists())

    def test_second_undo_does_not_redo(self):
        folder, agent = make_agent(["a.jpg"])
        agent.run_once()
        agent.undo()
        notes = agent.undo()
        self.assertTrue((folder / "a.jpg").exists())
        self.assertFalse(any(n.startswith("UNDID") for n in notes))

    def test_undo_skips_files_that_are_gone(self):
        folder, agent = make_agent(["a.jpg"])
        agent.run_once()
        (folder / "Images" / "a.jpg").unlink()
        notes = agent.undo()
        self.assertTrue(notes[0].startswith("UNDO SKIPPED a.jpg"))


class TestConfigAndSafety(unittest.TestCase):
    def test_custom_categories_from_rules_json(self):
        folder, agent = make_agent(
            ["game.exe"], config={"categories": {"Games": [".exe"]}}
        )
        agent.run_once()
        self.assertTrue((folder / "Games" / "game.exe").exists())

    def test_dangerous_category_is_rejected(self):
        with self.assertRaises(ValueError):
            make_agent(config={"categories": {"../evil": [".jpg"]}})

    def test_missing_folder_is_rejected(self):
        with self.assertRaises(NotADirectoryError):
            OrganizerAgent(Path(tempfile.gettempdir()) / "no_such_folder_xyz")

    def test_renamed_files_can_be_undone(self):
        folder, agent = make_agent(["a.jpg"])
        (folder / "Images").mkdir()
        (folder / "Images" / "a.jpg").write_text("ORIGINAL", encoding="utf-8")
        agent.run_once(ask=True, input_fn=lambda prompt: "r")
        agent.undo()
        self.assertTrue((folder / "a.jpg").exists())
        self.assertEqual(
            (folder / "Images" / "a.jpg").read_text(encoding="utf-8"), "ORIGINAL"
        )


class TestWatch(unittest.TestCase):
    def test_watch_stops_cleanly_on_keyboard_interrupt(self):
        folder, agent = make_agent()
        calls = {"n": 0}

        def fake_run_once(**kwargs):
            calls["n"] += 1
            if calls["n"] >= 3:
                raise KeyboardInterrupt
            return []

        agent.run_once = fake_run_once
        agent.watch(interval=0)  # must return, not raise
        self.assertEqual(calls["n"], 3)


if __name__ == "__main__":
    unittest.main()

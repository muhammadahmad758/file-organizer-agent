"""The File Organizer Agent.

A real agent loop in miniature — the same shape as big agent systems:

    PERCEIVE  -> look at the world (which files are in the folder?)
    DECIDE    -> choose an action for each thing perceived (which folder?)
    ACT       -> do it (move the file) — safely, never overwriting
    LOG       -> write down what was decided and done, every time

The skeleton's run_once() does one full loop over the folder.
Watch mode, dry-run, undo and smarter rules are YOUR extension tasks —
see EXTEND.md.
"""

import shutil
from dataclasses import dataclass
from pathlib import Path

from .rules import classify


@dataclass
class OrganizerAgent:
    watch_dir: Path
    log_file: Path = None  # default: <watch_dir>/organizer_log.txt

    def __post_init__(self):
        self.watch_dir = Path(self.watch_dir)
        if self.log_file is None:
            self.log_file = self.watch_dir / "organizer_log.txt"
        else:
            self.log_file = Path(self.log_file)

    # -- PERCEIVE ---------------------------------------------------------
    def perceive(self):
        """Return the files currently sitting in watch_dir.

        Folders are ignored (they are the destinations, not inputs),
        and so is the agent's own log file.
        """
        return [
            p
            for p in sorted(self.watch_dir.iterdir())
            if p.is_file() and p != self.log_file
        ]

    # -- DECIDE -----------------------------------------------------------
    def decide(self, file_path):
        """Return (category, destination_path) for one perceived file."""
        category = classify(file_path.name)
        destination = self.watch_dir / category / file_path.name
        return category, destination

    # -- ACT --------------------------------------------------------------
    def act(self, file_path, destination):
        """Move file_path to destination. Returns True if moved.

        Safety rule: NEVER overwrite. If the destination already exists,
        do nothing and return False — the caller logs it as skipped.
        """
        if destination.exists():
            return False
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(destination))
        return True

    # -- LOG --------------------------------------------------------------
    def log(self, message):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    # -- THE LOOP (one pass) ----------------------------------------------
    def run_once(self):
        """One full perceive -> decide -> act -> log cycle.

        Returns the list of action notes, one per file.
        """
        actions = []
        for file_path in self.perceive():
            category, destination = self.decide(file_path)
            if self.act(file_path, destination):
                note = f"MOVED {file_path.name} -> {category}/"
            else:
                note = f"SKIPPED {file_path.name} (already exists in {category}/)"
            self.log(note)
            actions.append(note)
        return actions

    # -- EXTENSION POINTS (your tasks, see EXTEND.md) ----------------------
    # Task 1: def watch(self, interval=2.0) — loop run_once() + sleep,
    #         stop cleanly on Ctrl+C.
    # Task 3: teach decide() name-based rules that run BEFORE the
    #         extension rules (e.g. "invoice" in the name -> Finance).
    # Task 4: def undo(self) — read the log backwards, move MOVED files back.

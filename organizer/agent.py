"""The File Organizer Agent.

A real agent loop in miniature — the same shape as big agent systems:

    PERCEIVE  -> look at the world (which files are in the folder?)
    DECIDE    -> choose an action for each thing perceived (which folder?)
    ACT       -> do it (move the file) — safely, never overwriting
    LOG       -> write down what was decided and done, every time

Features:
  * run_once()   one full loop over the folder
  * watch()      keep looping, organizing new files as they appear
  * dry_run      decide + log without moving anything (safe testing)
  * ask mode     on a name clash: ask overwrite / rename / skip
  * undo()       reverse the moves recorded in the log
  * rules.json   optional config file in the watched folder that
                 replaces the built-in classification rules

Safety rules (enforced, and covered by tests):
  * Never overwrites an existing file unless the user explicitly
    chooses "overwrite" in ask mode.
  * Never moves its own log file or its rules.json config.
  * Refuses to act on a watch folder that does not exist.
  * A rules.json with a dangerous category name (containing path
    separators or "..") is rejected — destinations can never escape
    the watched folder.
  * A file that disappears mid-run is logged as VANISHED, not a crash.
"""

import json
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from .rules import NAME_RULES, RULES, classify

LOG_NAME = "organizer_log.txt"
CONFIG_NAME = "rules.json"


def _validate_rules(categories, name_rules):
    """Reject rule tables that could send files outside the folder."""
    for category, extensions in categories.items():
        _validate_category(category)
        for ext in extensions:
            if not isinstance(ext, str) or not ext.startswith(".") or "/" in ext:
                raise ValueError(f"Invalid extension in rules: {ext!r}")
    for keyword, category in name_rules.items():
        if not isinstance(keyword, str) or not keyword:
            raise ValueError(f"Invalid name-rule keyword: {keyword!r}")
        _validate_category(category)


def _validate_category(category):
    if (
        not isinstance(category, str)
        or not category
        or category in {".", ".."}
        or "/" in category
        or "\\" in category
    ):
        raise ValueError(f"Unsafe category name in rules: {category!r}")


@dataclass
class OrganizerAgent:
    watch_dir: Path
    log_file: Path = None  # default: <watch_dir>/organizer_log.txt
    rules: dict = field(default=None, repr=False)
    name_rules: dict = field(default=None, repr=False)

    def __post_init__(self):
        self.watch_dir = Path(self.watch_dir)
        if not self.watch_dir.is_dir():
            raise NotADirectoryError(
                f"Watch folder does not exist: {self.watch_dir}"
            )
        self.log_file = (
            self.watch_dir / LOG_NAME if self.log_file is None else Path(self.log_file)
        )
        self.config_file = self.watch_dir / CONFIG_NAME
        loaded_rules, loaded_name_rules = self._load_config()
        self.rules = loaded_rules if self.rules is None else self.rules
        self.name_rules = (
            loaded_name_rules if self.name_rules is None else self.name_rules
        )
        _validate_rules(self.rules, self.name_rules)

    # -- CONFIG -------------------------------------------------------------
    def _load_config(self):
        """Load rules from <watch_dir>/rules.json if present.

        Format:
            {"categories": {"Images": [".jpg", ".png"]},
             "name_rules": {"invoice": "Finance"}}
        Either key may be omitted. A malformed file raises ValueError —
        failing loudly beats silently organizing by the wrong rules.
        """
        if not self.config_file.exists():
            return RULES, NAME_RULES
        try:
            data = json.loads(self.config_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid {CONFIG_NAME}: {exc}") from exc
        categories = data.get("categories")
        if categories is None:
            rules = RULES
        else:
            rules = {
                category: {ext.lower() for ext in extensions}
                for category, extensions in categories.items()
            }
        name_rules = data.get("name_rules", NAME_RULES)
        return rules, name_rules

    # -- PERCEIVE -----------------------------------------------------------
    def perceive(self):
        """Return the files currently sitting in watch_dir.

        Folders are ignored (they are destinations, not inputs), and so
        are the agent's own log and config files.
        """
        own_files = {self.log_file, self.config_file}
        return [
            p
            for p in sorted(self.watch_dir.iterdir())
            if p.is_file() and p not in own_files
        ]

    # -- DECIDE -------------------------------------------------------------
    def decide(self, file_path):
        """Return (category, destination_path) for one perceived file."""
        category = classify(file_path.name, self.rules, self.name_rules)
        destination = self.watch_dir / category / file_path.name
        return category, destination

    # -- ACT ----------------------------------------------------------------
    def _check_destination(self, destination):
        """True only if destination stays inside the watched folder."""
        root = self.watch_dir.resolve()
        parent = destination.parent.resolve()
        return parent == root or root in parent.parents

    def act(self, file_path, destination):
        """Move file_path to destination. Returns True if moved.

        Never overwrites: returns False if the destination exists or
        would escape the watched folder.
        """
        if destination.exists() or not self._check_destination(destination):
            return False
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(destination))
        return True

    @staticmethod
    def _free_name(destination):
        """photo.jpg -> photo (1).jpg -> photo (2).jpg ... first free one."""
        stem, suffix = destination.stem, destination.suffix
        counter = 1
        candidate = destination
        while candidate.exists():
            candidate = destination.with_name(f"{stem} ({counter}){suffix}")
            counter += 1
        return candidate

    # -- LOG ------------------------------------------------------------------
    def log(self, message):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    # -- THE LOOP (one pass) --------------------------------------------------
    def run_once(self, dry_run=False, ask=False, input_fn=input):
        """One full perceive -> decide -> act -> log cycle.

        dry_run=True: decide and log ("WOULD MOVE ...") but move nothing.
        ask=True: when a destination already exists, ask via input_fn
        whether to overwrite, rename, or skip (default is to skip).
        Returns the list of action notes, one per file.
        """
        actions = []
        for file_path in self.perceive():
            category, destination = self.decide(file_path)
            note = self._handle(file_path, category, destination, dry_run, ask, input_fn)
            self.log(note)
            actions.append(note)
        return actions

    def _handle(self, file_path, category, destination, dry_run, ask, input_fn):
        try:
            if not destination.exists():
                if dry_run:
                    return f"WOULD MOVE {file_path.name} -> {category}/{destination.name}"
                if self.act(file_path, destination):
                    return f"MOVED {file_path.name} -> {category}/{destination.name}"
                return f"BLOCKED {file_path.name} (destination outside folder)"

            # destination already exists — the safety branch
            if dry_run:
                return f"WOULD SKIP {file_path.name} (already exists in {category}/)"
            if not ask:
                return f"SKIPPED {file_path.name} (already exists in {category}/)"

            choice = ""
            while choice not in {"o", "r", "s"}:
                choice = input_fn(
                    f"{file_path.name} already exists in {category}/ — "
                    "[o]verwrite, [r]ename, [s]kip? "
                ).strip().lower()
            if choice == "s":
                return f"SKIPPED {file_path.name} (already exists in {category}/)"
            if choice == "o":
                os.replace(file_path, destination)
                return (
                    f"MOVED {file_path.name} -> {category}/{destination.name}"
                    " (overwrote existing)"
                )
            new_destination = self._free_name(destination)
            shutil.move(str(file_path), str(new_destination))
            return f"MOVED {file_path.name} -> {category}/{new_destination.name}"
        except FileNotFoundError:
            return f"VANISHED {file_path.name} (removed during run)"

    # -- WATCH MODE -----------------------------------------------------------
    def watch(self, interval=2.0):
        """Organize continuously: run_once() every `interval` seconds.

        Stops cleanly on Ctrl+C.
        """
        print(f"Watching {self.watch_dir} every {interval}s — Ctrl+C to stop.")
        try:
            while True:
                for note in self.run_once():
                    print(" ", note)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopped.")

    # -- UNDO -----------------------------------------------------------------
    @staticmethod
    def _parse_move(line):
        """'MOVED a.jpg -> Images/a.jpg ...' -> ('a.jpg', 'Images', 'a.jpg')"""
        if not line.startswith("MOVED "):
            return None
        body = line[len("MOVED "):].split(" (overwrote existing)")[0]
        if " -> " not in body:
            return None
        src, dest = body.split(" -> ", 1)
        if "/" not in dest:
            return None
        category, dest_name = dest.split("/", 1)
        return src.strip(), category.strip(), dest_name.strip()

    def undo(self):
        """Move files back, reversing the MOVED lines in the log.

        Only moves not already undone are reversed; nothing is ever
        overwritten — if the original spot is taken again, that file is
        skipped and logged. Returns the list of undo notes.
        """
        if not self.log_file.exists():
            return []
        pending = []
        for line in self.log_file.read_text(encoding="utf-8").splitlines():
            move = self._parse_move(line)
            if move:
                pending.append(move)
            elif line.startswith("UNDID "):
                body = line[len("UNDID "):]
                if " <- " in body:
                    src, category = body.split(" <- ", 1)
                    category = category.rstrip("/")
                    for i in range(len(pending) - 1, -1, -1):
                        if pending[i][0] == src.strip() and pending[i][1] == category:
                            pending.pop(i)
                            break
        actions = []
        for src, category, dest_name in reversed(pending):
            current = self.watch_dir / category / dest_name
            target = self.watch_dir / src
            if not current.exists():
                note = f"UNDO SKIPPED {src} (no longer in {category}/)"
            elif target.exists():
                note = f"UNDO SKIPPED {src} (name is taken in the folder)"
            else:
                shutil.move(str(current), str(target))
                note = f"UNDID {src} <- {category}/"
            self.log(note)
            actions.append(note)
        return actions

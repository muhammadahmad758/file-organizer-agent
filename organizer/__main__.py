"""Demo: build a messy folder, let the agent tidy it, show the result.

Run from the project root:
    python -m organizer
(on Boss's Windows PC:  py -m organizer)
"""

import tempfile
from pathlib import Path

from .agent import OrganizerAgent

SAMPLE_FILES = [
    "photo.jpg",
    "notes.txt",
    "song.mp3",
    "movie.mp4",
    "backup.zip",
    "script.py",
    "mystery.xyz",
]


def main():
    demo_dir = Path(tempfile.mkdtemp(prefix="organizer_demo_"))
    print(f"Messy folder: {demo_dir}")
    for name in SAMPLE_FILES:
        (demo_dir / name).write_text("demo", encoding="utf-8")
    print("Before:", ", ".join(SAMPLE_FILES))
    print()

    agent = OrganizerAgent(demo_dir)
    for note in agent.run_once():
        print(" ", note)

    print()
    print("After:")
    for path in sorted(demo_dir.rglob("*")):
        if path.is_file() and path.name != "organizer_log.txt":
            print(f"  {path.relative_to(demo_dir)}")
    print()
    print("Log file contents:")
    print((demo_dir / "organizer_log.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

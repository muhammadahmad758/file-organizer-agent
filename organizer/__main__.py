"""Demo: build a messy folder, let the agent tidy it, preview a second
file with dry-run, then undo everything.

Run from the project root:
    python -m organizer
(on Boss's Windows PC:  py -m organizer)
"""

import tempfile
from pathlib import Path

from .agent import OrganizerAgent

SAMPLE_FILES = [
    "photo.jpg",
    "invoice_march.pdf",   # name rule -> Finance (beats the .pdf rule)
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

    print("Pass 1 — organize:")
    for note in agent.run_once():
        print(" ", note)

    print()
    print("A new file arrives; dry-run previews what WOULD happen:")
    (demo_dir / "photo2.png").write_text("demo", encoding="utf-8")
    for note in agent.run_once(dry_run=True):
        print(" ", note)
    print("(photo2.png is still in the folder — dry-run moves nothing)")

    print()
    print("Undo — everything goes back:")
    for note in agent.undo():
        print(" ", note)
    loose = sorted(p.name for p in demo_dir.iterdir() if p.is_file())
    print("Loose files now:", ", ".join(loose))


if __name__ == "__main__":
    main()

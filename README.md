# File Organizer Agent

A tiny **agent** that tidies a messy folder: it perceives the files in a
folder, decides where each one belongs, moves it, and logs every decision.

```
PERCEIVE  -> which files are in the folder?
DECIDE    -> which category folder does each file belong to?
ACT       -> move it (safely — never overwrites)
LOG       -> write down every decision
```

Pure Python, standard library only. Built as a learning project to
understand the agent loop (perceive → decide → act) in its smallest form.

## Quick start

```bash
python -m organizer                       # runs the built-in demo
python -m unittest discover -s tests -v   # runs the tests
```

(On Windows, use `py` instead of `python`.)

## Use it on a real folder

```python
from organizer import OrganizerAgent

agent = OrganizerAgent("/path/to/messy/folder")
agent.run_once()
```

Categories (by extension): Images, Documents, Audio, Video, Archives,
Code — everything else goes to Others. Every action is appended to
`organizer_log.txt` in the watched folder.

## Status

Starter skeleton: the one-pass loop, rules table, safe move, and logging
work, with 6 passing tests. Watch mode, dry-run, name-based rules, undo,
config-file rules, and ask-before-overwrite are guided extension tasks —
see `EXTEND.md`.

## License

MIT — see LICENSE.

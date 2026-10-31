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
python -m unittest discover -s tests -v   # runs the tests (20)
```

(On Windows, use `py` instead of `python`.)

## Use it on a real folder

```python
from organizer import OrganizerAgent

agent = OrganizerAgent("/path/to/messy/folder")
agent.run_once()                  # organize once
agent.run_once(dry_run=True)      # preview only — moves nothing
agent.run_once(ask=True)          # ask on name clashes: overwrite/rename/skip
agent.watch(interval=2.0)         # keep organizing as files arrive (Ctrl+C stops)
agent.undo()                      # reverse everything, using the log
```

## How it decides

First match wins:

1. **Name rules** — a keyword in the filename: `invoice` → Finance,
   `screenshot` → Images, `wallpaper` → Images, `resume` → Documents
2. **Extension rules** — `.jpg` → Images, `.pdf` → Documents, `.mp3` →
   Audio, `.mp4` → Video, `.zip` → Archives, `.py` → Code, …
3. Everything else → **Others**

## Custom rules (rules.json)

Drop a `rules.json` into the watched folder to replace the built-in
rules — no code changes needed:

```json
{
  "categories": {"Games": [".exe"], "Pics": [".jpg", ".png"]},
  "name_rules": {"invoice": "Finance"}
}
```

## Safety

- **Never overwrites** an existing file unless you explicitly choose
  "overwrite" in ask mode (rename adds ` (1)`, ` (2)`, … instead).
- Never moves its own log file or its `rules.json`.
- Every action is appended to `organizer_log.txt` — and the log is what
  makes **undo** possible.
- A `rules.json` with a dangerous category name (path separators, `..`)
  is rejected, so destinations can never escape the watched folder.
- A file deleted mid-run is logged as VANISHED instead of crashing.

## Project layout

```
organizer/
  rules.py    the classification table + classify()
  agent.py    OrganizerAgent: perceive / decide / act / log, watch, undo
  __main__.py the demo
tests/
  test_organizer.py   20 tests covering every feature above
EXTEND.md     ideas for v2
LEARNING-NOTES.md   the concepts behind the code
```

## License

MIT — see LICENSE.

# Your Extension Tasks — File Organizer Agent

The skeleton works: one `run_once()` pass tidies a folder and logs every
move. These tasks turn it into *your* finished project. Do them in order;
each one is small. Predict the result before you run the tests, every time.

## Task 1 — Watch mode
Add `watch(self, interval=2.0)` to `OrganizerAgent`: loop forever calling
`run_once()`, sleep `interval` seconds between passes, and stop cleanly on
Ctrl+C (`KeyboardInterrupt`). Files dropped into the folder while it runs
should get organized within one interval.
**Done when:** you drop 3 files into a watched folder and watch them move,
then Ctrl+C stops the agent without an error.

## Task 2 — Dry-run mode
Add a `dry_run=False` parameter to `run_once()`. When True: perceive and
decide as normal, but do NOT move anything — log lines start with
`WOULD MOVE` instead of `MOVED`. This is how professionals test agents
safely before letting them act.
**Done when:** a test proves dry-run leaves every file in place but still
writes the WOULD MOVE log lines.

## Task 3 — Name-based rules
Teach `classify()` a second kind of rule that runs BEFORE extension rules:
keywords in the filename. Example: a name containing `invoice` goes to a new
`Finance` category even if it is a `.pdf`. Document the decision order at
the top of `rules.py`.
**Done when:** `classify("invoice_march.pdf") == "Finance"` and all old
tests still pass.

## Task 4 — Undo
Add `undo(self)`: read the log file, find the `MOVED` lines (newest last),
and move each file back to the watch folder root. Skip files that are no
longer there, and log the undo itself. Careful: the log also contains your
SKIPPED/WOULD MOVE lines — those must not be "undone".
**Done when:** organize a folder, run undo, and the folder looks exactly
like it did before (a test can prove this).

## Task 5 — Config file
Let the agent load its rules from a `rules.json` file next to the log if
one exists (categories -> list of extensions), falling back to the built-in
RULES. Now a user can retrain the agent's behaviour without touching code.
**Done when:** the agent organizes by a custom rules.json in a test.

## Task 6 — Ask mode (the safety upgrade)
Add `ask=False` to `run_once()`. When a destination already exists and
ask=True, prompt in the terminal: overwrite / rename / skip? Renaming adds
` (1)`, ` (2)`, ... until the name is free. Default (ask=False) keeps the
current safe behaviour: never overwrite.
**Done when:** you can watch the prompt appear for a duplicate file and
each of the three choices works.

---

Tasks 1–4 are the "complete" bar for uploading. Tasks 5–6 make it shine.
When you're done, tell Jinwoo — we upload it together, like StudySprint AI.

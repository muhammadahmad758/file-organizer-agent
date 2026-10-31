# EXTEND.md — from guided tasks to v2 ideas

Version 1.0 implements all six original extension tasks:

1. ✅ Watch mode — `watch(interval)` loops until Ctrl+C
2. ✅ Dry-run mode — `run_once(dry_run=True)` logs WOULD MOVE, moves nothing
3. ✅ Name-based rules — keywords checked before extensions (`invoice` → Finance)
4. ✅ Undo — reverses the log's MOVED lines, newest first, never overwriting
5. ✅ Config file — `rules.json` in the watched folder replaces the built-ins
6. ✅ Ask mode — on a clash: overwrite / rename / skip

## Ideas for v2 (pick one, build it, explain it)

- **watchdog support** — react to file events instantly instead of polling
- **LLM classify step** — for files no rule matches, ask a local model for
  a category suggestion (the decide step becomes a model, like real agents)
- **Date folders** — sort into `2026/10/` subfolders by file modified date
- **Duplicate finder** — same content (hash), different names: report only,
  never auto-delete
- **Stats report** — after a run, print counts per category and total size

Rule for v2 work: every new feature ships with a test, and the safety
rules in README.md do not get weaker.

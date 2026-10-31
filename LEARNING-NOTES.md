# File Organizer Agent — Learning Notes

## Why this is an agent and not just a script

A script does fixed steps top to bottom. An **agent** runs a loop:

1. **Perceive** — sense the world (here: which files are in the folder?)
2. **Decide** — pick an action using knowledge/rules (here: the category)
3. **Act** — change the world (here: move the file)
4. **Log** — record what happened, so the behaviour is auditable

That is the same loop as the coding-agent harness in the
harness-from-scratch fork (there the model decides; here the rules
decide). When people say "agentic AI", this loop is what they mean —
the intelligence in the decide step can be rules, an ML model, or an LLM.

## The three design decisions to be able to explain

- **Rules as data, not code** (`rules.py`): behaviour changes by editing a
  table. This is why Task 5 (config file) is even possible.
- **Never overwrite** (`act()` returns False instead): an agent that acts
  on your files must be safe by default. Destructive actions need consent
  — that is what Task 6's ask mode adds.
- **Log everything**: if an agent did it, there is a line proving it.
  Logs are also what makes undo (Task 4) possible.

## Vocabulary

- **Perception** — the input an agent senses from its environment.
- **Policy** — the rule/model that maps perception to action (here:
  `classify()` + RULES).
- **Dry run** — deciding and logging without acting; the standard way to
  test an agent safely (Task 2).
- **Idempotent** — running it twice gives the same result as once.
  `run_once()` on an already-tidy folder moves nothing.

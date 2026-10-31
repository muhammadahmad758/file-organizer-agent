"""Classification rules: how the agent decides where a file belongs.

Decision order (first match wins):
  1. NAME rules     — a keyword inside the filename (e.g. "invoice")
  2. EXTENSION rules — the file's extension (e.g. ".pdf")
  3. DEFAULT_CATEGORY ("Others")

The rules are DATA, not code: the agent can load a different table from
a rules.json file (see agent.py), so behaviour can change without
touching the program.
"""

from pathlib import Path

RULES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"},
    "Documents": {".pdf", ".docx", ".txt", ".md"},
    "Audio": {".mp3", ".wav"},
    "Video": {".mp4", ".mkv"},
    "Archives": {".zip", ".rar", ".7z"},
    "Code": {".py", ".java", ".cpp", ".js"},
}

# keyword (lowercase, substring match) -> category
NAME_RULES = {
    "invoice": "Finance",
    "screenshot": "Images",
    "wallpaper": "Images",
    "resume": "Documents",
}

DEFAULT_CATEGORY = "Others"


def classify(filename, rules=None, name_rules=None):
    """Return the category folder name for a file, e.g. "Images"."""
    rules = RULES if rules is None else rules
    name_rules = NAME_RULES if name_rules is None else name_rules

    lower_name = filename.lower()
    for keyword, category in name_rules.items():
        if keyword.lower() in lower_name:
            return category

    ext = Path(filename).suffix.lower()
    for category, extensions in rules.items():
        if ext in extensions:
            return category

    return DEFAULT_CATEGORY

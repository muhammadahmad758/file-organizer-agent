"""Classification rules: which file extensions belong to which category.

This is the agent's "knowledge" — the table its decide() step reads.
Keeping it in its own small module means you can change the agent's
behaviour by editing data, not code.
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

DEFAULT_CATEGORY = "Others"


def classify(filename):
    """Return the category folder name for a file, e.g. "Images".

    Decision order (v1): file extension only, case-insensitive.
    Unknown or missing extensions fall back to DEFAULT_CATEGORY.
    """
    ext = Path(filename).suffix.lower()
    for category, extensions in RULES.items():
        if ext in extensions:
            return category
    return DEFAULT_CATEGORY

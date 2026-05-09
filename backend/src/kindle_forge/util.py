from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Union


def natural_key(value: Union[str, Path]) -> list[object]:
    text = str(value)
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", text)]


def slugify(value: str, default: str = "book") -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", ascii_text).strip("-._")
    return slug or default


def human_list(items: list[Path]) -> str:
    return "\n".join(f"- {item}" for item in items)

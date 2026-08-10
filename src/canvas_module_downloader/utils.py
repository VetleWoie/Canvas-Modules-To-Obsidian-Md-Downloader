import re


def slugify(text: str, max_length: int = 80) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:max_length].rstrip("-") or "untitled"


def frontmatter(tags: list[str]) -> str:
    lines = "\n".join(f"  - {tag}" for tag in tags)
    return f"---\ntags:\n{lines}\n---\n\n"

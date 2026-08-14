import re


def slugify(text: str, max_length: int = 80) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:max_length].rstrip("-") or "untitled"


def safe_filename(text: str, max_length: int = 150) -> str:
    """Like slugify, but keeps case, spaces, and punctuation, only
    neutralizing characters that are illegal in filenames on Windows/macOS."""
    text = text.strip().replace(":", " -")
    text = re.sub(r'[\\/*?"<>|]', "-", text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    return text[:max_length].rstrip(" .-") or "untitled"


def frontmatter(tags: list[str]) -> str:
    lines = "\n".join(f"  - {tag}" for tag in tags)
    return f"---\ntags:\n{lines}\n---\n\n"

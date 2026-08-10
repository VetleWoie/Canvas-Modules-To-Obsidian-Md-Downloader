import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from requests import RequestException, Response, Session

_CONTENT_DISPOSITION_RE = re.compile(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?')
_UNSAFE_CHARS_RE = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def _filename_from_response(response: Response, fallback: str) -> str:
    match = _CONTENT_DISPOSITION_RE.search(response.headers.get("content-disposition", ""))
    if match:
        return unquote(match.group(1))
    return fallback


def _fallback_name_from_url(url: str) -> str:
    name = unquote(Path(urlparse(url).path).name)
    return name or "file"


def _sanitize(name: str) -> str:
    return _UNSAFE_CHARS_RE.sub("_", name).strip() or "file"


def _dedupe(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix, parent, n = path.stem, path.suffix, path.parent, 2
    while (candidate := parent / f"{stem}-{n}{suffix}").exists():
        n += 1
    return candidate


def download_asset(
    session: Session, url: str, dest_dir: Path, cache: dict[str, Path]
) -> Path | None:
    if url in cache:
        return cache[url]
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        response = session.get(url, stream=True)
        response.raise_for_status()
    except RequestException:
        return None
    name = _sanitize(_filename_from_response(response, _fallback_name_from_url(url)))
    dest_path = _dedupe(dest_dir / name)
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    cache[url] = dest_path
    return dest_path

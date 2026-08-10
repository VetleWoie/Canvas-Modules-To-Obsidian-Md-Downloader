import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
from requests import RequestException

from canvas_module_downloader.api import AuthError, CanvasClient
from canvas_module_downloader.assets import download_asset

_FILE_ID_RE = re.compile(r"/(?:courses/\d+/)?files/(\d+)")


class ObsidianConverter(MarkdownConverter):
    """Renders <img>/<a> tags that carry a data-embed attribute as Obsidian wikilinks."""

    def convert_img(self, el, text, parent_tags):
        target = el.get("data-embed")
        if target:
            return f"![[{target}]]"
        return super().convert_img(el, text, parent_tags)

    def convert_a(self, el, text, parent_tags):
        target = el.get("data-embed")
        if target:
            alias = text or target
            return f"[[{target}|{alias}]]"
        return super().convert_a(el, text, parent_tags)


def _download_course_file(
    client: CanvasClient, file_id: str, dest_dir: Path, download_cache: dict[str, Path]
) -> Path | None:
    cache_key = f"file:{file_id}"
    if cache_key in download_cache:
        return download_cache[cache_key]
    try:
        meta = client.get_json(f"/api/v1/files/{file_id}")
    except (AuthError, RequestException):
        return None
    download_url = meta.get("url")
    if not download_url:
        return None
    local_path = download_asset(client.session, download_url, dest_dir, download_cache)
    if local_path:
        download_cache[cache_key] = local_path
    return local_path


def _canvas_file_id(abs_url: str, base_netloc: str) -> str | None:
    if urlparse(abs_url).netloc != base_netloc:
        return None
    match = _FILE_ID_RE.search(abs_url)
    return match.group(1) if match else None


def page_html_to_markdown(
    html: str,
    base_url: str,
    client: CanvasClient,
    assets_dir: Path,
    files_dir: Path,
    download_cache: dict[str, Path],
) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    base_netloc = urlparse(base_url).netloc

    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        abs_url = urljoin(base_url + "/", src)
        file_id = _canvas_file_id(abs_url, base_netloc)
        local_path = (
            _download_course_file(client, file_id, assets_dir, download_cache)
            if file_id
            else download_asset(client.session, abs_url, assets_dir, download_cache)
        )
        if local_path:
            img["data-embed"] = local_path.name
        else:
            img["src"] = abs_url

    for a in soup.find_all("a", href=True):
        abs_url = urljoin(base_url + "/", a["href"])
        file_id = _canvas_file_id(abs_url, base_netloc)
        if file_id:
            local_path = _download_course_file(client, file_id, files_dir, download_cache)
            if local_path:
                a["data-embed"] = local_path.name
            else:
                a["href"] = abs_url
        else:
            a["href"] = abs_url

    return ObsidianConverter(heading_style="ATX").convert_soup(soup).strip() + "\n"

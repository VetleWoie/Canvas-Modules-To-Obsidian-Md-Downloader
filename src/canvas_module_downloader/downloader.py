from pathlib import Path

from canvas_module_downloader.api import CanvasClient
from canvas_module_downloader.assets import download_asset
from canvas_module_downloader.config import Config
from canvas_module_downloader.convert import page_html_to_markdown
from canvas_module_downloader.prompt import select_modules
from canvas_module_downloader.utils import frontmatter, slugify


def run(config: Config) -> None:
    client = CanvasClient(config.base_url, token=config.token, cookie=config.cookie)

    course = client.get_course(config.course_id)
    course_name = course.get("name", config.course_id)
    course_slug = slugify(course_name)
    print(f"Downloading course: {course_name}")

    modules = sorted(
        client.list_modules(config.course_id), key=lambda m: m.get("position") or 0
    )
    modules = select_modules(modules)
    download_cache: dict[str, Path] = {}

    for module in modules:
        module_slug = slugify(module["name"])
        module_dir = config.output_dir / f"{(module.get('position') or 0):02d}_{module_slug}"
        module_dir.mkdir(parents=True, exist_ok=True)
        print(f"Module: {module['name']}")

        tags = [f"course/{course_slug}", f"lesson/{module_slug}"]

        items = sorted(
            client.list_module_items(config.course_id, module["id"]),
            key=lambda i: i.get("position") or 0,
        )
        external_links: list[tuple[str, str]] = []

        for item in items:
            _handle_item(item, client, config, module_dir, download_cache, external_links, tags)

        if external_links:
            lines = "\n".join(f"- [{title}]({url})" for title, url in external_links)
            content = frontmatter(tags) + f"# External links\n\n{lines}\n"
            (module_dir / "external_links.md").write_text(content)

    print(f"Done. Output written to {config.output_dir}")


def _handle_item(
    item: dict,
    client: CanvasClient,
    config: Config,
    module_dir: Path,
    download_cache: dict[str, Path],
    external_links: list[tuple[str, str]],
    tags: list[str],
) -> None:
    item_type = item.get("type")
    position = item.get("position") or 0
    title = item.get("title", "untitled")

    if item_type == "Page":
        page = client.get_json(item["url"])
        markdown = page_html_to_markdown(
            page.get("body", ""),
            config.base_url,
            client,
            module_dir / "assets",
            module_dir / "files",
            download_cache,
        )
        filename = f"{position:02d}_{slugify(title)}.md"
        content = frontmatter(tags) + f"# {title}\n\n{markdown}"
        (module_dir / filename).write_text(content)
        print(f"  page: {title}")

    elif item_type == "File":
        file_meta = client.get_json(item["url"])
        download_url = file_meta.get("url")
        local_path = (
            download_asset(client.session, download_url, module_dir / "files", download_cache)
            if download_url
            else None
        )
        print(f"  file: {local_path.name if local_path else title + ' (failed)'}")

    elif item_type == "ExternalUrl":
        external_links.append((title, item.get("external_url", "")))

    elif item_type == "SubHeader":
        pass

    else:
        print(f"  skipped ({item_type}): {title}")

import argparse

from canvas_module_downloader.api import AuthError
from canvas_module_downloader.config import load_config
from canvas_module_downloader.downloader import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a Canvas course's modules and convert Pages to markdown."
    )
    parser.add_argument(
        "--course-id", required=True, help="Canvas course ID (visible in the course URL)"
    )
    parser.add_argument(
        "--url", help="Canvas base URL, e.g. https://school.instructure.com (or set CANVAS_URL)"
    )
    parser.add_argument("--token", help="Canvas API token (or set CANVAS_TOKEN)")
    parser.add_argument(
        "--cookie",
        help="Canvas session Cookie header, for when you don't have API token access "
        "(or set CANVAS_COOKIE)",
    )
    parser.add_argument("--output", default="output", help="Output directory (default: output)")

    args = parser.parse_args()
    try:
        run(load_config(args))
    except AuthError as e:
        raise SystemExit(f"Error: {e}") from e

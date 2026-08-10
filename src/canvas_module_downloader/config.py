import argparse
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    base_url: str
    token: str | None
    cookie: str | None
    course_id: str
    output_dir: Path


def load_config(args: argparse.Namespace) -> Config:
    load_dotenv()

    base_url = args.url or os.environ.get("CANVAS_URL")
    token = args.token or os.environ.get("CANVAS_TOKEN")
    cookie = args.cookie or os.environ.get("CANVAS_COOKIE")

    if not base_url:
        raise SystemExit("Canvas base URL not set. Pass --url or set CANVAS_URL in .env")
    if not token and not cookie:
        raise SystemExit(
            "No credentials set. Provide either an API token (--token / CANVAS_TOKEN) "
            "or a session cookie (--cookie / CANVAS_COOKIE) in .env"
        )

    return Config(
        base_url=base_url.rstrip("/"),
        token=token,
        cookie=cookie,
        course_id=args.course_id,
        output_dir=Path(args.output),
    )

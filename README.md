# canvas-module-downloader

Downloads a Canvas LMS course's Modules and converts the Pages inside them to
Markdown, with embedded images and linked files saved alongside as Obsidian
wikilink embeds (`![[image.jpg]]`, `[[handout.pdf|handout]]`).

Written by Claude (Anthropic) in collaboration with the repo owner, in an
interactive Claude Code session.

## Setup

```
uv sync
cp .env.example .env
```

Edit `.env` with your Canvas URL and credentials. You need either:

- **An API token** (`CANVAS_TOKEN`) — Canvas Account -> Settings -> New access token, or
- **A session cookie** (`CANVAS_COOKIE`), if your institution doesn't allow generating
  API tokens. Log into Canvas, open DevTools -> Network tab, click any request to your
  Canvas domain, and copy the full `Cookie` request header value. Session cookies expire
  (typically within hours of inactivity) — if a run fails partway through with an auth
  error, grab a fresh one and rerun.

## Usage

```
uv run canvas-module-downloader --course-id 12345
```

The course ID is the number in the course's URL, e.g.
`https://school.instructure.com/courses/12345`.

You'll be shown the course's modules and prompted to pick which ones to download
(comma-separated numbers, ranges like `1-3`, or blank for all).

Other flags: `--url`, `--token`, `--cookie` (override `.env`), `--output` (default:
`output/`).

## Output layout

```
output/
  04_l1-principles-and-methodology/
    01_100-overview-and-objectives.md
    ...
    assets/        <- images embedded in pages
    files/         <- downloaded attachments (PDFs, slides, etc.)
    external_links.md   <- present if the module has ExternalUrl items
```

Each page's Markdown file starts with YAML frontmatter tagging it by course and
module, e.g.:

```yaml
---
tags:
  - course/<course-slug>
  - lesson/<module-slug>
---
```

Point `--output` at a folder inside your Obsidian vault (or move the output there
afterwards) and the wikilinks/tags will resolve as normal vault notes.

Module items of type Assignment, Quiz, Discussion, and ExternalTool are not
downloaded — they're printed to the console as skipped so you know what was left out.

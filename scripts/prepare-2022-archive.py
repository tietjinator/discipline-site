#!/usr/bin/env python3
"""Copy the retained 2022 edition into a public /2022/ namespace."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

TARGET_RE = re.compile(r"(?P<prefix>\]\(|\b(?:link|href|src)\s*:\s*|\b(?:href|src)\s*=\s*[\"'])(?P<target>[^)\s\"']+)")
NUMBERED_LABEL_RE = re.compile(r"^(\*\*)(?P<number>\d{3,4})(?=[.:])")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_route(rel: str) -> str:
    if rel == "index.md":
        return "/"
    if rel.endswith("/index.md"):
        return "/" + rel[:-len("index.md")]
    return "/" + rel[:-3]


def split_target(target: str) -> tuple[str, str]:
    match = re.match(r"([^?#]*)([?#].*)?$", target)
    return match.group(1), match.group(2) or ""


def rewrite_target(target: str, routes: dict[str, str]) -> str | None:
    if not target.startswith("/") or target.startswith(("//", "/2022/")):
        return None
    path, suffix = split_target(target)
    candidates = [path]
    if path.endswith("/"):
        candidates.append(path.rstrip("/"))
    elif path.endswith(".md"):
        candidates.append(path[:-3])
    for candidate in candidates:
        if candidate in routes:
            return "/2022" + routes[candidate] + suffix
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("archive/2022-docs"))
    parser.add_argument("--destination", type=Path, default=Path("docs/2022"))
    parser.add_argument("--report", type=Path, default=Path("2022-ARCHIVE-TRANSFORM.json"))
    args = parser.parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    if not source.exists() or destination == source or source in destination.parents:
        raise SystemExit("invalid archive source/destination")

    files = sorted(p.relative_to(source).as_posix() for p in source.rglob("*.md"))
    routes = {source_route(rel): source_route(rel) for rel in files}
    destination.mkdir(parents=True, exist_ok=True)
    rewrites: list[dict[str, str]] = []
    anchor_insertions: list[dict[str, str]] = []
    anchor_skips: list[dict[str, str]] = []
    records: list[dict[str, object]] = []
    for rel in files:
        src = source / rel
        dst = destination / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        original = src.read_text(encoding="utf-8")
        line_no = 0

        def replace(match: re.Match[str]) -> str:
            nonlocal line_no
            line_no = original.count("\n", 0, match.start()) + 1
            target = match.group("target")
            rewritten = rewrite_target(target, routes)
            if rewritten is None:
                return match.group(0)
            rewrites.append({"file": rel, "line": str(line_no), "from": target, "to": rewritten})
            return match.group("prefix") + rewritten

        transformed = TARGET_RE.sub(replace, original)
        explicit_ids = set(re.findall(r"\{#([^}]+)\}|\bid=[\"']([^\"']+)[\"']", transformed))
        explicit_ids = {next(value for value in pair if value) for pair in explicit_ids}
        inserted_ids: set[str] = set()
        lines = transformed.splitlines(keepends=True)
        anchored: list[str] = []
        for index, line in enumerate(lines, 1):
            label = NUMBERED_LABEL_RE.match(line)
            if label:
                anchor_id = f"p{label.group('number')}"
                if anchor_id not in explicit_ids and anchor_id not in inserted_ids:
                    anchored.append(f'<a id="{anchor_id}"></a>\n')
                    inserted_ids.add(anchor_id)
                    anchor_insertions.append({"file": rel, "line": str(index), "anchor": anchor_id})
                else:
                    anchor_skips.append({"file": rel, "line": str(index), "anchor": anchor_id, "reason": "explicit-id" if anchor_id in explicit_ids else "duplicate-label"})
            anchored.append(line)
        transformed = "".join(anchored)
        dst.write_text(transformed, encoding="utf-8", newline="")
        records.append({
            "path": rel,
            "route": "/2022" + source_route(rel),
            "source_sha256": sha(src),
            "destination_sha256": sha(dst),
            "source_bytes": src.stat().st_size,
            "destination_bytes": dst.stat().st_size,
        })

    report = {
        "version": 1,
        "source": str(source),
        "destination": str(destination),
        "source_file_count": len(files),
        "destination_file_count": len(records),
        "source_files": records,
        "rewrites": rewrites,
        "rewrite_count": len(rewrites),
        "anchor_insertions": anchor_insertions,
        "anchor_insertion_count": len(anchor_insertions),
        "anchor_skips": anchor_skips,
        "anchor_skip_count": len(anchor_skips),
        "route_count": len(records),
    }
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "file_count": len(records), "rewrite_count": len(rewrites)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

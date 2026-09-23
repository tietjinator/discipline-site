#!/usr/bin/env python3
"""Deterministically archive 2022 Markdown and install the approved 2026 corpus."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path

EXPECTED = "5c4b9c162cbf752b3113d9450f2dbeddc85859e93b0bafaa5f07428200c71312"
LINK_RE = re.compile(r"!?(?:\[[^\]\n]*\])\((?P<target>[^)\n]+)\)")
ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9_-]+)\}")

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()

def file_hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob("*.md")) if p.is_file()}

def route(rel: str) -> str:
    if rel == "index.md": return "/"
    if rel.endswith("/index.md"): return "/" + rel[:-len("index.md")]
    return "/" + rel[:-3]

def target(root: Path, url: str) -> Path:
    clean = url.split("?", 1)[0].lstrip("/")
    if clean.endswith(".md"): clean = clean[:-3]
    if not clean: return root / "index.md"
    candidate = root / clean / "index.md"
    return candidate if candidate.exists() else root / (clean + ".md")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True); ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--docs", type=Path, required=True); ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True); a = ap.parse_args()
    manifest = sha256(a.manifest)
    if manifest != EXPECTED: raise SystemExit(f"manifest checksum mismatch: {manifest}")
    source = file_hashes(a.source)
    if len(source) != 71: raise SystemExit(f"expected 71 source files, found {len(source)}")
    archived = file_hashes(a.docs)
    if a.archive.exists(): raise SystemExit(f"archive already exists: {a.archive}")
    a.archive.mkdir(parents=True)
    for rel in sorted(archived):
        dst = a.archive / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(a.docs / rel), str(dst))
    if file_hashes(a.archive) != archived: raise SystemExit("archive preservation failure")
    for rel in sorted(source):
        dst = a.docs / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(a.source / rel, dst)
    a.docs.joinpath("index.md").write_text("""---
layout: home

hero:
  name: "The Discipline"
  text: "The Wesleyan Church"
  tagline: "2026 Edition — Governing document of The Wesleyan Church"
  actions:
    - theme: brand
      text: Start Reading
      link: /part-1/ch1-history
    - theme: alt
      text: Jump to a Paragraph
      link: /index-of-paragraphs-staging

features:
  - title: Part 1 — Basic Principles
    details: History, Mission of the Wesleyan Church, Classification of Church Law, Constitution, Special Directions
    link: /part-1/ch1-history
  - title: Part 2 — Local Church Government
    details: Local Church Organization, Membership, Conference, Pastors, Local Board of Administration, Officers and Committees
    link: /part-2/ch1-local-church-organization
  - title: Part 3 — District Church Government
    details: District Organization, Conference, Board of Administration, Officers and Committees, Administration, Ministerial Supervision
    link: /part-3/ch1-district-organization
  - title: Part 4 — General Church Government
    details: General Conference, General Board, General Officials of the Church, Administration, Communications, Global Partners, and more
    link: /part-4/ch1-general-conference
  - title: Parts 5–11 and Indexes
    details: World Organization, Ministry, Corporations, Property, Judiciary, The Ritual, Forms, Paragraph Index, Topical Index, and Appendix B
    link: /part-5/
---
""", encoding="utf-8")
    errors=[]; links=files=anchors=0
    for rel in sorted(source):
        for no,line in enumerate((a.docs/rel).read_text(encoding="utf-8").splitlines(),1):
            for m in LINK_RE.finditer(line):
                t=m.group("target")
                if not t.startswith("/") or t.startswith(("/2026/","http:","https:")): continue
                links += 1; url,_,anchor=t.partition("#"); dst=target(a.docs,url); files += 1
                if not dst.exists(): errors.append({"file":rel,"line":no,"target":t,"error":"missing target file"}); continue
                if anchor:
                    anchors += 1
                    if not ANCHOR_RE.search(dst.read_text(encoding="utf-8")): errors.append({"file":rel,"line":no,"target":t,"error":"missing target anchor"})
    out={"schema_version":1,"status":"PASS" if not errors else "FAIL","source_manifest_checksum":manifest,
         "archived_2022":{"file_count":len(archived),"files":file_hashes(a.archive),"root":"archive/2022-docs"},
         "copied_2026":{"file_count":len(source),"files":file_hashes(a.docs),"root":"docs"},
         "public_2026_routes":sorted(route(r) for r in file_hashes(a.docs)),"former_2022_routes_absent":sorted(route(r) for r in archived),
         "link_checks":{"root_absolute_internal_links":links,"target_file_checks":files,"target_anchor_checks":anchors,"errors":errors}}
    a.report.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())

#!/usr/bin/env python3
"""Rebuild docs/index-topical.md from the official PDF layout.

Uses PyMuPDF line x-coordinates to recover main-topic/subtopic hierarchy from the
printed two-column topical index. The output is deterministic Markdown, then
paragraph references are linked against anchor-map.json.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = Path('/Users/matthewtietje/Documents/Obsidian/Claude/The Discipline docusaurus.io or similar/The Discipline of The Wesleyan Church 2022.pdf')
ANCHOR_MAP = ROOT / 'anchor-map.json'
OUT = ROOT / 'docs/index-topical.md'

START_PAGE = 385  # physical PDF page: topical index begins at A
END_PAGE = 414    # physical PDF page: topical index ends at Z

ANCHORS = json.loads(ANCHOR_MAP.read_text())['anchors']
LOOKUP = {k.removeprefix('p'): v for k, v in ANCHORS.items()}

REF_RE = re.compile(r'(?<![\w#/.-])(\d{1,4}(?::\d+[a-z]?(?::?[a-z])?)?(?:[–-]\d{1,4}(?::\d+[a-z]?)?)?)')


def anchor_for(ref: str):
    first = re.split(r'[–-]', ref)[0]
    key = first.replace(':', '-').replace('.', '-')
    # Appended letter subitems like 3059:1a map to p3059-1a when present;
    # if not present, fall back to the numeric parent p3059-1.
    candidates = [key]
    m = re.match(r'(.+-\d+)[a-z]$', key)
    if m:
        candidates.append(m.group(1))
    for cand in candidates:
        path = LOOKUP.get(cand)
        if path:
            return path, 'p' + cand
    return None


def link_refs(text: str) -> str:
    # General Board Policy paragraph references are external to this site. Link
    # Discipline refs before the policy phrase, but leave policy refs plain.
    policy_markers = ['Gen. Bd.', 'Policy on Ch. Disc.', 'General Board Policy']
    cut = min([text.find(m) for m in policy_markers if m in text] or [-1])
    if cut >= 0:
        return link_refs(text[:cut]) + text[cut:]

    def repl(m: re.Match) -> str:
        ref = m.group(1)
        # Avoid years and obvious non-paragraph numbers that are not in the map.
        target = anchor_for(ref)
        if not target:
            return ref
        path, anchor = target
        display = '¶' + ref
        return f'[{display}](/' + path + f'#{anchor})'

    return REF_RE.sub(repl, text)


def normalize_text(s: str) -> str:
    s = s.replace('\u00a0', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    # Normalize straight apostrophe? Preserve curly punctuation from PDF.
    return s


def is_noise(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    if t == 'INDEX':
        return True
    if re.fullmatch(r'\d{3}', t):
        return True
    if t == '\t':
        return True
    return False


def extract_lines():
    doc = fitz.open(PDF)
    all_lines = []
    for pno in range(START_PAGE, END_PAGE + 1):
        page = doc[pno - 1]
        raw = []
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                text = normalize_text(''.join(span['text'] for span in line['spans']))
                if is_noise(text):
                    continue
                x0, y0, x1, y1 = line['bbox']
                # Skip headers/footers by y coordinate after preserving single-letter
                # index headings at top left.
                if y0 < 42 and not re.fullmatch(r'[A-Z]', text):
                    continue
                if y0 > 425:
                    continue
                raw.append({'page': pno, 'x': x0, 'y': y0, 'text': text})

        # Two-column order: left top-to-bottom, then right top-to-bottom.
        left = [l for l in raw if l['x'] < 145]
        right = [l for l in raw if l['x'] >= 145]
        for col, lines in enumerate([left, right]):
            if not lines:
                continue
            # Base indent is the most common minimum-ish x in this column.
            xs = [round(l['x'] * 2) / 2 for l in lines if not re.fullmatch(r'[A-Z]', l['text'])]
            base = min(xs) if xs else min(l['x'] for l in lines)
            for l in sorted(lines, key=lambda z: z['y']):
                l = dict(l)
                l['col'] = col
                l['base'] = base
                l['indent'] = l['x'] - base
                all_lines.append(l)
    return all_lines


class Item:
    def __init__(self, level: int, text: str):
        self.level = level  # 0 main, 1 sub
        self.text = text

    def append(self, more: str):
        if self.text.endswith('-'):
            self.text = self.text[:-1] + more
        else:
            self.text += ' ' + more
        self.text = normalize_text(self.text)


def parse_items(lines):
    out: list[str | Item] = []
    current: Item | None = None

    for l in lines:
        text = l['text']
        if re.fullmatch(r'[A-Z]', text):
            out.append(text)
            current = None
            continue

        indent = l['indent']
        # Main/sub/continuation. In this PDF, subtopics are about +9pt and
        # continuations are usually +17pt. Wrapped continuation can also be at
        # +9pt after a non-final main/sub line.
        if indent < 6:
            level = 0
        elif indent < 14:
            level = 1
        else:
            level = 2

        # Continuation rules: explicit continuation indent, or previous line has
        # not reached a natural ending and current line is indented.
        if current and (level == 2 or (level == 1 and not re.search(r'[:.;)]$|\d$', current.text))):
            current.append(text)
            continue

        if level == 2 and current:
            current.append(text)
            continue

        item = Item(level=1 if level >= 1 else 0, text=text)
        out.append(item)
        current = item

    return out


def split_topic_and_refs(text: str):
    # If the line ends with a recognizable paragraph reference cluster, render
    # as “topic — refs”. Otherwise return topic only.
    # Keep explicit See / see also lines as prose.
    if re.search(r'\b[Ss]ee\b', text) and not re.search(r'\d', text):
        return text, None
    m = re.search(r',\s*((?:\d{1,4}(?::\d+[a-z]?(?::?[a-z])?)?(?:[–-]\d{1,4}(?::\d+[a-z]?)?)?(?:[,;]\s*)?)+(?:\s+Gen\. Bd\. Policy on Ch\. Disc\.)?)$', text)
    if m:
        topic = text[:m.start()].strip()
        refs = m.group(1).strip().rstrip(',;')
        return topic, refs
    return text, None


def render(items):
    lines = [
        '---',
        'title: Topical Index',
        'pageClass: topical-index-page',
        '---',
        '',
        '# Topical Index',
        '',
        'This index covers the main topics and subtopics of *The Discipline of The Wesleyan Church 2022*. Paragraph numbers link directly to the relevant section. Entries labeled *see* or *see also* are cross-references to related topics.',
        '',
    ]

    letters = [x for x in items if isinstance(x, str) and re.fullmatch(r'[A-Z]', x)]
    # The PDF index has no W/X sections.
    lines.append('<nav class="topical-alpha" aria-label="Topical index alphabet">' + ''.join(f'<a href="#{l.lower()}">{l}</a>' for l in letters) + '</nav>')
    lines.append('')

    in_list = False
    seen_first_letter = False
    for obj in items:
        if isinstance(obj, str):
            seen_first_letter = True
            if in_list:
                lines.append('')
                in_list = False
            lines.extend([f'## {obj} {{#{obj.lower()}}}', ''])
            continue

        # The printed index has a short explanatory preface before the A section.
        # It is already represented by the intro paragraph above; do not render
        # the extracted preface lines as index entries.
        if not seen_first_letter:
            continue

        topic, refs = split_topic_and_refs(obj.text)
        rendered = link_refs(topic)
        if refs:
            rendered = f'{rendered} — {link_refs(refs)}'
        if obj.level == 0:
            if in_list:
                lines.append('')
                in_list = False
            lines.append(f'**{rendered}**')
            lines.append('')
        else:
            if not in_list:
                in_list = True
            lines.append(f'  - {rendered}')

    return '\n'.join(lines).rstrip() + '\n'


def main():
    lines = extract_lines()
    items = parse_items(lines)
    md = render(items)
    OUT.write_text(md)
    print(f'wrote {OUT}')
    print(f'items: {sum(isinstance(i, Item) for i in items)}')
    print(f'letters: {" ".join(i for i in items if isinstance(i, str))}')

if __name__ == '__main__':
    main()

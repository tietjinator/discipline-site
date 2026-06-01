#!/usr/bin/env python3
"""
Discipline Site Audit — compares all markdown content against the 2022 PDF
and scans for unlinked paragraph references.

Usage:
  /tmp/discipline-pdf-venv/bin/python scripts/audit-site.py

Produces a report at /tmp/discipline-audit-report.md
"""

import fitz, re, pathlib, json, sys
from collections import defaultdict

PDF_PATH = '/Users/matthewtietje/Documents/Obsidian/Claude/The Discipline docusaurus.io or similar/The Discipline of The Wesleyan Church 2022.pdf'
DOCS_DIR = pathlib.Path('/tmp/discipline-agents/claude-work/docs')
OUTPUT = pathlib.Path('/tmp/discipline-audit-report.md')

# ── Phase 1: Extract all paragraph text from PDF ──────────────────────────

def extract_pdf_paragraphs():
    """Extract every numbered paragraph (3+ digits) from the PDF.
    Returns dict: {paragraph_number: full_text}
    """
    doc = fitz.open(PDF_PATH)
    all_text = ''
    for pg in range(len(doc)):
        all_text += doc[pg].get_text() + '\n'
    
    paras = {}
    # Find all paragraph markers
    for m in re.finditer(r'(?:^|\n)\s*(\d{3,4})\.\s+', all_text):
        num = int(m.group(1))
        if num < 100:
            continue
        start = m.end()
        # Find next paragraph
        next_m = re.search(r'(?:^|\n)\s*\d{3,4}\.\s+', all_text[start:])
        end = start + next_m.start() if next_m else len(all_text)
        text = all_text[start:end]
        # Normalize: collapse whitespace, remove page numbers and headers
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\s+\d{1,3}$', '', text)  # trailing page number
        text = re.sub(r'\s+LOCAL\s+CHURCH\s+GOVERNMENT\s*$', '', text)
        text = re.sub(r'\s+LOCAL\s+CHURCH\s+OFFICERS.*$', '', text)
        text = re.sub(r'\s+[A-G]\.\s+\w[\w\s]+$', '', text)  # trailing section heading
        text = text.strip()
        if text:
            paras[num] = text
    return paras

# ── Phase 2: Extract all paragraph text from markdown ──────────────────────

def extract_md_paragraphs():
    """Extract paragraph text from all markdown files.
    Returns dict: {paragraph_number: {'text': ..., 'file': ..., 'line': ...}}
    """
    paras = {}
    for md_file in sorted(DOCS_DIR.rglob('*.md')):
        text = md_file.read_text(errors='ignore')
        # Skip index files
        if md_file.name == 'index.md':
            continue
        
        # Find paragraph headings like #### ¶815 {#p815}
        for m in re.finditer(r'^#{1,6}\s*¶(\d{3,4})\s*\{[^}]+\}', text, re.MULTILINE):
            num = int(m.group(1))
            start = m.end()
            # Get text until next paragraph heading or section heading
            rest = text[start:]
            next_m = re.search(r'^#{1,6}\s*¶\d{3,4}\s*\{', rest, re.MULTILINE)
            section_m = re.search(r'^##\s+[A-I]\.', rest, re.MULTILINE)
            end = start + min(
                next_m.start() if next_m else len(rest),
                section_m.start() if section_m else len(rest)
            )
            para_text = text[start:end]
            # Strip sub-paragraph headings
            para_text = re.sub(r'^#{5,6}\s*¶\d+:\w+\s*\{[^}]+\}\s*', '', para_text, flags=re.MULTILINE)
            para_text = re.sub(r'\s+', ' ', para_text).strip()
            if para_text:
                paras[num] = {
                    'text': para_text,
                    'file': str(md_file.relative_to(DOCS_DIR)),
                    'line': text[:m.start()].count('\n') + 1
                }
    return paras

# ── Phase 3: Find unlinked paragraph references in markdown ────────────────

def find_unlinked_refs():
    """Find all bare pilcrow references not inside markdown links.
    Returns list of (file, line_num, ref_text, context)
    """
    results = []
    for md_file in sorted(DOCS_DIR.rglob('*.md')):
        text = md_file.read_text(errors='ignore')
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            if line.startswith('#') or '{#' in line:
                continue
            for m in re.finditer(r'¶(\d{3,4}(?::\w+)?(?:[–-]\d{3,4}(?::\w+)?)?)', line):
                before = line[:m.start()]
                depth = before.count('[') - before.count(']')
                if depth <= 0:
                    rel = str(md_file.relative_to(DOCS_DIR))
                    results.append((rel, i, m.group(0), line.strip()[:150]))
    return results

# ── Phase 4: Compare PDF vs markdown content ───────────────────────────────

def compare_content(pdf_paras, md_paras):
    """Compare PDF paragraph text against markdown text.
    Returns list of discrepancies.
    """
    issues = []
    
    # Paras in PDF but not in markdown
    pdf_only = set(pdf_paras.keys()) - set(md_paras.keys())
    # Paras in markdown but not in PDF
    md_only = set(md_paras.keys()) - set(pdf_paras.keys())
    
    # Check content similarity for shared paragraphs
    shared = set(pdf_paras.keys()) & set(md_paras.keys())
    
    for num in sorted(shared):
        pdf_text = pdf_paras[num]
        md_text = md_paras[num]['text']
        
        # Quick check: significant length difference (>20% difference)
        len_ratio = len(md_text) / max(len(pdf_text), 1)
        if len_ratio < 0.7:
            issues.append({
                'type': 'truncated',
                'para': num,
                'file': md_paras[num]['file'],
                'detail': f'MD is {len(md_text)} chars, PDF is {len(pdf_text)} chars ({len_ratio:.1%})'
            })
        elif len_ratio > 1.3:
            issues.append({
                'type': 'extra_content',
                'para': num,
                'file': md_paras[num]['file'],
                'detail': f'MD is {len(md_text)} chars, PDF is {len(pdf_text)} chars ({len_ratio:.1%})'
            })
    
    for num in sorted(pdf_only):
        if num >= 800 and num < 10000:  # Skip page numbers etc
            issues.append({
                'type': 'missing_from_md',
                'para': num,
                'file': '-',
                'detail': f'Paragraph ¶{num} exists in PDF but not in markdown'
            })
    
    for num in sorted(md_only):
        issues.append({
            'type': 'not_in_pdf',
            'para': num,
            'file': md_paras[num]['file'],
            'detail': f'Paragraph ¶{num} in markdown does not exist in 2022 PDF'
        })
    
    return issues

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print('Extracting PDF paragraphs...')
    pdf_paras = extract_pdf_paragraphs()
    print(f'  Found {len(pdf_paras)} paragraphs in PDF')
    
    print('Extracting markdown paragraphs...')
    md_paras = extract_md_paragraphs()
    print(f'  Found {len(md_paras)} paragraphs in markdown')
    
    print('Comparing content...')
    content_issues = compare_content(pdf_paras, md_paras)
    print(f'  Found {len(content_issues)} content discrepancies')
    
    print('Scanning for unlinked references...')
    unlinked = find_unlinked_refs()
    print(f'  Found {len(unlinked)} unlinked references')
    
    # Write report
    lines = []
    lines.append('# Discipline Site Audit Report')
    lines.append('')
    lines.append(f'PDF paragraphs: {len(pdf_paras)}')
    lines.append(f'Markdown paragraphs: {len(md_paras)}')
    lines.append(f'Content discrepancies: {len(content_issues)}')
    lines.append(f'Unlinked references: {len(unlinked)}')
    lines.append('')
    
    if content_issues:
        lines.append('## Content Discrepancies')
        lines.append('')
        for issue in sorted(content_issues, key=lambda x: (x['type'], x['para'])):
            lines.append(f"- **{issue['type']}** — ¶{issue['para']} in `{issue['file']}`")
            lines.append(f"  {issue['detail']}")
        lines.append('')
    
    if unlinked:
        lines.append('## Unlinked Paragraph References')
        lines.append('')
        # Group by file
        by_file = defaultdict(list)
        for file, line_num, ref, ctx in unlinked:
            by_file[file].append((line_num, ref, ctx))
        
        for file in sorted(by_file):
            lines.append(f'### {file}')
            lines.append('')
            for line_num, ref, ctx in by_file[file]:
                lines.append(f'- Line {line_num}: `{ref}` — {ctx}')
            lines.append('')
    
    OUTPUT.write_text('\n'.join(lines) + '\n')
    print(f'\nReport written to {OUTPUT}')

if __name__ == '__main__':
    main()

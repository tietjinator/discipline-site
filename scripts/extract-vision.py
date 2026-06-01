#!/usr/bin/env python3
"""
Vision-based PDF paragraph extraction using GPT-4o.

Renders each PDF page, sends to GPT-4o vision API, extracts paragraph
numbers and full text, then compares against markdown files.

Usage:
  /tmp/vision-pdf-venv/bin/python scripts/extract-vision.py --start 93 --end 100
  /tmp/vision-pdf-venv/bin/python scripts/extract-vision.py --all
"""

import fitz, os, json, re, pathlib, sys, time, argparse, base64, tempfile
from openai import OpenAI
from io import BytesIO

PDF_PATH = '/Users/matthewtietje/Documents/Obsidian/Claude/The Discipline docusaurus.io or similar/The Discipline of The Wesleyan Church 2022.pdf'
DOCS_DIR = pathlib.Path('/tmp/discipline-agents/claude-work/docs')
KEY_FILE = os.path.expanduser('~/.hermes/.openai-key')
OUTPUT_DIR = pathlib.Path('/tmp/discipline-vision-output')
DPI = 150

# Paragraph-to-file mapping by range
PARA_RANGES = [
    (1, 99, 'part-1/ch1-history.md'),
    (100, 124, 'part-1/ch2-mission.md'),
    (125, 199, 'part-1/ch3-church-law.md'),
    (200, 399, 'part-1/ch4-constitution.md'),
    (400, 499, 'part-1/ch5-special-directions.md'),
    (500, 549, 'part-2/ch1-organization.md'),
    (550, 624, 'part-2/ch2-membership.md'),
    (625, 674, 'part-2/ch3-conference.md'),
    (675, 749, 'part-2/ch4-pastors.md'),
    (750, 799, 'part-2/ch5-local-board.md'),
    (800, 999, 'part-2/ch6-officers.md'),
    (1000, 1074, 'part-3/ch1-organization.md'),
    (1075, 1199, 'part-3/ch2-conference.md'),
    (1200, 1249, 'part-3/ch3-board.md'),
    (1250, 1299, 'part-3/ch4-officers.md'),
    (1300, 1374, 'part-3/ch5-administration.md'),
    (1375, 1409, 'part-3/ch6-ministerial.md'),
    (1410, 1449, 'part-3/ch7-missions.md'),
    (1500, 1599, 'part-4/ch1-general-conference.md'),
    (1600, 1799, 'part-4/ch2-general-board.md'),
    (1800, 1899, 'part-4/ch3-general-officials.md'),
    (1900, 1999, 'part-4/ch4-general-administration.md'),
    (2000, 2099, 'part-4/ch4-general-administration.md'),
    (2100, 2199, 'part-4/ch5-communication-admin.md'),
    (2200, 2299, 'part-4/ch6-global-partners.md'),
    (2300, 2337, 'part-4/ch7-multiplication-discipleship.md'),
    (2338, 2399, 'part-4/ch8-education-clergy.md'),
    (2400, 2499, 'part-4/ch9-boundaries.md'),
    (2600, 2699, 'part-5/ch2-conferences.md'),
    (3000, 3249, 'part-6/ch1-ministerial-orders.md'),
    (3250, 3299, 'part-6/ch1-ministerial-orders.md'),
    (3300, 3390, 'part-6/ch3-ministerial-appointments.md'),
    (3400, 3499, 'part-6/ch4-special-lay-ministries.md'),
    (4000, 4099, 'part-7/ch1-local-church-corporations.md'),
    (4100, 4199, 'part-7/ch2-district-corporations.md'),
    (4200, 4299, 'part-7/ch3-twc-corporation.md'),
    (4300, 4399, 'part-7/ch4-subsidiary-corporations.md'),
    (4500, 4630, 'part-8/ch1-general-principles.md'),
    (4650, 4790, 'part-8/ch2-local-church-property.md'),
    (4800, 4890, 'part-8/ch3-district-property.md'),
    (4900, 4999, 'part-8/ch4-general-church-property.md'),
    (5000, 5099, 'part-9/ch1-general-regulations.md'),
    (5500, 5549, 'part-10/ch1-baptism.md'),
    (5550, 5599, 'part-10/ch2-reception.md'),
    (5600, 5649, 'part-10/ch3-lords-supper.md'),
    (5650, 5699, 'part-10/ch4-marriage.md'),
    (5700, 5749, 'part-10/ch5-burial.md'),
    (5750, 5799, 'part-10/ch6-ordination.md'),
    (5800, 5849, 'part-10/ch7-commissioning.md'),
    (5850, 5899, 'part-10/ch8-commissioning-lay.md'),
    (5900, 5949, 'part-10/ch9-installation.md'),
    (5950, 5999, 'part-10/ch10-dedication.md'),
    (6000, 6249, 'part-11/ch1-church-letters.md'),
    (6250, 6499, 'part-11/ch2-service-credentials.md'),
]

def get_client():
    key = pathlib.Path(KEY_FILE).read_text().strip()
    return OpenAI(api_key=key)

def page_to_base64(page):
    """Render a PDF page to base64 PNG."""
    pix = page.get_pixmap(dpi=DPI)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        tmpname = f.name
        pix.save(tmpname)
    with open(tmpname, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    os.unlink(tmpname)
    return data

EXTRACTION_PROMPT = """Extract every numbered paragraph from this page of The Wesleyan Church Discipline. For each paragraph:

1. Paragraph number (e.g., 800, 807, 810)
2. If the paragraph has a title (like "Election." or "Duties and Powers."), include it after the number
3. The FULL text of the paragraph — every word, exactly as printed
4. All sub-paragraphs with their identifiers (1), (2), (a), (b), etc. — each with full text
5. Any section headings (A., B., C., 1., 2., etc.) and their text

Format each entry as:
PARA NNN: [title if any] Full text of the paragraph...
  (1) First sub-item text...
  (2) Second sub-item text...

Also list:
HEADING: text of any section headings on this page

If a paragraph continues from the previous page, mark it as:
PARA NNN (continued): ...remaining text...

Be precise. Every word matters. Do not summarize or paraphrase."""

def extract_page(page_num, client):
    """Extract paragraphs from one PDF page using vision."""
    doc = fitz.open(PDF_PATH)
    page = doc[page_num]  # 0-indexed
    img_b64 = page_to_base64(page)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": EXTRACTION_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}", "detail": "high"}}
            ]
        }],
        max_tokens=2000
    )
    
    text = response.choices[0].message.content
    usage = response.usage
    return text, usage

def parse_extraction(text):
    """Parse the GPT-4o output into structured data."""
    paragraphs = {}
    headings = []
    current_para = None
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # HEADING lines
        if line.startswith('HEADING:'):
            headings.append(line[8:].strip())
            continue
        
        # Paragraph lines
        m = re.match(r'PARA (\d{3,4})(?:\s*\(continued\))?:\s*(.*)', line)
        if m:
            num = m.group(1)
            text = m.group(2).strip()
            if num not in paragraphs:
                paragraphs[num] = {'text': text, 'subs': []}
            else:
                paragraphs[num]['text'] += ' ' + text
            current_para = num
            continue
        
        # Sub-paragraph lines
        m = re.match(r'\s*\((\w+)\)\s+(.*)', line)
        if m and current_para:
            sub_id = m.group(1)
            sub_text = m.group(2).strip()
            paragraphs[current_para]['subs'].append({'id': sub_id, 'text': sub_text})
            continue
        
        # Continuation lines (no prefix)
        if current_para:
            paragraphs[current_para]['text'] += ' ' + line
    
    return {'paragraphs': paragraphs, 'headings': headings}

def compare_with_markdown(para_data, md_file):
    """Compare vision-extracted paragraphs against markdown."""
    md_path = DOCS_DIR / md_file
    if not md_path.exists():
        return [f'MISSING FILE: {md_file}']
    
    md_text = md_path.read_text()
    issues = []
    
    for num, data in sorted(para_data['paragraphs'].items()):
        # Check if paragraph exists in markdown
        anchor = f'{{#p{num}}}'
        if anchor not in md_text:
            issues.append(f'¶{num}: exists in PDF but NOT in markdown')
            continue
        
        # Compare sub-paragraph counts
        if data['subs']:
            md_subs = len(re.findall(rf'##### ¶{num}:\w+', md_text))
            vision_subs = len(data['subs'])
            if md_subs != vision_subs:
                issues.append(f'¶{num}: PDF has {vision_subs} sub-paras, markdown has {md_subs}')
    
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, help='Start page (0-indexed)')
    parser.add_argument('--end', type=int, help='End page (0-indexed, exclusive)')
    parser.add_argument('--all', action='store_true', help='Process all content pages')
    parser.add_argument('--dry-run', action='store_true', help='Count pages without calling API')
    args = parser.parse_args()
    
    client = get_client() if not args.dry_run else None
    doc = fitz.open(PDF_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.all:
        # Find content pages (skip front matter before PART 1, skip index after Part 11)
        start_page = None
        end_page = None
        for pg in range(len(doc)):
            text = doc[pg].get_text()
            if 'PART 1' in text and 'Basic Principles' in text and start_page is None:
                start_page = pg
            if 'PART 1' in text and start_page is not None and pg > start_page + 50:
                # Second occurrence of PART 1 — this is the other language
                end_page = pg - 1
                break
        if end_page is None:
            end_page = len(doc) - 1
        
        pages = list(range(start_page, end_page + 1))
    else:
        pages = list(range(args.start, args.end))
    
    print(f'Pages to process: {len(pages)} ({pages[0]+1}-{pages[-1]+1})')
    
    if args.dry_run:
        return
    
    all_results = {}
    total_tokens = 0
    total_cost = 0.0
    
    for i, pg in enumerate(pages):
        page_label = pg + 1
        print(f'[{i+1}/{len(pages)}] Page {page_label}...', end=' ', flush=True)
        
        try:
            text, usage = extract_page(pg, client)
            parsed = parse_extraction(text)
            all_results[str(page_label)] = parsed
            
            tokens = usage.total_tokens
            total_tokens += tokens
            cost = (usage.prompt_tokens * 2.50 + usage.completion_tokens * 10.0) / 1_000_000
            total_cost += cost
            
            para_count = len(parsed['paragraphs'])
            print(f'{para_count} paras, {tokens} tokens, ${cost:.3f}')
            
            # Save incremental results
            with open(OUTPUT_DIR / f'page-{page_label:04d}.json', 'w') as f:
                json.dump(parsed, f, indent=2)
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f'ERROR: {e}')
            time.sleep(5)  # Back off on errors
    
    print(f'\nDone. {total_tokens} tokens, ${total_cost:.3f} estimated cost')
    
    # Compare against markdown
    print('\n--- Markdown Comparison ---')
    all_issues = []
    for page_num, data in sorted(all_results.items()):
        for num in data['paragraphs']:
            for lo, hi, fname in PARA_RANGES:
                if lo <= int(num) <= hi:
                    issues = compare_with_markdown(data, fname)
                    all_issues.extend(issues)
                    break
    
    for issue in all_issues:
        print(f'  {issue}')

if __name__ == '__main__':
    main()

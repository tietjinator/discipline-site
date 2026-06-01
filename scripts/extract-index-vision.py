#!/usr/bin/env python3
"""Extract full topical index from PDF via vision API, produce VitePress markdown."""
import fitz, base64, os, json, re, pathlib, time
from openai import OpenAI
from collections import defaultdict

PDF = '/Users/matthewtietje/Documents/Obsidian/Claude/The Discipline docusaurus.io or similar/The Discipline of The Wesleyan Church 2022.pdf'
OUTPUT = '/tmp/discipline-agents/claude-work/docs/index-topical.md'
ANCHOR_MAP = '/tmp/discipline-agents/claude-work/anchor-map.json'
KEY_FILE = os.path.expanduser('~/.hermes/.openai-key')
DPI = 150
BATCH_SIZE = 4

def get_client():
    return OpenAI(api_key=open(KEY_FILE).read().strip())

def load_anchor_map():
    with open(ANCHOR_MAP) as f:
        data = json.load(f)
    anchors = data.get('anchors', data)
    lookup = {}
    for key, value in anchors.items():
        m = re.match(r'p(\d+)(?:-(\w+))?', key)
        if m:
            num, sub = m.group(1), m.group(2)
            fpath = value.get('file', '') if isinstance(value, dict) else str(value)
            full = f'{num}:{sub}' if sub else num
            lookup[full] = fpath
    return lookup

PARA_RANGES = [
    (1, 99, 'part-1/ch1-history.md'), (100, 124, 'part-1/ch2-mission.md'),
    (125, 199, 'part-1/ch3-church-law.md'), (200, 399, 'part-1/ch4-constitution.md'),
    (400, 499, 'part-1/ch5-special-directions.md'),
    (500, 549, 'part-2/ch1-organization.md'), (550, 624, 'part-2/ch2-membership.md'),
    (625, 674, 'part-2/ch3-conference.md'), (675, 749, 'part-2/ch4-pastors.md'),
    (750, 799, 'part-2/ch5-local-board.md'), (800, 999, 'part-2/ch6-officers.md'),
    (1000, 1074, 'part-3/ch1-organization.md'), (1075, 1199, 'part-3/ch2-conference.md'),
    (1200, 1249, 'part-3/ch3-board.md'), (1250, 1299, 'part-3/ch4-officers.md'),
    (1300, 1374, 'part-3/ch5-administration.md'), (1375, 1409, 'part-3/ch6-ministerial.md'),
    (1410, 1449, 'part-3/ch7-missions.md'),
    (1500, 1599, 'part-4/ch1-general-conference.md'), (1600, 1799, 'part-4/ch2-general-board.md'),
    (1800, 1899, 'part-4/ch3-general-officials.md'), (1900, 2099, 'part-4/ch4-general-administration.md'),
    (2100, 2199, 'part-4/ch5-communication-admin.md'), (2200, 2299, 'part-4/ch6-global-partners.md'),
    (2300, 2337, 'part-4/ch7-multiplication-discipleship.md'), (2338, 2399, 'part-4/ch8-education-clergy.md'),
    (2400, 2499, 'part-4/ch9-boundaries.md'), (2600, 2699, 'part-5/ch2-conferences.md'),
    (3000, 3249, 'part-6/ch1-ministerial-orders.md'), (3250, 3390, 'part-6/ch3-ministerial-appointments.md'),
    (3400, 3499, 'part-6/ch4-special-lay-ministries.md'),
    (4000, 4099, 'part-7/ch1-local-church-corporations.md'), (4100, 4199, 'part-7/ch2-district-corporations.md'),
    (4200, 4299, 'part-7/ch3-twc-corporation.md'), (4300, 4399, 'part-7/ch4-subsidiary-corporations.md'),
    (4500, 4630, 'part-8/ch1-general-principles.md'), (4650, 4790, 'part-8/ch2-local-church-property.md'),
    (4800, 4890, 'part-8/ch3-district-property.md'), (4900, 4999, 'part-8/ch4-general-church-property.md'),
    (5000, 5099, 'part-9/ch1-general-regulations.md'),
    (5500, 5549, 'part-10/ch1-baptism.md'), (5550, 5599, 'part-10/ch2-reception.md'),
    (5600, 5649, 'part-10/ch3-lords-supper.md'), (5650, 5699, 'part-10/ch4-marriage.md'),
    (5700, 5749, 'part-10/ch5-burial.md'), (5750, 5799, 'part-10/ch6-ordination.md'),
    (5800, 5849, 'part-10/ch7-commissioning.md'), (5850, 5899, 'part-10/ch8-commissioning-lay.md'),
    (5900, 5949, 'part-10/ch9-installation.md'), (5950, 5999, 'part-10/ch10-dedication.md'),
    (6000, 6249, 'part-11/ch1-church-letters.md'), (6250, 6499, 'part-11/ch2-service-credentials.md'),
]

def resolve_ref(ref_text, anchor_map):
    """Convert a paragraph reference like '4730' or '265:2-10' to markdown link."""
    ref_text = ref_text.strip().rstrip(';').rstrip(',').strip()
    
    # Handle ranges: 265:2-10 → link to first
    m = re.match(r'(\d+):(\d+)[–-](\d+)', ref_text)
    if m:
        num, start_sub, end_sub = m.group(1), m.group(2), m.group(3)
        key = f'{num}:{start_sub}'
        if key in anchor_map:
            return f'[¶{num}:{start_sub}–{end_sub}](/{anchor_map[key]}#p{num}-{start_sub})'
    
    # Handle sub-ref: 265:2
    m = re.match(r'(\d+):(\w+)', ref_text)
    if m:
        num, sub = m.group(1), m.group(2)
        key = f'{num}:{sub}'
        if key in anchor_map:
            return f'[¶{key}](/{anchor_map[key]}#p{num}-{sub})'
    
    # Handle bare number
    m = re.match(r'(\d+)', ref_text)
    if m:
        num = m.group(1)
        pnum = int(num)
        if num in anchor_map:
            return f'[¶{num}](/{anchor_map[num]}#p{num})'
        for lo, hi, fname in PARA_RANGES:
            if lo <= pnum <= hi:
                return f'[¶{num}](/{fname}#p{num})'
    
    return f'¶{ref_text}'

def make_markdown(entries, anchor_map):
    """Convert parsed index entries to VitePress markdown."""
    letters = sorted(entries.keys())
    
    # Alphabet nav
    nav = ' '.join(f'<a href="#{l.lower()}">{l}</a>' for l in letters)
    
    lines = ['---', 'pageClass: topical-index-page', '---', '',
             '# Topical Index', '',
             f'<nav class="topical-alpha" aria-label="Topical index alphabet">{nav}</nav>', '']
    
    for letter in letters:
        lines.append(f'## {letter} {{#{letter.lower()}}}')
        lines.append('')
        
        for entry in entries[letter]:
            if entry['type'] == 'main':
                topic = entry['topic']
                refs = '; '.join(resolve_ref(r, anchor_map) for r in entry['refs'] if r.strip())
                if refs:
                    lines.append(f'**{topic}** {refs}  ')
                else:
                    lines.append(f'**{topic}**  ')
            
            elif entry['type'] == 'sub':
                text = entry['text']
                refs = '; '.join(resolve_ref(r, anchor_map) for r in entry['refs'] if r.strip())
                if refs:
                    lines.append(f'- {text} {refs}  ')
                else:
                    lines.append(f'- {text}  ')
        
        lines.append('')
    
    return '\n'.join(lines)


def main():
    client = get_client()
    doc = fitz.open(PDF)
    anchor_map = load_anchor_map()
    
    # Index pages: 385-417 (0-indexed: 384-416)
    pages = list(range(384, 417))
    print(f'Processing {len(pages)} index pages in batches of {BATCH_SIZE}')
    
    all_entries = defaultdict(list)
    total_tokens = 0
    
    for batch_start in range(0, len(pages), BATCH_SIZE):
        batch_pages = pages[batch_start:batch_start + BATCH_SIZE]
        page_labels = [p+1 for p in batch_pages]
        print(f'  Pages {page_labels[0]}-{page_labels[-1]}...', end=' ', flush=True)
        
        # Render images
        images_b64 = []
        for pg in batch_pages:
            pix = doc[pg].get_pixmap(dpi=DPI)
            import io
            buf = io.BytesIO()
            pix.save(buf, 'png')
            images_b64.append(base64.b64encode(buf.getvalue()).decode())
        
        # Build prompt
        content = [{"type": "text", "text": """Extract ALL entries from these pages of The Wesleyan Church Discipline Topical Index.

The index uses two column format. Main topics are in bold type. Subtopics are indented under main topics.

For EVERY entry, output:
MAIN: topic text | ref1; ref2; ref3
SUB: subtopic text | ref1; ref2

Include EVERY entry. Do not skip any. Be precise with paragraph numbers.

If an entry references "Gen. Bd. Policy on Ch. Disc." include that text as-is with its paragraph numbers.
If an entry says "SEE" or "SEE ALSO" with another topic, include that.
If an entry continues from a previous page, include it.
If this batch starts or ends mid-letter-section, note which letter sections appear."""}]
        for img in images_b64:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}", "detail": "high"}})
        
        try:
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content}],
                max_tokens=3000
            )
            text = resp.choices[0].message.content
            tokens = resp.usage.total_tokens
            total_tokens += tokens
            print(f'{tokens} tokens')
            
            # Parse output
            current_letter = None
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Letter section
                m = re.match(r'^([A-WYZ])$', line)  # single capital letter
                if m and len(line) == 1:
                    current_letter = m.group(1)
                    continue
                
                # Main entry
                m = re.match(r'^MAIN:\s*(.+?)\s*\|\s*(.+)$', line)
                if m and current_letter:
                    topic = m.group(1).strip()
                    refs = [r.strip() for r in m.group(2).split(';')]
                    all_entries[current_letter].append({'type': 'main', 'topic': topic, 'refs': refs})
                    continue
                
                # Try without pipe (just topic, no refs)
                m = re.match(r'^MAIN:\s*(.+)$', line)
                if m and current_letter:
                    all_entries[current_letter].append({'type': 'main', 'topic': m.group(1).strip(), 'refs': []})
                    continue
                
                # Sub entry
                m = re.match(r'^SUB:\s*(.+?)\s*\|\s*(.+)$', line)
                if m and current_letter:
                    all_entries[current_letter].append({'type': 'sub', 'text': m.group(1).strip(), 'refs': [r.strip() for r in m.group(2).split(';')]})
                    continue
                
                m = re.match(r'^SUB:\s*(.+)$', line)
                if m and current_letter:
                    all_entries[current_letter].append({'type': 'sub', 'text': m.group(1).strip(), 'refs': []})
                    continue
            
        except Exception as e:
            print(f'ERROR: {e}')
            time.sleep(5)
        
        time.sleep(1)
    
    print(f'\nTotal: {total_tokens} tokens, ~${total_tokens * 5 / 1_000_000:.3f}')
    
    # Build markdown
    md = make_markdown(all_entries, anchor_map)
    pathlib.Path(OUTPUT).write_text(md)
    print(f'Wrote {len(md)} chars to {OUTPUT}')
    print(f'Letters: {sorted(all_entries.keys())}')
    for l in sorted(all_entries.keys()):
        mains = sum(1 for e in all_entries[l] if e['type'] == 'main')
        subs = sum(1 for e in all_entries[l] if e['type'] == 'sub')
        print(f'  {l}: {mains} main, {subs} sub')

if __name__ == '__main__':
    main()

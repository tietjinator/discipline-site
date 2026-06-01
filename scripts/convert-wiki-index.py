#!/usr/bin/env python3
"""
Convert the wiki topical index HTML to VitePress markdown.

Source: https://discipline.wesleyan.org/api.php?action=parse&page=Index&prop=text&format=json
Output: docs/index-topical.md

Uses anchor-map.json to resolve /wiki/NNN links to VitePress paths.
"""

import json, re, html as html_mod, pathlib, urllib.request, sys
from collections import defaultdict

ANCHOR_MAP_PATH = '/tmp/discipline-agents/claude-work/anchor-map.json'
OUTPUT_PATH = '/tmp/discipline-agents/claude-work/docs/index-topical.md'
WIKI_API = 'https://discipline.wesleyan.org/api.php?action=parse&page=Index&prop=text&format=json'

def load_anchor_map():
    """Load anchor-map.json and build lookup: paragraph_number -> file_path"""
    with open(ANCHOR_MAP_PATH) as f:
        data = json.load(f)
    
    # The anchor map can be in different shapes. Try common patterns.
    anchors = data.get('anchors', data)
    
    # Build: {'315': 'part-1/ch4-constitution.md', '315:1': 'part-1/ch4-constitution.md', ...}
    lookup = {}
    for key, value in anchors.items():
        if isinstance(value, dict):
            fpath = value.get('file', '')
        elif isinstance(value, str):
            fpath = value
        else:
            continue
        
        # Key is like 'p315' or 'p315-1'
        m = re.match(r'p(\d+)(?:-(\w+))?', key)
        if m:
            num = m.group(1)
            sub = m.group(2)
            full = f'{num}:{sub}' if sub else num
            lookup[full] = fpath
            # Also store with different sub formats
            if sub:
                lookup[f'{num}:{sub}'] = fpath
    
    print(f'Anchor map: {len(lookup)} entries', file=sys.stderr)
    return lookup

def resolve_wiki_link(href, anchor_map):
    """Convert /wiki/NNN or /wiki/NNN:SUB to VitePress markdown link."""
    # Extract paragraph number from href
    m = re.match(r'/wiki/(\d+)(?::(\d+(?:-\d+)?))?', href)
    if not m:
        return None
    
    num = m.group(1)
    sub = m.group(2)
    
    # Try exact match first
    key = f'{num}:{sub}' if sub else num
    if key in anchor_map:
        fpath = anchor_map[key]
        return f'[¶{key}](/{fpath}#p{num}{"-"+sub if sub else ""})'
    
    # Try base number
    if num in anchor_map:
        fpath = anchor_map[num]
        if sub:
            return f'[¶{num}:{sub}](/{fpath}#p{num}-{sub})'
        return f'[¶{num}](/{fpath}#p{num})'
    
    # Fallback: try to find by prefix
    for k, v in anchor_map.items():
        if k.startswith(num):
            fpath = v
            return f'[¶{key}](/{fpath}#p{num}{"-"+sub if sub else ""})'
    
    # Hard-coded fallbacks for known paragraph ranges
    para_num = int(num)
    # Part 1
    if 1 <= para_num <= 99:       fpath = 'part-1/ch1-history.md'
    elif 100 <= para_num <= 124:   fpath = 'part-1/ch2-mission.md'
    elif 125 <= para_num <= 199:   fpath = 'part-1/ch3-church-law.md'
    elif 200 <= para_num <= 399:   fpath = 'part-1/ch4-constitution.md'
    elif 400 <= para_num <= 499:   fpath = 'part-1/ch5-special-directions.md'
    # Part 2
    elif 500 <= para_num <= 549:   fpath = 'part-2/ch1-organization.md'
    elif 550 <= para_num <= 624:   fpath = 'part-2/ch2-membership.md'
    elif 625 <= para_num <= 674:   fpath = 'part-2/ch3-conference.md'
    elif 675 <= para_num <= 749:   fpath = 'part-2/ch4-pastors.md'
    elif 750 <= para_num <= 799:   fpath = 'part-2/ch5-local-board.md'
    elif 800 <= para_num <= 999:   fpath = 'part-2/ch6-officers.md'
    # Part 3
    elif 1000 <= para_num <= 1074: fpath = 'part-3/ch1-organization.md'
    elif 1075 <= para_num <= 1199: fpath = 'part-3/ch2-conference.md'
    elif 1200 <= para_num <= 1249: fpath = 'part-3/ch3-board.md'
    elif 1250 <= para_num <= 1299: fpath = 'part-3/ch4-officers.md'
    elif 1300 <= para_num <= 1374: fpath = 'part-3/ch5-administration.md'
    elif 1375 <= para_num <= 1409: fpath = 'part-3/ch6-ministerial.md'
    elif 1410 <= para_num <= 1449: fpath = 'part-3/ch7-missions.md'
    # Part 4
    elif 1500 <= para_num <= 1599: fpath = 'part-4/ch1-general-conference.md'
    elif 1600 <= para_num <= 1699: fpath = 'part-4/ch2-general-board.md'
    elif 1800 <= para_num <= 1899: fpath = 'part-4/ch4-general-administration.md'
    elif 1900 <= para_num <= 1999: fpath = 'part-4/ch4-general-administration.md'
    elif 2000 <= para_num <= 2099: fpath = 'part-4/ch5-communication-admin.md'
    elif 2100 <= para_num <= 2199: fpath = 'part-4/ch5-communication-admin.md'
    elif 2200 <= para_num <= 2299: fpath = 'part-4/ch6-global-partners.md'
    elif 2300 <= para_num <= 2399: fpath = 'part-4/ch7-multiplication-discipleship.md'
    elif 2400 <= para_num <= 2499: fpath = 'part-4/ch9-boundaries.md'
    elif 2500 <= para_num <= 2599: fpath = 'part-4/ch9-boundaries.md'
    # Part 5
    elif 2600 <= para_num <= 2699: fpath = 'part-5/ch2-conferences.md'
    # Part 6
    elif 3000 <= para_num <= 3249: fpath = 'part-6/ch1-ministerial-orders.md'
    elif 3250 <= para_num <= 3299: fpath = 'part-6/ch1-ministerial-orders.md'
    elif 3300 <= para_num <= 3390: fpath = 'part-6/ch3-ministerial-appointments.md'
    elif 3400 <= para_num <= 3499: fpath = 'part-6/ch4-special-lay-ministries.md'
    # Part 7
    elif 4000 <= para_num <= 4099: fpath = 'part-7/ch1-local-church-corporations.md'
    elif 4100 <= para_num <= 4199: fpath = 'part-7/ch2-district-corporations.md'
    elif 4200 <= para_num <= 4299: fpath = 'part-7/ch3-twc-corporation.md'
    elif 4300 <= para_num <= 4399: fpath = 'part-7/ch4-subsidiary-corporations.md'
    # Part 8
    elif 4500 <= para_num <= 4630: fpath = 'part-8/ch1-general-principles.md'
    elif 4650 <= para_num <= 4790: fpath = 'part-8/ch2-local-church-property.md'
    elif 4800 <= para_num <= 4890: fpath = 'part-8/ch3-district-property.md'
    elif 4900 <= para_num <= 4999: fpath = 'part-8/ch4-general-church-property.md'
    # Part 9
    elif 5000 <= para_num <= 5099: fpath = 'part-9/ch1-general-regulations.md'
    # Part 10
    elif 5500 <= para_num <= 5549: fpath = 'part-10/ch1-baptism.md'
    elif 5550 <= para_num <= 5599: fpath = 'part-10/ch2-reception.md'
    elif 5600 <= para_num <= 5649: fpath = 'part-10/ch3-lords-supper.md'
    elif 5650 <= para_num <= 5699: fpath = 'part-10/ch4-marriage.md'
    elif 5700 <= para_num <= 5749: fpath = 'part-10/ch5-burial.md'
    elif 5750 <= para_num <= 5799: fpath = 'part-10/ch6-ordination.md'
    elif 5800 <= para_num <= 5849: fpath = 'part-10/ch7-commissioning.md'
    elif 5850 <= para_num <= 5899: fpath = 'part-10/ch8-commissioning-lay.md'
    elif 5900 <= para_num <= 5949: fpath = 'part-10/ch9-installation.md'
    elif 5950 <= para_num <= 5999: fpath = 'part-10/ch10-dedication.md'
    # Part 11
    elif 6000 <= para_num <= 6249: fpath = 'part-11/ch1-church-letters.md'
    elif 6250 <= para_num <= 6499: fpath = 'part-11/ch2-service-credentials.md'
    else:
        return None
    
    return f'[¶{key}](/{fpath}#p{num}{"-"+sub if sub else ""})'

def fetch_wiki_html():
    """Fetch the index page HTML from the wiki API."""
    req = urllib.request.Request(WIKI_API)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data['parse']['text']['*']

def html_to_markdown(html_text, anchor_map):
    """Convert the wiki index HTML to VitePress markdown."""
    # Extract body content between TOC and end
    # Remove TOC div
    html_text = re.sub(r'<div id="toc".*?</div>', '', html_text, flags=re.DOTALL)
    
    # Split into sections by h2 tags
    # Each section is: <h2>...letter heading...</h2><content>
    sections = re.split(r'(<h2>.*?</h2>)', html_text)
    
    lines = []
    lines.append('---')
    lines.append('pageClass: topical-index-page')
    lines.append('---')
    lines.append('')
    lines.append('# Topical Index')
    lines.append('')
    
    # Build alphabet nav
    letters_found = []
    section_data = []  # (letter, content_html)
    
    for i, chunk in enumerate(sections):
        h2_match = re.match(r'<h2>.*?<span[^>]*id="([A-Z])".*?</h2>', chunk)
        if h2_match:
            letter = h2_match.group(1)
            letters_found.append(letter)
            # Content follows in next chunk
            if i + 1 < len(sections):
                section_data.append((letter, sections[i+1]))
    
    # Generate alphabet nav
    nav_links = ' '.join(f'<a href="#{l.lower()}">{l}</a>' for l in letters_found)
    lines.append(f'<nav class="topical-alpha" aria-label="Topical index alphabet">{nav_links}</nav>')
    lines.append('')
    
    # Process each letter section
    total_links = 0
    for letter, content_html in section_data:
        lines.append(f'## {letter} {{#{letter.lower()}}}')
        lines.append('')
        
        # Parse content: each <p> or <dl> is a block
        # Use simple regex-based parsing
        blocks = re.findall(r'(<p>.*?</p>|<dl>.*?</dl>)', content_html, re.DOTALL)
        
        open_list = False
        
        for block in blocks:
            if block.startswith('<p>'):
                inner = block[3:-4]  # strip <p> and </p>
                
                # Check if this is a bold topic with subtopics (ends with colon, next block is dl)
                bold_match = re.match(r'^\s*<b>(.+?)</b>\s*$', inner)
                if bold_match:
                    topic = clean_text(bold_match.group(1))
                    if open_list:
                        lines.append('')
                        open_list = False
                    lines.append(f'**{topic}**  ')
                    continue
                
                # Bold topic with inline refs
                bold_match = re.match(r'^\s*<b>(.+?)</b>\s*(.*)', inner)
                if bold_match:
                    topic = clean_text(bold_match.group(1))
                    rest = bold_match.group(2)
                    if open_list:
                        lines.append('')
                        open_list = False
                    
                    # Convert links in the rest
                    rest_md = convert_inline_html(rest, anchor_map)
                    lines.append(f'**{topic}** {rest_md}  ')
                    total_links += rest.count('<a ')
                    continue
                
                # Plain paragraph (rare)
                md = convert_inline_html(inner, anchor_map)
                if md.strip():
                    if open_list:
                        lines.append('')
                        open_list = False
                    lines.append(md)
                    lines.append('')
            
            elif block.startswith('<dl>'):
                # Description list — these are subtopics
                dds = re.findall(r'<dd>(.*?)</dd>', block, re.DOTALL)
                for dd in dds:
                    md = convert_inline_html(dd, anchor_map)
                    if md.strip():
                        if not open_list:
                            open_list = True
                        lines.append(f'- {md}  ')
                        total_links += dd.count('<a ')
        
        if open_list:
            lines.append('')
        lines.append('')
    
    result = '\n'.join(lines)
    print(f'Total links converted: {total_links}', file=sys.stderr)
    return result

def clean_text(s):
    """Clean HTML entities and whitespace from text."""
    s = html_mod.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    # Remove trailing comma/colon for some cases
    return s

def convert_inline_html(inner, anchor_map):
    """Convert inline HTML with <a> and <b> tags to markdown."""
    # Replace <a href="/wiki/NNN">text</a> with markdown links
    def replace_link(m):
        href = m.group(1)
        text = clean_text(m.group(2))
        
        # Handle cross-index links like /wiki/Index_P
        if 'Index_' in href:
            letter = href.split('_')[-1].lower()
            return f'[{text}](#{letter})'
        
        # Handle General Board Policy references
        if 'Gen._Bd._Policy' in href or 'Church_Disc' in href:
            return f'*{text}*'
        
        # Try to resolve to VitePress path
        result = resolve_wiki_link(href, anchor_map)
        if result:
            return result
        
        # Last resort: link with pilcrow but no path
        return f'¶{text}'
    
    inner = re.sub(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', replace_link, inner)
    
    # Replace <b> tags
    inner = re.sub(r'<b>(.*?)</b>', r'**\1**', inner)
    
    # Replace <i> tags
    inner = re.sub(r'<i>(.*?)</i>', r'*\1*', inner)
    
    # Replace &nbsp;
    inner = inner.replace('&#160;', ' ')
    inner = inner.replace('&nbsp;', ' ')
    
    # Strip remaining HTML tags
    inner = re.sub(r'<br\s*/?>', ' ', inner)
    inner = re.sub(r'<[^>]+>', '', inner)
    
    # Clean entities
    inner = html_mod.unescape(inner)
    
    # Collapse whitespace
    inner = re.sub(r'\s+', ' ', inner).strip()
    
    # Remove leading comma if present
    inner = re.sub(r'^,\s*', '', inner)
    
    return inner

def main():
    print('Loading anchor map...', file=sys.stderr)
    anchor_map = load_anchor_map()
    
    print('Fetching wiki HTML...', file=sys.stderr)
    html_text = fetch_wiki_html()
    print(f'  Got {len(html_text)} chars', file=sys.stderr)
    
    print('Converting to markdown...', file=sys.stderr)
    markdown = html_to_markdown(html_text, anchor_map)
    
    print(f'Writing {OUTPUT_PATH}...', file=sys.stderr)
    pathlib.Path(OUTPUT_PATH).write_text(markdown)
    print(f'  {len(markdown)} chars, {markdown.count(chr(10))} lines', file=sys.stderr)

if __name__ == '__main__':
    main()

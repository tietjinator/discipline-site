#!/usr/bin/env python3
"""Aggregate vision-extracted paragraphs across pages and compare against markdown."""

import json, re, pathlib, sys
from collections import defaultdict

OUTPUT_DIR = pathlib.Path('/tmp/discipline-vision-output')
DOCS_DIR = pathlib.Path('/tmp/discipline-agents/claude-work/docs')

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

def get_md_file(para_num):
    for lo, hi, fname in PARA_RANGES:
        if lo <= para_num <= hi:
            return fname
    return None

def load_and_aggregate():
    """Load all per-page JSON files and merge paragraph data across pages."""
    aggregated = defaultdict(lambda: {'text': '', 'subs': {}, 'headings': []})
    
    files = sorted(OUTPUT_DIR.glob('page-*.json'))
    for fpath in files:
        data = json.loads(fpath.read_text())
        
        for num, pdata in data.get('paragraphs', {}).items():
            # Merge text
            if pdata.get('text'):
                existing = aggregated[num]['text']
                if existing and not existing.endswith(' '):
                    existing += ' '
                aggregated[num]['text'] = existing + pdata['text']
            
            # Merge sub-paragraphs
            for sub in pdata.get('subs', []):
                sid = sub['id']
                if sid not in aggregated[num]['subs']:
                    aggregated[num]['subs'][sid] = sub['text']
                else:
                    aggregated[num]['subs'][sid] += ' ' + sub['text']
    
    return aggregated

def compare_with_markdown(aggregated):
    """Compare aggregated vision data against markdown files."""
    issues = []
    
    for num in sorted(aggregated.keys(), key=int):
        data = aggregated[num]
        md_file = get_md_file(int(num))
        
        if not md_file:
            issues.append({'type': 'no_file', 'para': num, 'detail': f'No markdown file maps to paragraph {num}'})
            continue
        
        md_path = DOCS_DIR / md_file
        if not md_path.exists():
            issues.append({'type': 'missing_file', 'para': num, 'file': md_file, 'detail': f'File {md_file} does not exist'})
            continue
        
        md_text = md_path.read_text()
        
        # Check paragraph exists in markdown
        anchor = f'{{#p{num}}}'
        if anchor not in md_text:
            issues.append({'type': 'missing_para', 'para': num, 'file': md_file, 'detail': f'Paragraph ¶{num} exists in PDF but NOT in markdown'})
            continue
        
        # Compare sub-paragraph counts
        vision_subs = len(data['subs'])
        md_subs = len(re.findall(rf'##### ¶{num}:\w+', md_text))
        
        if vision_subs > 0 and md_subs != vision_subs:
            issues.append({
                'type': 'sub_count',
                'para': num,
                'file': md_file,
                'vision': vision_subs,
                'markdown': md_subs,
                'detail': f'¶{num}: PDF has {vision_subs} sub-paras ({sorted(data["subs"].keys())}), markdown has {md_subs}'
            })
    
    return issues

def main():
    print('Loading and aggregating vision data...')
    aggregated = load_and_aggregate()
    print(f'  {len(aggregated)} unique paragraphs across {len(list(OUTPUT_DIR.glob("page-*.json")))} pages')
    
    print('Comparing against markdown...')
    issues = compare_with_markdown(aggregated)
    
    # Group by type
    by_type = defaultdict(list)
    for issue in issues:
        by_type[issue['type']].append(issue)
    
    print(f'\nResults:')
    for t, items in sorted(by_type.items()):
        print(f'  {t}: {len(items)}')
    
    # Show missing paragraphs (most critical)
    if 'missing_para' in by_type:
        print('\n--- PARAGRAPHS IN PDF BUT NOT MARKDOWN ---')
        for issue in sorted(by_type['missing_para'], key=lambda x: int(x['para'])):
            print(f'  {issue["detail"]}')
    
    # Show sub-count mismatches
    if 'sub_count' in by_type:
        print('\n--- SUB-PARAGRAPH COUNT MISMATCHES ---')
        for issue in sorted(by_type['sub_count'], key=lambda x: int(x['para'])):
            print(f'  {issue["detail"]}')
            # Show which subs are in vision vs markdown
            data = aggregated[issue['para']]
            vision_keys = set(data['subs'].keys())
            md_text = (DOCS_DIR / issue['file']).read_text()
            md_keys = set()
            for m in re.finditer(rf'##### ¶{issue["para"]}:(\w+)', md_text):
                md_keys.add(m.group(1))
            if vision_keys != md_keys:
                print(f'    Vision subs: {sorted(vision_keys)}')
                print(f'    Markdown subs: {sorted(md_keys)}')
                print(f'    Only in vision: {vision_keys - md_keys}')
                print(f'    Only in markdown: {md_keys - vision_keys}')
    
    # Summary
    print(f'\nTotal issues: {len(issues)}')

if __name__ == '__main__':
    main()

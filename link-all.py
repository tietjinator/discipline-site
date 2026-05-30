#!/usr/bin/env python3
"""One-shot: link all paragraph references across all markdown files."""
import re, os, sys

docs_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/discipline-agents/claude-work/docs"

# Build anchor maps
anchor_map = {}
para_to_anchor = {}
for root, dirs, files in os.walk(docs_dir):
    for f in files:
        if f.endswith('.md'):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, docs_dir)
            content = open(full).read()
            for m in re.finditer(r'\{#(p[^}]+)\}', content):
                anchor = m.group(1)
                anchor_map[anchor] = rel
                num = anchor[1:]
                for variant in [num, num.replace('-', ':'), num.replace('-', '.')]:
                    para_to_anchor[variant] = anchor

def resolve(para_text, current_file):
    """Return markdown link for a paragraph reference, or None."""
    # Strip optional pilcrow prefix
    clean = para_text.lstrip('\u00b6')
    lookup = clean.replace(':', '-').replace('.', '-')
    anchor = para_to_anchor.get(lookup) or para_to_anchor.get(clean)
    if anchor and anchor in anchor_map:
        target = anchor_map[anchor]
        if target == current_file:
            return f'[\u00b6{clean}](#{anchor})'
        else:
            return f'[\u00b6{clean}](/{target}#{anchor})'
    # Try stripping trailing letter (e.g., 360:3b → 360:3)
    letter_match = re.match(r'^(.+)[a-z]$', lookup)
    if letter_match:
        base = letter_match.group(1)
        anchor = para_to_anchor.get(base) or para_to_anchor.get(base.replace('-', ':'))
        if anchor and anchor in anchor_map:
            target = anchor_map[anchor]
            if target == current_file:
                return f'[\u00b6{clean}](#{anchor})'
            else:
                return f'[\u00b6{clean}](/{target}#{anchor})'
    # Range: take first number
    m = re.match(r'^(\d+)[–-]', clean)
    if m:
        anchor = para_to_anchor.get(m.group(1))
        if anchor and anchor in anchor_map:
            target = anchor_map[anchor]
            if target == current_file:
                return f'[\u00b6{clean}](#{anchor})'
            else:
                return f'[\u00b6{clean}](/{target}#{anchor})'
    return None

PARA_PAT = re.compile(r'^\u00b6?\d{2,}(?::\d+[a-z]?)?(?:[–-]\d+(?::\d+[a-z]?)?)?$')

fixed = 0
for root, dirs, files in os.walk(docs_dir):
    for f in files:
        if f.endswith('.md'):
            full = os.path.join(root, f)
            current = os.path.relpath(full, docs_dir)
            content = open(full).read()
            original = content

            def fix_paren(m):
                full_match = m.group(0)
                inner = m.group(1)
                # Skip if inner contains any markdown link or starts with ¶ link
                if '](' in inner or inner.strip().startswith('[\u00b6'):
                    return full_match
                # Split on all separators
                parts = re.split(r';\s*|\s*,\s*|\s+and\s+|\s+or\s+|\s+nor\s+', inner)
                new_inner = inner
                for part in parts:
                    stripped = part.strip()
                    if PARA_PAT.match(stripped):
                        linked = resolve(stripped, current)
                        if linked:
                            new_inner = new_inner.replace(stripped, linked, 1)
                return '(' + new_inner + ')'

            content = re.sub(r'\(([^)]+)\)', fix_paren, content)

            # Bare inline refs after keywords
            def fix_bare(m):
                prefix = m.group(1)
                num = m.group(2)
                # Skip if this appears to be inside a markdown link
                # (check by looking at surrounding context — if preceded by '](' it's inside a link)
                linked = resolve(num, current)
                if linked:
                    return prefix + linked
                return m.group(0)
            # Only match bare refs NOT inside markdown links, and skip ¶ (handled by paren fix)
            content = re.sub(
                r'(?<!\]\()(in |see |cf\.? |and |or |paragraphs?\s+|nor )'
                r'(\d{2,}(?::\d+[a-z]?)?(?:[–-]\d+)?)',
                fix_bare, content
            )

            if content != original:
                open(full, 'w').write(content)
                fixed += 1

# Report
cross = same = doubles = 0
for root, dirs, files in os.walk(docs_dir):
    for f in files:
        if f.endswith('.md'):
            content = open(os.path.join(root, f)).read()
            cross += len(re.findall(r'\[\u00b6[^\]]+\]\(/[^)]+#p[^)]+\)', content))
            same += len(re.findall(r'\[\u00b6[^\]]+\]\(#p[^)]+\)', content))
            doubles += len(re.findall(r'\[\u00b6.*\[\u00b6', content))

print(f"Files: {fixed}")
print(f"Cross-file: {cross}")
print(f"Same-file: {same}")
print(f"Total: {cross + same}")
print(f"Double-link errors: {doubles}")

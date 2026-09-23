#!/usr/bin/env python3
"""Verify the rebuilt primary 2026 VitePress output."""
from __future__ import annotations
import argparse, hashlib, json, re
from urllib.parse import urljoin, urlsplit
from pathlib import Path

LINK_RE=re.compile(r"!?(?:\[[^\]\n]*\])\((?P<target>[^)\n]+)\)"); ID_RE=re.compile(r"\bid=[\"']([^\"']+)[\"']")
ALL_TARGET_RE=re.compile(r"\]\((?P<md>[^)\n]+)|(?:link|href|src)\s*:\s*[\"']?(?P<yaml>[^\s,}\"']+)|(?:href|src)\s*=\s*[\"'](?P<html>[^\"']+)")
PART_TITLES=["Part 1 — Basic Principles","Part 2 — Local Church Government","Part 3 — District Church Government","Part 4 — General Church Government","Part 5 — World Organization","Part 6 — Ministry","Part 7 — Corporations","Part 8 — Property","Part 9 — Judiciary","Part 10 — The Ritual","Part 11 — Forms"]
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def route(rel):
 if rel=='index.md': return '/'
 if rel.endswith('/index.md'): return '/'+rel[:-len('index.md')]
 return '/'+rel[:-3]
def output(route_name):
 r=route_name.split('#',1)[0].split('?',1)[0]; r=r[:-3] if r.endswith('.md') else r
 return Path('docs/.vitepress/dist')/(r.lstrip('/')+'index.html' if r.endswith('/') else r.lstrip('/')+'.html')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--transform-report',type=Path,default=Path('PRIMARY-CUTOVER-2026-TRANSFORM.json')); ap.add_argument('--archive-report',type=Path,default=Path('2022-ARCHIVE-TRANSFORM.json')); a=ap.parse_args()
 tr=json.loads(a.transform_report.read_text()); docs=Path('docs'); dist=Path('docs/.vitepress/dist'); archive=Path('archive/2022-docs'); errors=[]
 docs_files=sorted(p.relative_to(docs).as_posix() for p in docs.rglob('*.md') if p.is_file() and not p.relative_to(docs).as_posix().startswith('2022/')); expected=sorted(list(tr['copied_2026']['files'])+['index.md'])
 if docs_files!=expected: errors.append('docs Markdown set mismatch')
 if archive.resolve().is_relative_to(docs.resolve()) or not archive.exists(): errors.append('archive isolation failure')
 routes=[route(x) for x in docs_files]; outs=[output(x) for x in routes]
 if len(outs)!=len(set(outs)): errors.append('duplicate generated routes')
 for r,o in zip(routes,outs):
  if not o.exists(): errors.append(f'missing built route: {r}')
 for rel,h in tr['archived_2022']['files'].items():
  if not (archive/rel).exists() or sha(archive/rel)!=h: errors.append(f'archive hash mismatch: {rel}')
 for rel,h in tr['copied_2026']['files'].items():
  if not (docs/rel).exists() or sha(docs/rel)!=h: errors.append(f'corpus hash mismatch: {rel}')
 if {sha(docs/x) for x in docs_files if x!='index.md'} & set(tr['archived_2022']['files'].values()): errors.append('legacy byte-identical Markdown remains in docs')
 same_page=0
 for rel in docs_files:
  for no,line in enumerate((docs/rel).read_text(encoding='utf8').splitlines(),1):
   for m in LINK_RE.finditer(line):
    t=m.group('target')
    if t.startswith('#'):
     same_page+=1; o=output(route(rel)); ids=set(ID_RE.findall(o.read_text(encoding='utf8'))) if o.exists() else set()
     if t[1:] not in ids: errors.append(f'missing same-page anchor {rel}:{no}:{t}')
    elif t.startswith('/') and not t.startswith(('http:','https:','mailto:')):
     u,_,anc=t.partition('#'); o=output(u)
     if not o.exists(): errors.append(f'broken root link {rel}:{no}:{t}')
     elif anc and anc not in set(ID_RE.findall(o.read_text(encoding='utf8'))): errors.append(f'missing anchor {rel}:{no}:{t}')
     if u.startswith('/2022/') or u.startswith('/2026/'): errors.append(f'wrong edition link {rel}:{no}:{t}')
 config=Path('docs/.vitepress/config.mts').read_text(encoding='utf8'); home=(docs/'index.md').read_text(encoding='utf8'); home_html=output('/').read_text(encoding='utf8')
 local_css=docs/'public/theme-override.css'
 if not local_css.exists(): errors.append('local theme override missing')
 else:
  css=local_css.read_text(encoding='utf8')
  if '--radius-interactive: 8px' not in css or '.VPButton' not in css: errors.append('local theme override lacks live geometry rules')
  if 'theme-override.css?v=2' not in config: errors.append('local theme override is not loaded by VitePress head')
 if 'theme-override.css?v=2' not in home_html: errors.append('local theme override is absent from built homepage HTML')
 if "siteTitle: 'The Discipline'" not in config: errors.append('siteTitle is not exactly The Discipline')
 if '/2026/' in config: errors.append('unsupported /2026/ public config remains')
 if not re.search(r'^layout:\s*home\s*$',home,re.M) or 'VPHomeHero' not in home_html or 'VPHomeFeatures' not in home_html: errors.append('homepage home layout missing')
 for r in ['/part-1/ch1-history','/index-of-paragraphs-staging','/part-2/ch1-local-church-organization','/part-3/ch1-district-organization','/part-4/ch1-general-conference','/part-5/']:
  if r not in home or not output(r).exists(): errors.append(f'homepage route missing: {r}')
 for title in PART_TITLES:
  if title not in config: errors.append(f'part title missing: {title}')
 for item in [
  "{ text: 'Home', link: '/' }", "{ text: 'The Discipline', items:",
  "{ text: 'Paragraph Index', link: '/index-of-paragraphs-staging' }", "{ text: 'Topical Index', link: '/topical-index-staging' }",
  "{ text: 'Appendix B — Affiliate Churches', link: '/appendices/appendix-b-affiliate-church-agreement' }"]:
  if item not in config: errors.append(f'top navigation item missing: {item}')
 for r in ['/part-1/','/part-2/','/part-3/','/part-4/','/part-5/','/part-6/','/part-7/','/part-8/','/part-9/','/part-10/','/part-11/']:
  if r not in config: errors.append(f'top dropdown route missing: {r}')
 if 'border-radius: var(--radius-interactive)' not in local_css.read_text(encoding='utf8') if local_css.exists() else True: errors.append('8px interactive radius rule missing')
 for n in range(1,12):
  text=(docs/f'part-{n}'/'index.md').read_text(encoding='utf8')
  for title,link in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',text):
   expected_route=f'/part-{n}/'+link.lstrip('/')
   if title not in config or expected_route not in config: errors.append(f'sidebar mismatch: {title} -> {expected_route}')
 required=['p1240-1','p1240-1-a','p6410','p6420']; html='\n'.join(o.read_text(encoding='utf8') for o in outs if o.exists())
 for x in required:
  if f'id="{x}"' not in html and f"id='{x}'" not in html: errors.append(f'missing required anchor: {x}')
 old_unique=[x for x in tr['former_2022_routes_absent'] if x not in set(routes)]
 for r in old_unique:
  if output(r).exists(): errors.append(f'former unique 2022 route built: {r}')
 archive_report = json.loads(a.archive_report.read_text()) if a.archive_report.exists() else None
 archive_links = archive_anchor_checks = 0
 if not archive_report:
  errors.append('2022 archive transform report missing')
 else:
  archive_files=archive_report['source_files']; public_root=Path('docs/2022')
  if len(archive_files) != 73 or archive_report.get('source_file_count') != 73 or archive_report.get('destination_file_count') != 73:
   errors.append('2022 archive file count is not exactly 73')
  if archive_report.get('rewrite_count', 0) <= 0: errors.append('2022 archive has no recorded link rewrites')
  for record in archive_files:
   rel=record['path']; src=archive/rel; dst=public_root/rel
   if not src.exists() or sha(src) != record['source_sha256']: errors.append(f'2022 archive source hash mismatch: {rel}')
   if not dst.exists() or sha(dst) != record['destination_sha256']: errors.append(f'2022 public hash mismatch: {rel}')
   page_route='/2022'+route(rel)
   page_output=output(page_route)
   if not page_output.exists(): errors.append(f'missing built 2022 route: {page_route}')
   if not dst.exists(): continue
   text=dst.read_text(encoding='utf8')
   for match in ALL_TARGET_RE.finditer(text):
    target=next((x for x in match.group('md','yaml','html') if x is not None), '')
    if not target or target.startswith(('#','http:','https:','mailto:','data:','//')): continue
    resolved=urlsplit(urljoin('https://local'+page_route, target))
    target_path=resolved.path
    if target_path.endswith('.md'): target_path=target_path[:-3]
    if target.startswith('/') and not target_path.startswith('/2022/'):
     errors.append(f'2022 link escapes archive: {rel}:{target}')
     continue
    if not target_path.startswith('/2022/'):
     errors.append(f'2022 relative link escapes archive: {rel}:{target}')
     continue
    target_output=output(target_path)
    if not target_output.exists(): errors.append(f'broken 2022 link {rel}:{target}')
    else:
     archive_links += 1
     anchor=resolved.fragment
     if anchor:
      archive_anchor_checks += 1
      if anchor not in set(ID_RE.findall(target_output.read_text(encoding='utf8'))): errors.append(f'missing 2022 anchor {rel}:{target}')
  for rewrite in archive_report['rewrites']:
   if not rewrite['to'].startswith('/2022/'): errors.append(f'non-2022 rewrite recorded: {rewrite}')
  duplicate_ids=[]
  for page in dist.rglob('*.html'):
   ids=ID_RE.findall(page.read_text(encoding='utf8'))
   counts={item: ids.count(item) for item in set(ids)}
   for item,count in counts.items():
    if count > 1: duplicate_ids.append({'page': page.relative_to(dist).as_posix(), 'id': item, 'count': count})
  if duplicate_ids: errors.append(f'duplicate HTML ids: {duplicate_ids[:12]}')
  p5605_output=output('/2022/part-10/ch3-lords-supper')
  p1522_output=output('/2022/part-4/ch1-general-conference')
  if p5605_output.exists() and ID_RE.findall(p5605_output.read_text(encoding='utf8')).count('p5605') != 1: errors.append('regression: p5605 is not unique')
  if p1522_output.exists() and ID_RE.findall(p1522_output.read_text(encoding='utf8')).count('p1522') != 1: errors.append('regression: p1522 is not unique')
  repeated_source=(archive/'part-10/ch3-lords-supper.md').read_text(encoding='utf8')
  collision_source=(archive/'part-4/ch1-general-conference.md').read_text(encoding='utf8')
  if repeated_source.count('**5605.**') != 2: errors.append('regression fixture missing repeated 5605 labels')
  if '{#p1522}' not in collision_source: errors.append('regression fixture missing explicit p1522 anchor')
  if not any(item.get('anchor') == 'p5605' and item.get('reason') == 'duplicate-label' for item in archive_report.get('anchor_skips', [])): errors.append('transform did not record repeated p5605 suppression')
  if not any(item.get('anchor') == 'p1522' and item.get('reason') == 'explicit-id' for item in archive_report.get('anchor_skips', [])): errors.append('transform did not record explicit p1522 collision suppression')
  for required_route in ['/2022/','/2022/index-of-paragraphs','/2022/index-topical','/2022/part-1/','/2022/part-2/ch1-organization','/2022/appendices']:
   if not output(required_route).exists(): errors.append(f'missing required 2022 route: {required_route}')
  archive_home=output('/2022/').read_text(encoding='utf8') if output('/2022/').exists() else ''
  if '2022 Edition' not in archive_home: errors.append('2022 homepage identity missing')
  if "{ text: '2022 Archive', link: '/2022/' }" not in config or "'/2022/': archiveSidebar" not in config: errors.append('2022 archive navigation namespace missing')
  sitemap=dist/'sitemap.xml'
  if not sitemap.exists() or '/2022/' not in sitemap.read_text(encoding='utf8') or '/part-1/' not in sitemap.read_text(encoding='utf8'): errors.append('sitemap does not contain both edition namespaces')
 result={'status':'PASS' if not errors else 'FAIL','root_2026_route_count':len(routes),'archive_2022_file_count':len(tr['archived_2022']['files']),'public_2022_route_count':len(archive_report['source_files']) if archive_report else 0,'same_page_anchor_checks':same_page,'archive_link_checks':archive_links,'archive_anchor_checks':archive_anchor_checks,'archive_rewrite_count':archive_report.get('rewrite_count',0) if archive_report else 0,'duplicate_id_count':len(duplicate_ids) if archive_report else 0,'required_anchors':required,'errors':errors}
 print(json.dumps(result,indent=2,sort_keys=True)); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())

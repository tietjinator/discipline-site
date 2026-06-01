# Discipline Site — Next Steps Plan

**Date:** June 1, 2026  
**Context:** Audit report at /tmp/discipline-audit-report.md found 293 content discrepancy flags and 164 unlinked references. Verification (at /tmp/discipline-audit-verification.md) found ~95% of content flags are false positives (markdown link inflation) and ~25% of unlinked refs are real.

## Goal

Make the discipline site content match the 2022 PDF with 100% accuracy. No 2016-era carryovers, no broken paragraph numbers, all cross-references linked.

## Phase 1: Unlinked References Sweep (~40 real refs)

**Priority:** High. These are visible to users — bare pilcrow text that should be clickable links.

**Approach:** Write a batch script that scans each file for bare `¶NNN` references, resolves them against the anchor-map.json + known paragraph ranges, and adds markdown links. Apply the two-layer masking approach proven on ch6.

**Files with the most real unlinked refs:**
- `part-10/ch6-ordination.md` (~19 refs) — ritual cross-references
- `part-10/ch7-commissioning.md` — ritual cross-references
- `part-10/ch8-commissioning-lay.md` — ritual cross-references
- Other Part 10 ritual chapters
- `part-1/ch4-constitution.md` — some real refs buried among footnote div refs

**Validation:** After each file, `grep` for remaining bare pilcrows outside known-external (GB Policy, ¶6765) and TOC/index contexts.

**Script:** `scripts/link-bare-refs.py`

## Phase 2: Paragraph Renumbering Audit

**Priority:** High. The most insidious bug — content matches but paragraph number is wrong (e.g., ¶1542 → ¶1541 in 2022).

**Approach:** Write a script that:
1. Extracts all paragraph numbers from the PDF in sequence
2. Extracts all paragraph numbers from each markdown file
3. Compares: if PDF has ¶1541 and markdown has ¶1542 with matching text, flag as renumbering
4. Produces a fix list: `sed 's/¶1542/¶1541/g' part-4/ch1-general-conference.md`

**Known renumberings found so far:**
- ¶1542 → ¶1541 (General Conference Delegates)

**Script:** `scripts/find-renumbering.py`

## Phase 3: Content Carryover Detection

**Priority:** Medium. Finding sentences/paragraphs from 2016 that survived in the markdown but aren't in the 2022 PDF.

**Approach:** Improve the audit script to:
1. Strip markdown link syntax from MD text before comparing length
2. Flag only differences >50% (not >30%) as real
3. Human-review any file with flags, comparing PDF page-by-page

**Known carryovers fixed so far:**
- ch6: ¶800 list items (3)-(4), ¶810 extra sentences, ¶833, ¶835, ¶837, ¶856:8-9
- ch1-General Conference: ¶1542 renumbering, ¶1539 stray period

**Script:** `scripts/audit-site.py` (already exists, needs improvement)

## Phase 4: Anchor Completeness

**Priority:** Low. Every `###` heading in every chapter should have an explicit `{#anchor}` for clean URLs.

**Approach:** Scan all markdown files for `###` headings without `{#...}` anchors. Auto-generate clean slugs.

**Script:** `scripts/add-h3-anchors.py`

## Phase 5: Cross-File Link Validation

**Priority:** Low. Some references may link to wrong files after Part 8/9 swap or renumbering.

**Approach:** Extract all `[¶NNN](path#pNNN)` links from every file. Verify each anchor actually exists in the target file. Flag broken links.

**Script:** `scripts/validate-cross-refs.py`

## Execution Order

1. Phase 1 (unlinked refs) — highest user-visible impact
2. Phase 2 (renumbering) — silently wrong, data corruption
3. Phase 3 (carryover) — remaining 2016 text
4. Phase 4 (anchors) — cosmetic but clean
5. Phase 5 (cross-file links) — final integrity check

## Risks

- **Batch linking could create double-links** — use the proven two-layer mask approach from ch6
- **Renumbering script false positives** — paragraph text must be content-matched, not just number-matched
- **PDF extraction truncation** — paragraphs spanning page breaks need full-text extraction, not single-page
- **Part 10/11 paragraphs** — these chapter files may not have all anchor IDs yet; linking may create dead links until anchors exist

## Validation After Each Phase

```bash
npm run docs:build        # must pass
git diff --stat           # review scope of changes
# Spot-check 2-3 pages in browser
```

# Build Plan: The Discipline — VitePress Site

## Handoff Notes for Coder

**Goal:** Convert *The Discipline of The Wesleyan Church 2022* into a navigable, cross-referenced web publication using VitePress. The finished site should feel authoritative, readable, and fully aligned with The Wesleyan Church's brand.

**Audience:** Public-facing. The site will be indexed by search engines.

**Staging URL:** `https://twcdiscipline.kal-el.net` — self-hosted on owner's server.

**End goal:** Replace the existing official wiki at `discipline.wesleyan.org` (currently MediaWiki, poor UX). Build with that eventual migration in mind — clean URLs, good SEO, no orphaned links.

**Scope split — two workstreams:**
- **Workstream A (coder):** VitePress project setup, theming, config, deployment pipeline. Produces the site shell ready to receive content.
- **Workstream B (content):** PDF extraction and markdown conversion of The Discipline. This is a separate AI-assisted effort and can proceed in parallel. Coder should build with placeholder content first.

**Key files in this project folder:**
- `The Discipline of The Wesleyan Church 2022.pdf` — the source document
- `Public-TWC-Brand-Guide-Revised-2023.pdf` — official brand reference
- `Raleway TWC 2.0/woff2/` — converted web fonts ready to use (8 weights)

**An official MediaWiki already exists** at [discipline.wesleyan.org](https://discipline.wesleyan.org). This project is a full replacement, not a companion site.

---

---

## Phase 1 — Project Setup

### 1.1 Prerequisites
- Node.js 18 or higher (`node -v` to check; install from nodejs.org if needed)
- A code editor (VS Code recommended)
- Git (for version control and deployment)

### 1.2 Initialize VitePress

```bash
mkdir discipline-site
cd discipline-site
npm init -y
npm install -D vitepress
npx vitepress init
```

When prompted:
- Site title: `The Discipline — The Wesleyan Church 2022`
- Site description: `The governing document of The Wesleyan Church`
- Theme: `Default Theme`
- TypeScript: No (keep it simple)

### 1.3 Folder structure to build toward

```
discipline-site/
├── docs/
│   ├── .vitepress/
│   │   ├── config.mts         ← site config, nav, sidebar
│   │   └── theme/
│   │       ├── index.ts       ← theme entry
│   │       └── custom.css     ← all brand/style overrides
│   ├── index.md               ← homepage
│   ├── part-1/
│   │   ├── index.md
│   │   ├── ch1-history.md
│   │   ├── ch2-mission.md
│   │   └── ...
│   ├── part-2/
│   ├── part-3/
│   ├── part-4/
│   ├── part-5/
│   ├── part-6/
│   ├── appendices/
│   └── index-of-paragraphs.md
├── package.json
└── .gitignore
```

---

## Phase 2 — Content Extraction (PDF → Markdown)

This is the most labor-intensive phase. Use AI tools to automate as much as possible.

### 2.1 Extract raw text from the PDF using MarkItDown

[MarkItDown](https://github.com/microsoft/markitdown) (Microsoft, 123k stars) converts PDFs and Office documents directly to Markdown, preserving structure better than raw text extraction. Use it instead of a custom script.

```bash
pip install 'markitdown[pdf]'
markitdown "The Discipline of The Wesleyan Church 2022.pdf" -o raw-extract.md
```

That's it — one command produces a markdown file with headings, lists, and structure already partially intact. The output will still need AI-assisted cleanup (Phase 2.2), but you're starting from structured markdown rather than raw text, which significantly reduces the cleanup work.

**Optional: Azure Document Intelligence (higher fidelity)**

If MarkItDown's standard PDF extraction misses formatting detail, Microsoft's Document Intelligence service produces better results on complex layouts. Requires an Azure account (free tier available):

```bash
markitdown "The Discipline of The Wesleyan Church 2022.pdf" -o raw-extract.md \
  -d -e "<your-document-intelligence-endpoint>"
```

### 2.2 AI-assisted conversion (recommended approach)

The raw text will have formatting artifacts from the PDF. Use an AI tool (Claude, GPT-4, etc.) with the following instructions for each section:

**Prompt template for each chapter:**

```
Convert the following raw text from The Wesleyan Church Discipline into clean markdown.

Rules:
- Each numbered paragraph (e.g., "125.") becomes a heading: ## ¶125 {#p125}
- Each subparagraph (e.g., "1:") becomes: ### ¶725:1 {#p725-1}
- Sub-subparagraphs lettered (a, b, c) become: #### ¶1233:9b {#p1233-9b}
- Cross-references in parentheses like (725:1) or (260–268) become markdown links:
  [¶725:1](#p725-1) or [¶260–268](#p260)
- Scripture references in italics stay as plain text
- Preserve section headings (Part, Chapter, Article) as # and ## headings
- Do not add commentary or change any wording

[PASTE RAW TEXT HERE]
```

### 2.3 File organization by section

Map The Discipline's structure to files:

| Section | Paragraphs | File |
|---|---|---|
| Part 1, Ch. 1 — History | 1–99 | `part-1/ch1-history.md` |
| Part 1, Ch. 2 — Mission | 100–124 | `part-1/ch2-mission.md` |
| Part 1, Ch. 3 — Classification of Church Law | 125–199 | `part-1/ch3-church-law.md` |
| Part 1, Ch. 4 — Constitution | 200–399 | `part-1/ch4-constitution.md` |
| Part 1, Ch. 5 — Special Directions | 400–499 | `part-1/ch5-special-directions.md` |
| Part 2, Ch. 1 — Local Church Organization | 500–549 | `part-2/ch1-organization.md` |
| Part 2, Ch. 2 — Membership | 550–624 | `part-2/ch2-membership.md` |
| Part 2, Ch. 3 — Local Church Conference | 625–674 | `part-2/ch3-conference.md` |
| Part 2, Ch. 4 — Pastors | 675–749 | `part-2/ch4-pastors.md` |
| Part 2, Ch. 5 — Local Board of Administration | 750–799 | `part-2/ch5-local-board.md` |
| Part 2, Ch. 6 — Officers and Committees | 800–999 | `part-2/ch6-officers.md` |
| Part 3 — District Government | 1000–1499 | `part-3/` (split by chapter) |
| Part 4 — General Church Government | 1500–2499 | `part-4/` (split by chapter) |
| Part 5 — World Organization | 2500–2999 | `part-5/` |
| Ministry | 3000–3499 | `ministry/` |
| Corporations | 4000–4499 | `corporations/` |
| Property | 4500–4999 | `property/` |
| Judiciary | 5000–5004 | `judiciary/` |
| Ritual | 5500–5999 | `ritual/` |
| Forms | 6000–6499 | `forms/` |
| Appendices | 6500–7999 | `appendices/` |

### 2.4 Cross-reference anchor convention

Every paragraph needs a stable HTML anchor. Use this convention consistently:

| Reference type | Markdown heading syntax | Rendered anchor |
|---|---|---|
| Paragraph 725 | `## ¶725 {#p725}` | `#p725` |
| Subparagraph 725:1 | `### ¶725:1 {#p725-1}` | `#p725-1` |
| Sub-subparagraph 1233:9b | `#### ¶1233:9b {#p1233-9b}` | `#p1233-9b` |

Cross-reference links use relative paths:

```markdown
See [¶725](/part-2/ch4-pastors#p725) for requirements.
See [¶260–268](/part-1/ch4-constitution#p260) for General Rules.
```

For cross-references within the same file, just use the anchor:

```markdown
as provided in [¶725:1](#p725-1)
```

---

## Phase 3 — VitePress Configuration

### 3.1 Main config file

Create `docs/.vitepress/config.mts`:

```typescript
import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "The Discipline",
  description: "The governing document of The Wesleyan Church, 2022 Edition",

  // Update to https://discipline.wesleyan.org when migrating
  base: '/',

  sitemap: {
    hostname: 'https://twcdiscipline.kal-el.net'
  },

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#0B496F' }],
    ['meta', { name: 'robots', content: 'index, follow' }],
    ['link', { rel: 'canonical', href: 'https://twcdiscipline.kal-el.net' }],
    // Load Open Sans from Google Fonts (remove if self-hosting)
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,600;1,400&display=swap' }],
  ],

  themeConfig: {
    logo: '/wesleyan-logo.svg',
    siteTitle: 'The Discipline 2022',

    nav: [
      { text: 'Home', link: '/' },
      { text: 'Part 1 — Basic Principles', link: '/part-1/' },
      { text: 'Part 2 — Local Church', link: '/part-2/' },
      { text: 'Part 3 — District', link: '/part-3/' },
      { text: 'Part 4 — General Church', link: '/part-4/' },
      { text: 'Paragraph Index', link: '/index-of-paragraphs' },
    ],

    sidebar: {
      '/part-1/': [{
        text: 'Part 1 — Basic Principles',
        items: [
          { text: 'Ch. 1 — History (¶1–99)', link: '/part-1/ch1-history' },
          { text: 'Ch. 2 — Mission (¶100–124)', link: '/part-1/ch2-mission' },
          { text: 'Ch. 3 — Church Law (¶125–199)', link: '/part-1/ch3-church-law' },
          { text: 'Ch. 4 — Constitution (¶200–399)', link: '/part-1/ch4-constitution' },
          { text: 'Ch. 5 — Special Directions (¶400–499)', link: '/part-1/ch5-special-directions' },
        ]
      }],
      '/part-2/': [{
        text: 'Part 2 — Local Church Government',
        items: [
          { text: 'Ch. 1 — Organization (¶500–549)', link: '/part-2/ch1-organization' },
          { text: 'Ch. 2 — Membership (¶550–624)', link: '/part-2/ch2-membership' },
          { text: 'Ch. 3 — Conference (¶625–674)', link: '/part-2/ch3-conference' },
          { text: 'Ch. 4 — Pastors (¶675–749)', link: '/part-2/ch4-pastors' },
          { text: 'Ch. 5 — Local Board (¶750–799)', link: '/part-2/ch5-local-board' },
          { text: 'Ch. 6 — Officers & Committees (¶800–999)', link: '/part-2/ch6-officers' },
        ]
      }],
      '/part-3/': [{
        text: 'Part 3 — District Government',
        items: [
          { text: 'Ch. 1 — Organization (¶1000–1074)', link: '/part-3/ch1-organization' },
          { text: 'Ch. 2 — District Conference (¶1075–1199)', link: '/part-3/ch2-conference' },
          { text: 'Ch. 3 — Board of Administration (¶1200–1249)', link: '/part-3/ch3-board' },
          { text: 'Ch. 4 — Officers & Committees (¶1250–1299)', link: '/part-3/ch4-officers' },
          { text: 'Ch. 5 — Administration (¶1300–1374)', link: '/part-3/ch5-administration' },
          { text: 'Ch. 6 — Ministerial Supervision (¶1375–1409)', link: '/part-3/ch6-ministerial' },
          { text: 'Ch. 7 — Missions & Evangelism (¶1410–1439)', link: '/part-3/ch7-missions' },
          { text: 'Ch. 8 — Christian Education (¶1440–1499)', link: '/part-3/ch8-education' },
        ]
      }],
      '/part-4/': [{
        text: 'Part 4 — General Church Government',
        items: [
          { text: 'General Church Government (¶1500–2499)', link: '/part-4/' },
        ]
      }],
      '/part-5/': [{
        text: 'Part 5 — World Organization',
        items: [
          { text: 'World Organization (¶2500–2999)', link: '/part-5/' },
        ]
      }],
      '/ministry/': [{
        text: 'Ministry',
        items: [
          { text: 'Ministry (¶3000–3499)', link: '/ministry/' },
        ]
      }],
      '/corporations/': [{
        text: 'Corporations',
        items: [
          { text: 'Corporations (¶4000–4499)', link: '/corporations/' },
        ]
      }],
      '/property/': [{
        text: 'Property',
        items: [
          { text: 'Property (¶4500–4999)', link: '/property/' },
        ]
      }],
      '/judiciary/': [{
        text: 'Judiciary',
        items: [
          { text: 'Judiciary (¶5000–5004)', link: '/judiciary/' },
        ]
      }],
      '/ritual/': [{
        text: 'Ritual',
        items: [
          { text: 'Ritual (¶5500–5999)', link: '/ritual/' },
        ]
      }],
      '/forms/': [{
        text: 'Forms',
        items: [
          { text: 'Forms (¶6000–6499)', link: '/forms/' },
        ]
      }],
      '/appendices/': [{
        text: 'Appendices',
        items: [
          { text: 'Appendices (¶6500–7999)', link: '/appendices/' },
        ]
      }],
    },

    search: {
      provider: 'local'
    },

    outline: {
      level: [2, 3],
      label: 'Paragraphs on this page'
    },

    editLink: {
      pattern: 'https://github.com/YOUR-USERNAME/discipline-site/edit/main/docs/:path',
      text: 'Suggest a correction'
    },

    footer: {
      message: 'The Discipline of The Wesleyan Church, 2022 Edition',
      copyright: 'Copyright © 2022 Wesleyan Publishing House'
    }
  }
})
```

### 3.2 Homepage (docs/index.md)

```markdown
---
layout: home

hero:
  name: "The Discipline"
  text: "The Wesleyan Church"
  tagline: "2022 Edition — Governing document of The Wesleyan Church"
  image:
    src: /discipline-cover.jpg
    alt: The Discipline 2022
  actions:
    - theme: brand
      text: Start Reading
      link: /part-1/ch1-history
    - theme: alt
      text: Jump to a Paragraph
      link: /index-of-paragraphs

features:
  - title: Basic Principles (¶1–499)
    details: History, Mission, Classification of Church Law, Constitution, Special Directions
    link: /part-1/
  - title: Local Church Government (¶500–999)
    details: Organization, Membership, Conference, Pastors, Board of Administration, Officers
    link: /part-2/
  - title: District Government (¶1000–1499)
    details: Organization, Conference, Board, Officers, Administration, Ministerial Supervision
    link: /part-3/
  - title: General Church Government (¶1500–2499)
    details: General Conference, General Board, Officers, Corporations
    link: /part-4/
---
```

---

## Phase 4 — Theming

### 4.1 Wesleyan Church brand reference

From the official TWC Brand Guide (2023). Use these exact values — do not approximate.

**Primary colors (logo-safe):**
| Name | Hex | RGB | Usage |
|---|---|---|---|
| Dark Blue | `#0B496F` | 14, 73, 111 | Primary brand color — headers, nav, CTAs |
| Light Blue | `#39AAE1` | 57, 171, 225 | Interactive elements, links, accents |

**Secondary colors:**
| Name | Hex | Usage |
|---|---|---|
| Blue-Black | `#03344D` | Deep backgrounds, dark mode |
| Aqua | `#40BCBC` | Accent highlights |
| Green | `#83B841` | Success states (use sparingly) |
| Yellow | `#FDBF51` | Callout highlights |
| Red | `#E96351` | Warnings, important notices |

**Neutral palette:**
| Name | Hex | Usage |
|---|---|---|
| Dark Gray | `#333132` | Body text |
| Light Blue | `#BDE6FA` | Backgrounds, tinted sections |
| Mid Gray | `#B8B9B9` | Borders, dividers |
| Light Gray | `#E7E7E7` | Subtle backgrounds |

**Fonts (official TWC brand fonts):**
- **Display/Headlines:** Raleway TWC 2.0 — download free from wesleyan.org/brand. Elegant sans-serif, 9 weights. This is the primary brand font.
- **Body:** Open Sans — clean sans-serif, free, available on Google Fonts. Primary body copy font.
- **Decorative:** Market Pro — hand-drawn script, use sparingly for callout words or phrases only. Available at myfonts.com.

**Logo:** Download from wesleyan.org/brand. Two approved versions: stacked (for sidebars/corners) and horizontal (for headers with white space). The dove icon alone can also be used.

**A note on typography for The Discipline:** The official TWC brand uses sans-serif throughout. For a long-form legal/governing document, Open Sans at comfortable size and line height reads well. If you want to introduce a serif for body text to differentiate this as a formal document, that is a reasonable deviation — but navbars, labels, and UI chrome should stay in Raleway/Open Sans to maintain brand alignment.

### 4.2 Custom CSS

Create `docs/.vitepress/theme/custom.css`:

```css
/* ============================================
   WESLEYAN DISCIPLINE — THEME OVERRIDES
   Brand: The Wesleyan Church (wesleyan.org)
   ============================================ */

/* --- Color tokens (TWC Brand Guide 2023) --- */
:root {
  /* Primary brand blues */
  --vp-c-brand-1: #0B496F;   /* Dark Blue — primary */
  --vp-c-brand-2: #39AAE1;   /* Light Blue — interactive */
  --vp-c-brand-3: #03344D;   /* Blue-Black — deep */
  --vp-c-brand-soft: rgba(11, 73, 111, 0.08);

  /* Secondary / accent */
  --twc-aqua: #40BCBC;
  --twc-light-blue-bg: #BDE6FA;

  /* Neutrals */
  --twc-dark-gray: #333132;
  --twc-mid-gray: #B8B9B9;
  --twc-light-gray: #E7E7E7;

  /* Typography — TWC brand fonts */
  /* Raleway for UI/display, Open Sans for body */
  --vp-font-family-base: 'Open Sans', system-ui, sans-serif;
  --vp-font-family-mono: 'Courier New', monospace;

  /* Content width — wider for a book-like feel */
  --vp-layout-max-width: 1440px;

  /* Line height for dense legal/church text */
  --vp-doc-line-height: 1.8;
}

/* --- Dark mode brand colors --- */
.dark {
  --vp-c-brand-1: #39AAE1;   /* Light Blue becomes primary in dark mode */
  --vp-c-brand-2: #40BCBC;   /* Aqua for secondary */
  --vp-c-brand-3: #BDE6FA;
  --vp-c-brand-soft: rgba(57, 170, 225, 0.12);
}

/* --- Nav bar --- */
.VPNav {
  border-bottom: 2px solid var(--vp-c-brand-1) !important;
}

.VPNavBarTitle .title {
  font-family: 'Raleway', system-ui, sans-serif;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--vp-c-brand-1);
  text-transform: uppercase;
  font-size: 0.9rem;
}

/* --- Home hero --- */
.VPHero .name {
  font-family: 'Raleway', system-ui, sans-serif;
  font-weight: 700;
  color: var(--vp-c-brand-1) !important;
  background: none !important;
  -webkit-text-fill-color: var(--vp-c-brand-1) !important;
  font-size: 3.5rem;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.VPHero .text {
  font-family: 'Raleway', system-ui, sans-serif;
  font-weight: 400;
  color: var(--twc-dark-gray) !important;
}

.VPHero .tagline {
  font-family: 'Open Sans', system-ui, sans-serif;
  color: #555 !important;
}

/* --- Sidebar --- */
.VPSidebarItem .text {
  font-family: 'Open Sans', system-ui, sans-serif;
  font-size: 0.875rem;
}

.VPSidebarItem.is-active > .item .text {
  color: var(--vp-c-brand-1);
  font-weight: 600;
}

/* --- Document body --- */
.vp-doc {
  /* Open Sans per brand guide. Swap to a serif if preferred for long-form reading. */
  font-family: 'Open Sans', system-ui, sans-serif;
  font-size: 1.0rem;
  line-height: 1.85;
  color: var(--twc-dark-gray);
}

/* --- Paragraph headings --- */
/* ¶125, ¶725:1, etc. */
.vp-doc h2 {
  font-family: 'Raleway', system-ui, sans-serif;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--vp-c-brand-1);
  border-bottom: 1px solid var(--twc-mid-gray);
  padding-bottom: 0.3em;
  margin-top: 2.5em;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.vp-doc h3 {
  font-family: 'Raleway', system-ui, sans-serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--vp-c-brand-3);
  margin-top: 1.75em;
}

.vp-doc h4 {
  font-family: 'Open Sans', system-ui, sans-serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--twc-dark-gray);
}

/* Chapter/Part headings (h1) */
.vp-doc h1 {
  font-family: 'Raleway', system-ui, sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: var(--vp-c-brand-1);
  border-bottom: 3px solid var(--vp-c-brand-1);
  padding-bottom: 0.4em;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* --- Cross-reference links --- */
/* TWC Light Blue (#39AAE1) for interactive elements per brand guide */
.vp-doc a[href*="#p"] {
  color: #39AAE1;
  text-decoration: none;
  border-bottom: 1px dotted #39AAE1;
  font-variant-numeric: tabular-nums;
}

.vp-doc a[href*="#p"]:hover {
  color: var(--vp-c-brand-1);
  border-bottom-style: solid;
}

/* --- Scripture references --- */
/* Wrap scripture citations in <cite> for styling */
.vp-doc cite {
  font-style: italic;
  color: #555;
  font-size: 0.9em;
  display: block;
  margin: 0.5em 0 0.5em 1.5em;
  border-left: 3px solid #dde3ec;
  padding-left: 0.75em;
}

/* --- Outline (right-hand TOC) --- */
.VPDocOutlineItem a {
  font-size: 0.8rem;
  color: #555;
}

.VPDocOutlineItem.active a {
  color: var(--vp-c-brand-1);
  font-weight: 600;
}

/* --- Feature cards on homepage --- */
.VPFeature {
  border: 1px solid var(--twc-mid-gray) !important;
  border-top: 3px solid var(--vp-c-brand-2) !important;
}

.VPFeature .title {
  font-family: 'Raleway', system-ui, sans-serif;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: var(--vp-c-brand-1);
}

/* --- Footer --- */
.VPFooter {
  border-top: 2px solid var(--vp-c-brand-1);
  font-family: 'Open Sans', system-ui, sans-serif;
}

/* --- Print styles --- */
@media print {
  .VPNav, .VPSidebar, .VPDocAside { display: none !important; }
  .vp-doc { font-size: 11pt; line-height: 1.6; }
  .vp-doc h2 { color: black; border-color: black; }
  a[href]::after { content: " (" attr(href) ")"; font-size: 0.8em; color: #666; }
}
```

### 4.3 Theme entry file

Create `docs/.vitepress/theme/index.ts`:

```typescript
import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default DefaultTheme
```

### 4.4 Loading the official TWC fonts

**Raleway** and **Open Sans** are both available free on Google Fonts. Add to `config.mts` head:

```typescript
head: [
  ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
  ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
  ['link', {
    rel: 'stylesheet',
    href: 'https://fonts.googleapis.com/css2?family=Raleway:wght@400;600;700;800&family=Open+Sans:ital,wght@0,400;0,600;1,400&display=swap'
  }],
]
```

Note: The brand guide specifies "Raleway TWC 2.0" — a customized version with preferred lining numerals and alternate W glyphs. Download it from wesleyan.org/brand and self-host it for pixel-perfect brand alignment. The Google Fonts version of Raleway is a close substitute if you don't need the customized glyphs.

**Self-hosting Raleway TWC 2.0:**

The `.otf` files have been converted to `.woff2` and are in `Raleway TWC 2.0/woff2/`. Copy that folder to `docs/public/fonts/` in your VitePress project.

Add to `custom.css`:

```css
@font-face {
  font-family: 'Raleway';
  src: url('/fonts/RalewayTWC-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Raleway';
  src: url('/fonts/RalewayTWC-Italic.woff2') format('woff2');
  font-weight: 400;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: 'Raleway';
  src: url('/fonts/RalewayTWC-SemiBold.woff2') format('woff2');
  font-weight: 600;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Raleway';
  src: url('/fonts/RalewayTWC-SemiBoldItalic.woff2') format('woff2');
  font-weight: 600;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: 'Raleway';
  src: url('/fonts/RalewayTWC-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Raleway';
  src: url('/fonts/RalewayTWC-BoldItalic.woff2') format('woff2');
  font-weight: 700;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: 'Raleway';
  src: url('/fonts/RalewayTWC-ExtraBold.woff2') format('woff2');
  font-weight: 800;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'Raleway';
  src: url('/fonts/RalewayTWC-ExtraBoldItalic.woff2') format('woff2');
  font-weight: 800;
  font-style: italic;
  font-display: swap;
}
```

When self-hosting Raleway TWC 2.0, remove the Google Fonts `<link>` tags from `config.mts` — you don't need both. Open Sans can still be loaded from Google Fonts since there's no custom TWC version of it.

---

## Phase 5 — Paragraph Index Page

Create `docs/index-of-paragraphs.md` — a full index allowing direct navigation to any paragraph number. This is a key navigational aid.

Structure it as a table or alphabetical list by paragraph range:

```markdown
# Paragraph Index

Jump directly to any paragraph. Format: [¶NNN](/path/to/file#pNNN)

## ¶1–499 Basic Principles
[¶1](/part-1/ch1-history#p1) · [¶2](#) · [¶3](#) · ...

## ¶500–999 Local Church Government
...
```

For large ranges, AI can generate this index automatically from the completed markdown files by scanning all `{#pNNN}` anchors.

**AI prompt to generate the index:**

```
Given these markdown files (paste content), extract every paragraph anchor 
in the format {#pNNN} or {#pNNN-N} and generate a markdown index page 
organized by Part and Chapter, with links in the format [¶NNN](filepath#pNNN).
```

---

## Phase 6 — Deployment

### Primary: Self-hosted at twcdiscipline.kal-el.net

Build locally or via CI, then deploy the static output to the server.

```bash
npm run docs:build
# output is in docs/.vitepress/dist — deploy this folder
```

Serve with nginx (recommended). Minimal config:

```nginx
server {
    listen 80;
    server_name twcdiscipline.kal-el.net;
    root /var/www/discipline/dist;
    index index.html;

    # Required for VitePress client-side routing
    location / {
        try_files $uri $uri/ $uri.html /index.html;
    }

    # Cache static assets
    location ~* \.(woff2|js|css|png|svg|ico)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Add SSL via Let's Encrypt: `certbot --nginx -d twcdiscipline.kal-el.net`

### CI/CD via GitHub Actions (recommended for ongoing updates)

Push to GitHub, auto-deploy to server on merge to `main`:

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run docs:build
      - name: Deploy to server
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          source: docs/.vitepress/dist/*
          target: /var/www/discipline/dist
          strip_components: 3
```

### Future migration to discipline.wesleyan.org

When ready to migrate:
1. Update `sitemap.hostname` in `config.mts` to `https://discipline.wesleyan.org`
2. Update the canonical meta tag in `head`
3. Point DNS for `discipline.wesleyan.org` to the same server
4. Add a redirect from the old MediaWiki URL patterns to the new paragraph anchors (nginx `rewrite` rules)

---

## Phase 7 — Quality Checks

Before publishing, verify:

- [ ] Every paragraph number in the original PDF has a corresponding anchor in markdown
- [ ] All cross-references resolve (no broken links) — run `npx vitepress build` and check for warnings
- [ ] Scripture citations display correctly
- [ ] Paragraph index covers the full ¶1–7999 range
- [ ] Search finds paragraphs by number (e.g., searching "725" returns ¶725)
- [ ] Site renders correctly on mobile
- [ ] Print stylesheet produces a clean printed version
- [ ] Spot-check 20+ paragraphs against the PDF for accuracy

**Link checker (run after build):**

```bash
npx broken-link-checker http://localhost:4173 --recursive
```

---

## Suggested AI Workflow for Content Conversion

Since this is a large document, batch the conversion work:

1. Extract the full PDF text to `raw-extract.txt` (Phase 2.1 script)
2. Split the raw text by Part/Chapter boundaries into separate `.txt` files
3. Feed each chapter to an AI tool using the prompt template in Phase 2.2
4. Save the output as the corresponding `.md` file
5. Manually review one chapter end-to-end before processing the rest — catch any patterns the AI missed
6. Build a find-and-replace list for any recurring conversion errors and apply across all files

**Estimated conversion scope:** ~80–100 markdown files, ~400 paragraphs with cross-references. With good AI tooling, the bulk conversion should take a few focused sessions.

---

## Reference

- VitePress docs: https://vitepress.dev
- The Wesleyan Church: https://www.wesleyan.org
- Existing Discipline wiki: https://discipline.wesleyan.org
- PDF source: *The Discipline of The Wesleyan Church 2022*

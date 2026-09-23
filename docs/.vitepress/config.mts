import { defineConfig } from 'vitepress'

const part = (title: string, links: { text: string; link: string }[]) => [{ text: title, items: links }]
const archivePart = (slug: string, title: string, chapters: [string, string][]) => [{
  text: title,
  items: [
    { text: `${title} Index`, link: `/2022/${slug}/` },
    ...chapters.map(([file, text]) => ({ text, link: `/2022/${slug}/${file}` })),
  ],
}]
const archiveSidebar = [
  { text: '2022 Archive', items: [
    { text: 'Archive Home', link: '/2022/' },
    { text: 'Preface', link: '/2022/preface' },
    { text: 'Paragraph Index', link: '/2022/index-of-paragraphs' },
    { text: 'Topical Index', link: '/2022/index-topical' },
    { text: 'Appendices', link: '/2022/appendices' },
  ] },
  ...archivePart('part-1', 'Part 1 — Basic Principles', [
    ['ch1-history', 'Chapter 1 — History'], ['ch2-mission', 'Chapter 2 — Mission of The Wesleyan Church'],
    ['ch3-church-law', 'Chapter 3 — Classification of Church Law'], ['ch4-constitution', 'Chapter 4 — The Constitution'], ['ch5-special-directions', 'Chapter 5 — Special Directions'],
  ]),
  ...archivePart('part-2', 'Part 2 — Local Church Government', [
    ['ch1-organization', 'Chapter 1 — Local Church Organization'], ['ch2-membership', 'Chapter 2 — Membership'], ['ch3-conference', 'Chapter 3 — Local Church Conference'],
    ['ch4-pastors', 'Chapter 4 — Pastors'], ['ch5-local-board', 'Chapter 5 — Local Board of Administration'], ['ch6-officers', 'Chapter 6 — Local Church Officers and Committees'],
  ]),
  ...archivePart('part-3', 'Part 3 — District Church Government', [
    ['ch1-organization', 'Chapter 1 — District Organization'], ['ch2-conference', 'Chapter 2 — District Conference'], ['ch3-board', 'Chapter 3 — District Board of Administration'],
    ['ch4-officers', 'Chapter 4 — District Officers and Committees'], ['ch5-administration', 'Chapter 5 — District Administration'], ['ch6-ministerial', 'Chapter 6 — District Ministerial Supervision'],
    ['ch7-missions', 'Chapter 7 — District Missions and Evangelism'], ['ch8-education', 'Chapter 8 — District Christian Education and Spiritual Formation'],
  ]),
  ...archivePart('part-4', 'Part 4 — General Church Government', [
    ['ch1-general-conference', 'Chapter 1 — General Conference'], ['ch2-general-board', 'Chapter 2 — General Board'], ['ch3-general-officials', 'Chapter 3 — General Officials of the Church'],
    ['ch4-general-administration', 'Chapter 4 — General Administration'], ['ch5-communication-admin', 'Chapter 5 — Communication and Administration Division'],
    ['ch6-global-partners', 'Chapter 6 — Global Partners Division'], ['ch7-multiplication-discipleship', 'Chapter 7 — Church Multiplication and Discipleship Division'],
    ['ch8-education-clergy', 'Chapter 8 — Education and Clergy Development Division'], ['ch9-boundaries', 'Chapter 9 — Boundaries'],
  ]),
  ...archivePart('part-5', 'Part 5 — World Organization', [
    ['ch1-basic-principles', 'Chapter 1 — Basic Principles (World Organization)'], ['ch2-conferences', 'Chapter 2 — General Conferences and Established National/Regional Conferences'], ['ch3-international', 'Chapter 3 — International Conference of The Wesleyan Church'],
  ]),
  ...archivePart('part-6', 'Part 6 — Ministry', [
    ['ch1-ministerial-orders', 'Chapter 1 — Ministerial Orders and Regulations'], ['ch2-ministerial-education', 'Chapter 2 — Ministerial Education'], ['ch3-ministerial-appointments', 'Chapter 3 — Ministerial Appointments'], ['ch4-special-lay-ministries', 'Chapter 4 — Special Lay Ministries'],
  ]),
  ...archivePart('part-7', 'Part 7 — Corporations', [
    ['ch1-local-church-corporations', 'Chapter 1 — Local Church Corporations'], ['ch2-district-corporations', 'Chapter 2 — District Corporations'], ['ch3-twc-corporation', 'Chapter 3 — The Wesleyan Church Corporation'], ['ch4-subsidiary-corporations', 'Chapter 4 — Subsidiary and Affiliate Corporations'], ['ch5-pension-corporation', 'Chapter 5 — Pension Corporation'],
  ]),
  ...archivePart('part-8', 'Part 8 — Property', [
    ['ch1-general-principles', 'Chapter 1 — General Regulations'], ['ch2-local-church-property', 'Chapter 2 — Local Church Property'], ['ch3-district-property', 'Chapter 3 — District Property'], ['ch4-general-church-property', 'Chapter 4 — General Church Property'],
  ]),
  ...archivePart('part-9', 'Part 9 — Judiciary', [['ch1-general-regulations', 'Chapter 1 — General Principles']]),
  ...archivePart('part-10', 'Part 10 — The Ritual', [
    ['ch1-baptism', 'Chapter 1 — Baptism'], ['ch2-reception', 'Chapter 2 — Reception of Members'], ['ch3-lords-supper', 'Chapter 3 — The Lord’s Supper'], ['ch4-marriage', 'Chapter 4 — Marriage'], ['ch5-burial', 'Chapter 5 — Burial of the Dead'], ['ch6-ordination', 'Chapter 6 — Ordination of Ministers'], ['ch7-commissioning', 'Chapter 7 — Commissioning of Ministers'], ['ch8-commissioning-lay', 'Chapter 8 — Commissioning of Lay Workers'], ['ch9-installation', 'Chapter 9 — Installation Ceremonies'], ['ch10-dedication', 'Chapter 10 — Dedication Services'],
  ]),
  ...archivePart('part-11', 'Part 11 — Forms', [['ch1-church-letters', 'Chapter 1 — Church Letters'], ['ch2-service-credentials', 'Chapter 2 — Service Credentials']]),
]

export default defineConfig({
  title: 'The Discipline',
  description: 'The governing document of The Wesleyan Church, 2026 Edition',
  base: '/',
  sitemap: { hostname: 'https://twcdiscipline.kal-el.net' },
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#0B496F' }],
    ['meta', { name: 'robots', content: 'index, follow' }],
    ['link', { rel: 'canonical', href: 'https://twcdiscipline.kal-el.net' }],
    ['link', { rel: 'stylesheet', href: '/theme-override.css?v=2' }],
  ],
  themeConfig: {
    logo: '/wesleyan-logo.svg', siteTitle: 'The Discipline',
    nav: [
      { text: 'Home', link: '/' },
      { text: 'The Discipline', items: [
        { text: 'Part 1 — Basic Principles (¶1–499)', link: '/part-1/' },
        { text: 'Part 2 — Local Church Government (¶500–999)', link: '/part-2/' },
        { text: 'Part 3 — District Church Government (¶1000–1499)', link: '/part-3/' },
        { text: 'Part 4 — General Church Government (¶1500–2499)', link: '/part-4/' },
        { text: 'Part 5 — World Organization (¶2500–2999)', link: '/part-5/' },
        { text: 'Part 6 — Ministry (¶3000–3499)', link: '/part-6/' },
        { text: 'Part 7 — Corporations (¶4000–4499)', link: '/part-7/' },
        { text: 'Part 8 — Property (¶4500–4999)', link: '/part-8/' },
        { text: 'Part 9 — Judiciary (¶5000–5004)', link: '/part-9/' },
        { text: 'Part 10 — The Ritual (¶5500–5999)', link: '/part-10/' },
        { text: 'Part 11 — Forms (¶6000–6499)', link: '/part-11/' },
        { text: 'Appendix B — Affiliate Churches', link: '/appendices/appendix-b-affiliate-church-agreement' },
      ] },
      { text: 'Paragraph Index', link: '/index-of-paragraphs-staging' },
      { text: 'Topical Index', link: '/topical-index-staging' },
      { text: '2022 Archive', link: '/2022/' },
    ],
    sidebar: { '/2022/': archiveSidebar, '/': [
      { text: '2026 Edition', items: [
        { text: 'Home', link: '/' }, { text: 'Front Matter and Contents', link: '/front-matter-and-contents-staging' },
        { text: 'Paragraph Index', link: '/index-of-paragraphs-staging' }, { text: 'Topical Index', link: '/topical-index-staging' },
        { text: 'Additional Source Sections', link: '/uncertain-special-sections-staging' },
        { text: 'Appendix B — Affiliate Churches', link: '/appendices/appendix-b-affiliate-church-agreement' },
      ] },
      ...part('Part 1 — Basic Principles', [
        { text: 'Part 1 Index', link: '/part-1/' }, { text: 'Ch. 1 — History', link: '/part-1/ch1-history' },
        { text: 'Ch. 2 — Mission of the Wesleyan Church', link: '/part-1/ch2-mission-of-the-wesleyan-church' },
        { text: 'Ch. 3 — Classification of Church Law', link: '/part-1/ch3-classification-of-church-law' },
        { text: 'Ch. 4 — The Constitution of the North American General Conference', link: '/part-1/ch4-the-constitution-of-the-north-american-general-conference' },
        { text: 'Ch. 5 — Special Directions', link: '/part-1/ch5-special-directions' },
      ]),
      ...part('Part 2 — Local Church Government', [
        { text: 'Part 2 Index', link: '/part-2/' }, { text: 'Ch. 1 — Local Church Organization', link: '/part-2/ch1-local-church-organization' },
        { text: 'Ch. 2 — Membership', link: '/part-2/ch2-membership' }, { text: 'Ch. 3 — Local Church Conference', link: '/part-2/ch3-local-church-conference' },
        { text: 'Ch. 4 — Pastors', link: '/part-2/ch4-pastors' }, { text: 'Ch. 5 — Local Board of Administration', link: '/part-2/ch5-local-board-of-administration' },
        { text: 'Ch. 6 — Local Church Officers and Committees', link: '/part-2/ch6-local-church-officers-and-committees' },
      ]),
      ...part('Part 3 — District Church Government', [
        { text: 'Part 3 Index', link: '/part-3/' }, { text: 'Ch. 1 — District Organization', link: '/part-3/ch1-district-organization' },
        { text: 'Ch. 2 — District Conference', link: '/part-3/ch2-district-conference' }, { text: 'Ch. 3 — District Board of Administration', link: '/part-3/ch3-district-board-of-administration' },
        { text: 'Ch. 4 — District Officers and Committees', link: '/part-3/ch4-district-officers-and-committees' },
        { text: 'Ch. 5 — District Administration', link: '/part-3/ch5-district-administration' }, { text: 'Ch. 6 — District Ministerial Supervision', link: '/part-3/ch6-district-ministerial-supervision' },
      ]),
      ...part('Part 4 — General Church Government', [
        { text: 'Part 4 Index', link: '/part-4/' }, { text: 'Ch. 1 — General Conference', link: '/part-4/ch1-general-conference' },
        { text: 'Ch. 2 — General Board', link: '/part-4/ch2-general-board' }, { text: 'Ch. 3 — General Officials of the Church', link: '/part-4/ch3-general-officials-of-the-church' },
        { text: 'Ch. 4 — General Administration', link: '/part-4/ch4-general-administration' }, { text: 'Ch. 5 — Communications', link: '/part-4/ch5-communications' },
        { text: 'Ch. 6 — Global Partners', link: '/part-4/ch6-global-partners' }, { text: 'Ch. 7 — Church Multiplication and Discipleship', link: '/part-4/ch7-church-multiplication-and-discipleship' },
        { text: 'Ch. 8 — Wesleyan Higher Education', link: '/part-4/ch8-wesleyan-higher-education' }, { text: 'Ch. 9 — Boundaries', link: '/part-4/ch9-boundaries' },
      ]),
      ...part('Part 5 — World Organization', [
        { text: 'Part 5 Index', link: '/part-5/' }, { text: 'Ch. 1 — Basic Principles', link: '/part-5/ch1-basic-principles' },
        { text: 'Ch. 2 — General Conferences and Established National/Regional Conferences', link: '/part-5/ch2-general-conferences-and-established-national-regional-conferences' },
        { text: 'Ch. 3 — International Conference of the Wesleyan Church', link: '/part-5/ch3-international-conference-of-the-wesleyan-church' },
      ]),
      ...part('Part 6 — Ministry', [
        { text: 'Part 6 Index', link: '/part-6/' }, { text: 'Ch. 1 — Ministerial Orders and Regulations', link: '/part-6/ch1-ministerial-orders-and-regulations' },
        { text: 'Ch. 2 — Ministerial Education', link: '/part-6/ch2-ministerial-education' }, { text: 'Ch. 3 — Ministerial Appointments', link: '/part-6/ch3-ministerial-appointments' },
        { text: 'Ch. 4 — Special Lay Ministries', link: '/part-6/ch4-special-lay-ministries' },
      ]),
      ...part('Part 7 — Corporations', [
        { text: 'Part 7 Index', link: '/part-7/' }, { text: 'Ch. 1 — Local Church Corporations', link: '/part-7/ch1-local-church-corporations' },
        { text: 'Ch. 2 — District Corporations', link: '/part-7/ch2-district-corporations' }, { text: 'Ch. 3 — The Wesleyan Church Corporation', link: '/part-7/ch3-the-wesleyan-church-corporation' },
        { text: 'Ch. 4 — Subsidiary and Affiliate Corporations and Adjunct Entities', link: '/part-7/ch4-subsidiary-and-affiliate-corporations-and-adjunct-entities' },
        { text: 'Ch. 5 — Pension Corporation', link: '/part-7/ch5-pension-corporation' },
      ]),
      ...part('Part 8 — Property', [
        { text: 'Part 8 Index', link: '/part-8/' }, { text: 'Ch. 1 — General Regulations', link: '/part-8/ch1-general-regulations' },
        { text: 'Ch. 2 — Local Church Property', link: '/part-8/ch2-local-church-property' }, { text: 'Ch. 3 — District Property', link: '/part-8/ch3-district-property' },
        { text: 'Ch. 4 — General Church Property', link: '/part-8/ch4-general-church-property' },
      ]),
      ...part('Part 9 — Judiciary', [ { text: 'Part 9 Index', link: '/part-9/' }, { text: 'Ch. 1 — General Principles', link: '/part-9/ch1-general-principles' } ]),
      ...part('Part 10 — The Ritual', [
        { text: 'Part 10 Index', link: '/part-10/' }, { text: 'Ch. 1 — Baptism', link: '/part-10/ch1-baptism' }, { text: 'Ch. 2 — Reception of Members', link: '/part-10/ch2-reception-of-members' },
        { text: 'Ch. 3 — The Lord’s Supper', link: '/part-10/ch3-the-lords-supper' }, { text: 'Ch. 4 — Marriage', link: '/part-10/ch4-marriage' }, { text: 'Ch. 5 — Burial', link: '/part-10/ch5-burial' },
        { text: 'Ch. 6 — Ordination of Ministers', link: '/part-10/ch6-ordination-of-ministers' }, { text: 'Ch. 7 — Commissioning of Ministers', link: '/part-10/ch7-commissioning-of-ministers' },
        { text: 'Ch. 8 — Commissioning of Lay Workers', link: '/part-10/ch8-commissioning-of-lay-workers' }, { text: 'Ch. 9 — Installation Ceremonies', link: '/part-10/ch9-installation-ceremonies' },
        { text: 'Ch. 10 — Dedication Services', link: '/part-10/ch10-dedication-services' },
      ]),
      ...part('Part 11 — Forms', [ { text: 'Part 11 Index', link: '/part-11/' }, { text: 'Ch. 1 — Church Letters', link: '/part-11/ch1-church-letters' }, { text: 'Ch. 2 — Service Credentials', link: '/part-11/ch2-service-credentials' } ]),
    ] },
    search: { provider: 'local' }, outline: { level: [2, 6], label: 'On this page' },
    editLink: { pattern: 'https://github.com/tietjinator/discipline-site/edit/main/docs/:path', text: 'Suggest a correction' },
    footer: { message: 'The Discipline of The Wesleyan Church, 2026 Edition · 2022 Archive', copyright: 'Copyright © 2026 Wesleyan Publishing House' },
  },
})

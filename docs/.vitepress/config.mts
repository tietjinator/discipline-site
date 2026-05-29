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
    // Load Open Sans from Google Fonts (Raleway is self-hosted as Raleway TWC 2.0)
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
      pattern: 'https://github.com/tietjinator/discipline-site/edit/main/docs/:path',
      text: 'Suggest a correction'
    },

    footer: {
      message: 'The Discipline of The Wesleyan Church, 2022 Edition',
      copyright: 'Copyright © 2022 Wesleyan Publishing House'
    }
  }
})

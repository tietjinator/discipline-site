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
    // Load Open Sans from Google Fonts (Raleway TWC 2.0 is self-hosted via @font-face)
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,400;0,600;1,400&display=swap' }],
  ],

  themeConfig: {
    logo: '/wesleyan-logo.svg',
    siteTitle: 'The Discipline 2022',

    nav: [
      { text: 'Home', link: '/' },
      {
        text: 'The Discipline',
        items: [
          { text: 'Part 1 — Basic Principles (¶1–499)', link: '/part-1/' },
          { text: 'Part 2 — Local Church Government (¶500–999)', link: '/part-2/' },
          { text: 'Part 3 — District Government (¶1000–1499)', link: '/part-3/' },
          { text: 'Part 4 — General Church Government (¶1500–2499)', link: '/part-4/' },
          { text: 'Part 5 — World Organization (¶2500–2999)', link: '/part-5/' },
          { text: 'Part 6 — Ministry (¶3000–3499)', link: '/part-6/' },
          { text: 'Part 7 — Corporations (¶4000–4499)', link: '/part-7/' },
          { text: 'Part 8 — Property (¶4500–4999)', link: '/part-8/' },
          { text: 'Part 9 — Judiciary (¶5000–5004)', link: '/part-9/' },
          { text: 'Part 10 — The Ritual (¶5500–5999)', link: '/part-10/' },
          { text: 'Part 11 — Forms (¶6000–6499)', link: '/part-11/' },
        ]
      },
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
          { text: 'Ch. 1 — General Conference (¶1500–1599)', link: '/part-4/ch1-general-conference' },
          { text: 'Ch. 2 — General Board (¶1600–1799)', link: '/part-4/ch2-general-board' },
          { text: 'Ch. 3 — General Officials (¶1800–1899)', link: '/part-4/ch3-general-officials' },
          { text: 'Ch. 4 — General Administration (¶1900–2099)', link: '/part-4/ch4-general-administration' },
          { text: 'Ch. 5 — Communication & Admin (¶2100–2199)', link: '/part-4/ch5-communication-admin' },
          { text: 'Ch. 6 — Global Partners (¶2200–2299)', link: '/part-4/ch6-global-partners' },
          { text: 'Ch. 7 — Multiplication & Discipleship (¶2300–2337)', link: '/part-4/ch7-multiplication-discipleship' },
          { text: 'Ch. 8 — Education & Clergy (¶2338–2399)', link: '/part-4/ch8-education-clergy' },
          { text: 'Ch. 9 — Boundaries (¶2400–2499)', link: '/part-4/ch9-boundaries' },
        ]
      }],
      '/part-5/': [{
        text: 'Part 5 — World Organization',
        items: [
          { text: 'Ch. 1 — Basic Principles (¶2500–2549)', link: '/part-5/ch1-basic-principles' },
          { text: 'Ch. 2 — General Conferences (¶2550–2649)', link: '/part-5/ch2-conferences' },
          { text: 'Ch. 3 — International Conference (¶2650–2999)', link: '/part-5/ch3-international' },
        ]
      }],
      '/part-6/': [{
        text: 'Part 6 — Ministry',
        items: [
          { text: 'Ch. 1 — Ministerial Orders (¶3000–3249)', link: '/part-6/ch1-ministerial-orders' },
          { text: 'Ch. 2 — Ministerial Education (¶3250–3299)', link: '/part-6/ch2-ministerial-education' },
          { text: 'Ch. 3 — Ministerial Appointments (¶3300–3390)', link: '/part-6/ch3-ministerial-appointments' },
          { text: 'Ch. 4 — Special Lay Ministries (¶3400–3499)', link: '/part-6/ch4-special-lay-ministries' },
        ]
      }],
      '/part-7/': [{
        text: 'Part 7 — Corporations',
        items: [
          { text: 'Ch. 1 — Local Church Corp. (¶4000–4099)', link: '/part-7/ch1-local-church-corporations' },
          { text: 'Ch. 2 — District Corp. (¶4100–4199)', link: '/part-7/ch2-district-corporations' },
          { text: 'Ch. 3 — TWC Corporation (¶4200–4299)', link: '/part-7/ch3-twc-corporation' },
          { text: 'Ch. 4 — Subsidiary Corp. (¶4300–4399)', link: '/part-7/ch4-subsidiary-corporations' },
          { text: 'Ch. 5 — Pension Corp. (¶4400–4499)', link: '/part-7/ch5-pension-corporation' },
        ]
      }],
      '/part-8/': [{
        text: 'Part 8 — Property',
        items: [
          { text: 'Ch. 1 — General Principles (¶4500–4549)', link: '/part-8/ch1-general-principles' },
          { text: 'Ch. 2 — Local Church Property (¶4550–4699)', link: '/part-8/ch2-local-church-property' },
          { text: 'Ch. 3 — District Property (¶4700–4849)', link: '/part-8/ch3-district-property' },
          { text: 'Ch. 4 — General Church Property (¶4850–4999)', link: '/part-8/ch4-general-church-property' },
        ]
      }],
      '/part-9/': [{
        text: 'Part 9 — Judiciary',
        items: [
          { text: 'Ch. 1 — General Regulations (¶5000–5004)', link: '/part-9/ch1-general-regulations' },
        ]
      }],
      '/part-10/': [{
        text: 'Part 10 — The Ritual',
        items: [
          { text: 'Ch. 1 — Baptism (¶5500–5549)', link: '/part-10/ch1-baptism' },
          { text: 'Ch. 2 — Reception of Members (¶5550–5599)', link: '/part-10/ch2-reception' },
          { text: 'Ch. 3 — The Lord\'s Supper (¶5600–5649)', link: '/part-10/ch3-lords-supper' },
          { text: 'Ch. 4 — Marriage (¶5650–5699)', link: '/part-10/ch4-marriage' },
          { text: 'Ch. 5 — Burial of the Dead (¶5700–5749)', link: '/part-10/ch5-burial' },
          { text: 'Ch. 6 — Ordination (¶5750–5799)', link: '/part-10/ch6-ordination' },
          { text: 'Ch. 7 — Commissioning (¶5800–5849)', link: '/part-10/ch7-commissioning' },
          { text: 'Ch. 8 — Commissioning Lay Workers (¶5850–5899)', link: '/part-10/ch8-commissioning-lay' },
          { text: 'Ch. 9 — Installation (¶5900–5949)', link: '/part-10/ch9-installation' },
          { text: 'Ch. 10 — Dedication (¶5950–5999)', link: '/part-10/ch10-dedication' },
        ]
      }],
      '/part-11/': [{
        text: 'Part 11 — Forms',
        items: [
          { text: 'Ch. 1 — Church Letters (¶6000–6249)', link: '/part-11/ch1-church-letters' },
          { text: 'Ch. 2 — Service Credentials (¶6250–6499)', link: '/part-11/ch2-service-credentials' },
        ]
      }],
    },

    search: {
      provider: 'local'
    },

    outline: {
      level: [2, 6],
      label: 'On this page'
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

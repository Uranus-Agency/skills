# BB — Yektanet Digital Billboard Developer

**BB** is a Claude Code plugin that generates production-ready Yektanet Digital Billboard (DB) ad packages for Uranus Agency.

## What It Does

Given a campaign scenario and asset list, BB generates a complete 4-file ad package:

| File | Purpose |
|------|---------|
| `index.html` | Full HTML document (RTL Persian, 150px frame) |
| `style.css` | Full CSS with mandatory animations (tapesh, float, pulse) |
| `script.js` | Full GSAP animations, tracking events, 60s auto-reload |
| `tags.js` | Yektanet event tracking boilerplate (never modified) |

## How to Use

### Automatic (Skill)
Just describe a billboard scenario in conversation — BB activates automatically:
> "Build a billboard for a gold jewelry brand with 3 products and a dark theme"

### Manual (Command)
```
/bb Black Friday sale for Digikala, 5 products cycling, intro truck
```

## Features

- **10 animation patterns:** 3-Act, Fade-In, Product Carousel, Fortune Wheel, Countdown, Video BG, Live Data Chart, Scroll Reactive, Calculator, Two-Slide
- **Automatic asset mapping:** Recognizes logo, cta, product, bg, intro, stick, percent by filename
- **Full Yektanet compliance:** tags.js, click_url handler, fire_tag tracking
- **RTL Persian:** `dir="rtl"`, `lang="fa"`, Persian numerals
- **GSAP animations:** Timeline orchestration, product cycling, flying clones
- **Quality checklist:** Verified before every output

## Technical Spec

- Frame: 150px tall, 100% wide, sticky bottom, inside Yektanet iframe
- All elements: `position: fixed`
- GSAP CDN: `cdn.yektanet.com/assets/3rdparty/gsap@3.12.5/gsap.min.js`
- Auto-reload: 60s with LOOP tracking event

## Components

```
bb/
├── plugin.json
├── README.md
├── skills/
│   └── bb/
│       ├── SKILL.md                    # Core skill (auto-activates)
│       └── references/
│           ├── spec.md                 # Frame specification
│           ├── animation-patterns.md   # 10 production patterns
│           └── design-system.md        # Visual design rules
└── commands/
    └── bb.md                           # /bb slash command
```

## Author

Uranus Agency — dev@uranus-agency.ir

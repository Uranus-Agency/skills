---
name: BB creation log - Bitpin 40X
description: Bitpin 40X campaign billboard — two-phase impact+CTA pattern, crypto surge matrix bg, coin burst + 40X slam + copy compress
type: project
---

Brand: Bitpin (crypto exchange)
Campaign: 40X — تا ۴۰ برابر سود بیشتر در معامله (up to 40x profit with $500 prize competition)
Folder: BB/bitpin/40x/
Pattern: Two-phase (Impact → Call-to-Action), poke-out 40X hero

## Brand Colors
- Background: deep dark teal `#070f0c` / `#091510`
- Brand green: `#3DD68C` / `#4EF09D`
- Gold/yellow: `#F5C842` (copy headline, CTA button)

## Assets
- 40X.png: 3D gold "40x" text + green upward arrow (POKE-OUT, left:2px, bottom:5px, height:145px)
- coins.png: 7 floating crypto coins (BTC×2, XRP, ETH, etc.) — transparent, clusters upper-right of PNG
- copy.png: combined headline+subtitle PNG ("تا ۴۰ برابر سود | با چاشنی رقابت و ۵۰۰ دلار جایزه")
- cta.png: gold pill button "معامله رمزارز"
- logo.png: Bitpin white+green logo (very wide/thin, ~4:1 ratio)

## Layout (400×150px)
- Left zone (x:0–165px): 40X poke-out + coins overlay
- Right zone (x:180–395px): logo (top), copy (center), CTA (bottom Phase 2)
- Coins at left:5px, top:18px, width:162px — partially poke above bg for depth
- 40X z-index:2, coins z-index:4 (coins in front of arrow for orbital feel)

## bg.html — Crypto Surge Matrix (390×120px)
- radial-gradient dark teal base (#070f0c → #0C1E16)
- 4 animated glow orbs (2 green, 1 gold, 1 accent)
- Canvas: 75 upward-drifting particles (70% green, 15% gold, 15% white)
- Candlestick bar decorations (mostly green = bull market)
- Price surge lines: diagonal glowing lines shoot up from bottom-left with gradient + glow tip, every ~3s
- Circuit grid (subtle, 18px/22px spacing)
- Shimmer sweep every 4.5s
- Right-side readability overlay (240px wide gradient)

## GSAP Timeline (~10s loop)
Phase 1 (0–4.8s): coins burst in (back.out) → 40X SLAM (back.out(3.2)) → flash impact → coins micro-bounce → logo slides down → copy slides in from right → coins start idle float (via tl.call)
Phase 2 (4.9–9.3s): copy scale:0.71 y:-13 (transformOrigin:top right) → CTA rises up → CTA tapesh pulse (via tl.call)
Exit (9.4s): all fade out with stagger:0.04

## Copy sizing challenge
copy.png is roughly square (all-in-one headline+subtitle). Solution: Phase 1 at width:118px (scale:1), Phase 2 compressed to scale:0.71 + y:-13 to make room for CTA. transformOrigin:"top right" ensures it shrinks toward logo (top-right anchor).

## Key Technique
Two-phase "copy compress" trick: Phase 1 shows copy full size, Phase 2 GSAP scale+y transform compresses it upward to reveal CTA slot below. No second copy asset needed.

Date: 2026-04-18

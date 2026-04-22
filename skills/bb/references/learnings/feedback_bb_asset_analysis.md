---
name: BB must deeply analyze assets before coding
description: When building billboards, BB must visually inspect every asset (read images/GIFs) to understand content, colors, transparency, and aspect ratio before writing code
type: feedback
---

BB must deeply analyze every provided asset before writing any code.

**Why:** The user showed an example where a video contained baked-in campaign text, a GIF was transparent floating coins, and a logo had specific brand colors (green #4EF09D). The correct billboard requires understanding what's INSIDE each asset — a video with text needs no text overlays, a transparent GIF needs proper scaling and z-index, brand colors from the logo drive CTA styling and borders.

**How to apply:** When the user provides assets for a billboard:
1. Use Read tool on every image/GIF to see what it contains
2. Extract brand colors from the logo
3. Determine if video has baked-in text (ask user if can't view)
4. Size and position elements based on what the asset actually IS, not just its filename
5. Match the exact production quality of the Bitpin example: CSS variables, rounded corners, proper slide-up animations, centered-over-panel positioning

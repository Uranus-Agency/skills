---
name: BB CSS Mask Transparency for BG Fade
description: Animate partial transparency on bg card using CSS mask-image via GSAP onUpdate — keeps all canvas animations intact, only fades the color
type: feedback
---

## Pattern: Transparent Left Zone on BG Card

Instead of shrinking the background (scaleX), fade the left portion to transparent while keeping all canvas animations running inside.

### Why not scaleX?
`scaleX:0.65` physically shrinks the card — phone frame and key visual overlap empty space. The mask approach keeps the card at full width but makes the left portion visually transparent.

### Implementation
```javascript
// In Phase 2 timeline (replaces scaleX tween):
var _mp = {pos: -20};  // start value: -20 = transparent zone is off-screen
tl.to(_mp, {
  pos: 35,             // end value: left 35% becomes transparent
  duration: 0.55,
  ease: 'power2.inOut',
  onUpdate: function(){
    var g = 'linear-gradient(to right,transparent '+_mp.pos+'%,black '+(_mp.pos+22)+'%,black 100%)';
    bgWrap.style.webkitMaskImage = g;
    bgWrap.style.maskImage = g;
  }
}, '-=0.15');
```

### In resetAll (clear mask before Phase 1):
```javascript
bgWrap.style.webkitMaskImage = 'none';
bgWrap.style.maskImage = 'none';
```

### How the gradient works
- `pos:-20`: gradient = `transparent -20%, black 2%` → fully opaque (transparent zone is off-screen left)
- `pos:35`: gradient = `transparent 35%, black 57%` → left 35% transparent, smooth fade to fully opaque
- The 22% transition zone creates a smooth gradient edge (not hard cut)

### Visible bg center calculation (for CTA/logo placement)
```
bg card: left:5px, width:380px
after 35% fade: visible area starts at 5 + 380×0.35 = 138px, ends at 385px
center of visible bg = (138 + 385) / 2 ≈ 262px
→ animate ctaWrap to left:262, xPercent:-50 for perfect centering
```

### Canvas animations are unaffected
The mask clips the visual output of the element but does NOT stop JavaScript execution inside the iframe. All particles, nodes, and effects continue running behind the transparent area.

### bg.html text readability overlay (separate pattern)
To reduce animation noise behind text in Phase 1, add a static overlay to bg.html:
```html
<div style="position:absolute;top:0;left:155px;right:0;bottom:0;
  background:linear-gradient(to right,transparent 0%,rgba(R,G,B,0.38) 35%,rgba(R,G,B,0.52) 100%);
  z-index:8;pointer-events:none;"></div>
```
Use campaign-matched dark color (e.g. purple bg → `rgba(18,0,55,0.38)`). Left side (behind key visual) stays fully animated.

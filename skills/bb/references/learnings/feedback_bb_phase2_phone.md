---
name: BB Phase 2 — Live Phone Frame Pattern
description: Two-phase billboard structure: Phase 1 content showcase → Phase 2 live app iframe in phone frame with CTA + logo centered
type: feedback
---

## Pattern: Two-Phase Billboard with App Showcase

After Phase 1 (8s content showcase), transition to Phase 2 (6s phone + CTA) then loop.

### Phone Frame HTML Structure
```html
<div class="ph" id="ph">
  <div class="ph-notch"></div>
  <div class="ph-screen">
    <div class="ph-scroll" id="phScroll">
      <iframe src="https://example.ir/page" loading="eager"></iframe>
    </div>
  </div>
  <div class="ph-bar"></div>
</div>
```

### Phone Frame CSS
```css
.ph{position:absolute;left:5px;top:5px;width:130px;height:258px;background:#1c1c1e;border:2px solid rgba(255,255,255,0.16);border-radius:24px;box-shadow:0 8px 32px rgba(0,0,0,0.65);z-index:18;opacity:0;overflow:visible;}
.ph-notch{position:absolute;top:8px;left:50%;transform:translateX(-50%);width:32px;height:9px;background:#000;border-radius:5px;z-index:5;}
.ph-screen{position:absolute;top:3px;left:3px;right:3px;bottom:3px;border-radius:22px;overflow:hidden;background:#000;}
.ph-scroll{position:absolute;top:0;left:0;width:124px;height:900px;}
.ph-scroll iframe{position:absolute;top:0;left:0;width:375px;height:2800px;border:none;transform:scale(0.3307);transform-origin:top left;pointer-events:none;}
.ph-bar{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);width:38px;height:4px;background:rgba(255,255,255,0.18);border-radius:3px;z-index:5;}
```
Scale formula: `phone_screen_inner_width / 375`. For 130px phone: (130-6)/375 = 0.3307.

### Phase 2 GSAP Timeline
```javascript
// product exits
tl.to(product,{opacity:0,y:-45,scale:0.88,duration:0.35,ease:'power2.in'});
// texts exit
tl.to([headline,subtitle],{opacity:0,x:12,stagger:0.04,duration:0.28,ease:'power2.in'},'-=0.28');
// bg left side fades with CSS mask
var _mp={pos:-20};
tl.to(_mp,{pos:35,duration:0.55,ease:'power2.inOut',
  onUpdate:function(){
    var g='linear-gradient(to right,transparent '+_mp.pos+'%,black '+(_mp.pos+22)+'%,black 100%)';
    bgWrap.style.webkitMaskImage=g;bgWrap.style.maskImage=g;
  }},'-=0.15');
// CTA moves to center of visible bg (x=262 for 380px wide bg at 35% fade)
tl.to(ctaWrap,{left:262,xPercent:-50,scale:1.28,y:-3,duration:0.5,ease:'back.out(2)'},'-=0.4');
// logo appears above CTA
tl.fromTo(yjLabel,{opacity:0,scale:0.4,xPercent:-50},{opacity:1,scale:1,xPercent:-50,duration:0.55,ease:'back.out(2)',immediateRender:false},'-=0.2');
// phone enters from left
tl.fromTo(ph,{opacity:0,x:-80},{opacity:1,x:0,duration:0.6,ease:'back.out(1.4)',immediateRender:false},'-=0.3');
// start scroll + pulse
tl.call(function(){
  phoneTween = gsap.to(phScroll,{y:-260,duration:12,ease:'power1.inOut'});
  ctaPulse2  = gsap.to(ctaWrap,{scale:1.22,duration:1.0,ease:'sine.inOut',yoyo:true,repeat:-1});
  gsap.to(yjLabel,{scale:1.1,duration:1.0,ease:'sine.inOut',yoyo:true,repeat:-1,delay:0.5});
});
tl.to({},{duration:6});
```

### resetAll additions
```javascript
bgWrap.style.webkitMaskImage='none'; bgWrap.style.maskImage='none';
// restore CTA original position (different per campaign)
gsap.set(ctaWrap, {left:ORIGINAL_LEFT, xPercent:0});
gsap.set(yjLabel, {opacity:0, scale:1, xPercent:-50});
gsap.set(ph,      {opacity:0, x:-80});
gsap.set(phScroll,{y:0});
```

### CTA + Logo Centering Math
- bg card: left:5px, width:380px → right edge at 385px
- After 35% mask fade: visible bg starts at 5 + 380×0.35 = 138px
- Center of visible bg: (138 + 385) / 2 = **261.5px → use left:262**
- Logo inside ctaWrap: `position:absolute; bottom:100%; left:50%` + GSAP `xPercent:-50` — centers logo over CTA
- **CRITICAL**: Do NOT use CSS `transform:translateX(-50%)` on logo — GSAP overrides it. Use `xPercent:-50` in GSAP only.

### Logo (yekjoo brand mark) placement
```html
<!-- inside ctaWrap, as first child -->
<img class="yj-label" id="yjLabel" src="yeklogo.png" alt="یکجو">
```
```css
.yj-label{position:absolute;bottom:100%;left:50%;height:44px;width:auto;margin-bottom:8px;opacity:0;filter:drop-shadow(0 0 8px rgba(255,255,255,0.5));}
/* NO transform:translateX(-50%) — let GSAP handle xPercent */
```

### Separate tweens to kill
```javascript
var phoneTween = null, ctaPulse2 = null;
function killSep(){
  if(phoneTween){phoneTween.kill();phoneTween=null;}
  if(ctaPulse2){ctaPulse2.kill();ctaPulse2=null;}
}
```

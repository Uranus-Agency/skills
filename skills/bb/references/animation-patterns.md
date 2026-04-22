# BB Animation Patterns — Complete Production Code

## Pattern 1: Standard 3-Act (Default — 70%+ of campaigns)

**Use when:** There's an intro element (truck, mascot, ribbon) that crosses the screen, then the main offer reveals.

**Timeline:** Act 1 (0–8s) → Act 2 (8–14s) → Act 3 (14–60s) → Loop

### HTML Structure
```html
<img class="intro" src="intro.png" />
<img class="bg" src="bg.png" />
<img class="logo" src="logo.png" />
<img class="overline" src="overline.png" />
<img class="percent" src="percent.png" />
<img class="product product1" src="product1.png" />
<img class="product product2" src="product2.png" />
<img class="product product3" src="product3.png" />
<img class="stick" src="stick.png" />
<img class="cta tapesh" src="cta.png" />
<img class="star star1" src="star.png" />
```

### CSS Initial States
```css
.intro { position: fixed; right: -650px; bottom: 0; height: 120px; z-index: 99999; }
.bg { position: fixed; right: 0; bottom: 0; width: 70%; height: 120px; z-index: -100; transform: scaleY(0); transform-origin: bottom center; }
.logo { position: fixed; right: calc(35% - 65px); top: -80px; width: 120px; z-index: 5; }
.overline { position: fixed; right: 8%; bottom: 45px; height: 20px; z-index: 3; opacity: 0; }
.percent { position: fixed; left: 28%; top: -100px; height: 80px; z-index: 5; }
.product { position: fixed; left: 35%; bottom: 0; height: 80px; z-index: 2; opacity: 0; }
.stick { position: fixed; left: 50px; bottom: 10px; width: 120px; z-index: 10; opacity: 0; transform-origin: bottom center; }
.cta { position: fixed; right: calc(35% + 45px); bottom: -50px; height: 28px; z-index: 99; }
.star1 { position: fixed; right: 15%; top: 10px; width: 20px; z-index: 9999; opacity: 0; }
```

### Script (3-Act Timeline)
```javascript
document.addEventListener('DOMContentLoaded', () => {
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE01);

  const intro = document.querySelector('.intro');
  const bg = document.querySelector('.bg');
  const logo = document.querySelector('.logo');
  const overline = document.querySelector('.overline');
  const percent = document.querySelector('.percent');
  const products = document.querySelectorAll('.product');
  const stick = document.querySelector('.stick');
  const cta = document.querySelector('.cta');
  const star1 = document.querySelector('.star1');

  // ACT 1: Intro crosses screen (0–8s)
  gsap.to(intro, {
    right: '105%',
    duration: 8,
    ease: 'linear',
    onComplete: startAct2
  });

  // ACT 2: Background reveals, brand elements appear (8–14s)
  function startAct2() {
    fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE02);

    const tl = gsap.timeline();
    tl.to(bg, { scaleY: 1, duration: 0.8, ease: 'power2.out' })
      .to(logo, { top: '10px', duration: 0.6, ease: 'back.out(1.5)' }, '-=0.3')
      .to(overline, { opacity: 1, duration: 0.5 }, '-=0.2')
      .to(percent, { top: '28px', duration: 0.8, ease: 'back.out(1.9)' }, '-=0.3')
      .to(star1, { opacity: 1, duration: 0.3 })
      .call(() => setTimeout(startAct3, 2000));
  }

  // ACT 3: Products cycle, CTA pulses (14–60s)
  function startAct3() {
    fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE03);

    // Show stick
    gsap.to(stick, { opacity: 1, duration: 0.5 });

    // Reveal CTA
    gsap.to(cta, { bottom: '12px', duration: 0.7, ease: 'back.out(1.5)' });

    // Start product carousel
    let idx = 0;
    function cycleProduct() {
      stick.classList.remove('hammer');
      void stick.offsetWidth;
      stick.classList.add('hammer');

      products.forEach(p => gsap.to(p, { opacity: 0, bottom: '0px', duration: 0.8 }));
      gsap.to(products[idx], { opacity: 1, bottom: '72px', duration: 0.8 });

      if (idx === 0) fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE03);
      if (idx === 1) fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE04);
      if (idx === 2) fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE05);

      idx = (idx + 1) % products.length;
    }

    cycleProduct();
    setInterval(cycleProduct, 5000);
  }

  // Auto-reload at 60s
  setTimeout(() => {
    fire_tag(ALL_EVENT_TYPES.LOOP);
    location.reload();
  }, 60000);
});
```

---

## Pattern 2: Minimal Fade-In

**Use when:** Elegant brand, text-heavy, no intro element needed.

### Script
```javascript
document.addEventListener('DOMContentLoaded', () => {
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE01);

  gsap.set(['.logo', '.overline', '.cta', '.product'], { opacity: 0 });

  const tl = gsap.timeline();
  tl.to('.bg', { opacity: 1, duration: 1 })
    .to('.logo', { opacity: 1, x: 0, duration: 0.7, ease: 'power2.out' }, '-=0.3')
    .to('.overline', { opacity: 1, duration: 0.5 }, '-=0.2')
    .to('.product', { opacity: 1, bottom: '72px', duration: 0.8, stagger: 0.15 }, '-=0.2')
    .to('.cta', { opacity: 1, bottom: '12px', duration: 0.7, ease: 'back.out(1.5)' }, '-=0.3')
    .call(() => fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE02));

  setTimeout(() => {
    fire_tag(ALL_EVENT_TYPES.LOOP);
    location.reload();
  }, 60000);
});
```

---

## Pattern 3: Fortune Wheel

**Use when:** Promotional campaign, lucky draw, gamification.

### HTML Additions
```html
<div class="wheel-container">
  <div class="spinner"></div>
  <div class="arrow"></div>
  <div class="led-ring">
    <!-- 16 LEDs positioned in a circle -->
    <div class="led" style="transform: rotate(0deg) translateY(-55px);"></div>
    <div class="led" style="transform: rotate(22.5deg) translateY(-55px);"></div>
    <!-- ... repeat to 337.5deg -->
  </div>
</div>
```

### CSS
```css
.wheel-container { position: fixed; right: -150px; bottom: -30px; width: 150px; height: 150px; z-index: 100; }
.spinner { width: 100%; height: 100%; border-radius: 50%; background: conic-gradient(#ff0 0deg, #f00 45deg, #0f0 90deg, #00f 135deg, #ff0 180deg, #f00 225deg, #0f0 270deg, #00f 315deg, #ff0 360deg); }
.arrow { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-top: 20px solid red; z-index: 101; }
.led { position: absolute; width: 8px; height: 8px; border-radius: 50%; background: yellow; top: 50%; left: 50%; transform-origin: center; }
```

### Script
```javascript
document.addEventListener('DOMContentLoaded', () => {
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE01);

  const wheel = document.querySelector('.wheel-container');
  const spinner = document.querySelector('.spinner');
  const leds = document.querySelectorAll('.led');

  // LED flash animation
  let ledState = false;
  setInterval(() => {
    leds.forEach((led, i) => {
      led.style.background = (i % 2 === (ledState ? 0 : 1)) ? 'yellow' : 'transparent';
    });
    ledState = !ledState;
  }, 500);

  // Wheel enters from bottom-right
  gsap.to(wheel, { right: '30%', bottom: '0px', duration: 1, ease: 'back.out(1.7)' });

  // Fast spin phase
  setTimeout(() => {
    fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE02);
    gsap.to(spinner, { rotation: '+=3600', duration: 0.4, repeat: -1, ease: 'none' });
  }, 2000);

  // Slow dramatic stop
  setTimeout(() => {
    gsap.killTweensOf(spinner);
    gsap.to(spinner, {
      rotation: '+=720',
      duration: 2,
      ease: 'power3.out',
      onComplete: () => {
        fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE03);
        // Reveal prize / CTA
        gsap.to('.cta', { opacity: 1, bottom: '12px', duration: 0.7, ease: 'back.out(1.5)' });
      }
    });
  }, 12000);

  setTimeout(() => { fire_tag(ALL_EVENT_TYPES.LOOP); location.reload(); }, 60000);
});
```

---

## Pattern 4: Scroll Reactive

**Use when:** Products swap based on page scroll position.

### Script
```javascript
document.addEventListener('DOMContentLoaded', () => {
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE01);

  const products = document.querySelectorAll('.product');
  let currentIdx = 0;

  // Listen for scroll messages from parent page
  window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'yn-window-scroll') {
      const scrollPercent = event.data.percent || 0;
      const newIdx = Math.min(
        Math.floor(scrollPercent / (100 / products.length)),
        products.length - 1
      );

      if (newIdx !== currentIdx) {
        gsap.to(products[currentIdx], { opacity: 0, duration: 0.5 });
        gsap.to(products[newIdx], { opacity: 1, bottom: '72px', duration: 0.5 });
        currentIdx = newIdx;
      }
    }
  });

  // Show first product
  gsap.to(products[0], { opacity: 1, bottom: '72px', duration: 0.8 });

  setTimeout(() => { fire_tag(ALL_EVENT_TYPES.LOOP); location.reload(); }, 60000);
});
```

---

## Pattern 5: Countdown Timer

**Use when:** Sale deadline, event launch, limited-time offer.

### HTML
```html
<div class="countdown">
  <div class="countdown-item"><span class="days">۰۰</span><small>روز</small></div>
  <div class="countdown-item"><span class="hours">۰۰</span><small>ساعت</small></div>
  <div class="countdown-item"><span class="minutes">۰۰</span><small>دقیقه</small></div>
  <div class="countdown-item"><span class="seconds">۰۰</span><small>ثانیه</small></div>
</div>
```

### CSS
```css
.countdown { position: fixed; left: 10%; bottom: 40px; display: flex; gap: 8px; z-index: 5; direction: ltr; }
.countdown-item { text-align: center; background: rgba(0,0,0,0.7); border-radius: 6px; padding: 4px 8px; color: white; }
.countdown-item span { font-size: 22px; font-weight: 900; display: block; }
.countdown-item small { font-size: 9px; opacity: 0.7; }
```

### Script
```javascript
const TARGET_DATE = new Date('2026-04-01T00:00:00+03:30'); // adjust per campaign

function toPersian(n) {
  return Number(n).toLocaleString('fa-IR', { useGrouping: false });
}

function padPersian(n) {
  return toPersian(String(n).padStart(2, '0'));
}

function updateCountdown() {
  const now = new Date();
  const diff = TARGET_DATE - now;

  if (diff <= 0) {
    document.querySelector('.countdown').style.display = 'none';
    return;
  }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const minutes = Math.floor((diff / (1000 * 60)) % 60);
  const seconds = Math.floor((diff / 1000) % 60);

  document.querySelector('.days').textContent = padPersian(days);
  document.querySelector('.hours').textContent = padPersian(hours);
  document.querySelector('.minutes').textContent = padPersian(minutes);
  document.querySelector('.seconds').textContent = padPersian(seconds);
}

updateCountdown();
setInterval(updateCountdown, 1000);
```

---

## Pattern 6: Video Background

**Use when:** Cinematic, premium brand, video-first creative.

### HTML
```html
<video class="bg-video" autoplay muted loop playsinline>
  <source src="bg.mp4" type="video/mp4" />
</video>
<div class="glass"></div>
<div class="curtain curtain-left"></div>
<div class="curtain curtain-right"></div>
<button class="unmute">🔊</button>
```

### CSS
```css
.bg-video { position: fixed; left: 0; bottom: 0; width: 60%; height: 150px; object-fit: cover; z-index: -999999; }
.glass { position: fixed; left: 0; bottom: 0; width: 60%; height: 150px; background: rgba(0,0,0,0.3); z-index: -200; }
.curtain { position: fixed; bottom: 0; width: 50%; height: 150px; z-index: 99999; }
.curtain-left { left: 0; background: #000; }
.curtain-right { right: 0; background: #000; }
.unmute { position: fixed; left: 5px; top: 5px; z-index: 99999999; background: rgba(0,0,0,0.6); color: white; border: none; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; font-size: 14px; }
```

### Script
```javascript
document.addEventListener('DOMContentLoaded', () => {
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE01);

  const video = document.querySelector('.bg-video');
  const unmute = document.querySelector('.unmute');

  // Curtain reveal
  gsap.to('.curtain-left', { x: '-100%', duration: 1, ease: 'power2.inOut', delay: 0.5 });
  gsap.to('.curtain-right', { x: '100%', duration: 1, ease: 'power2.inOut', delay: 0.5,
    onComplete: () => fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE02)
  });

  // Unmute toggle
  unmute.addEventListener('click', (e) => {
    e.stopPropagation();
    fire_tag(ALL_EVENT_TYPES.CLICK_AUTOPLAY);
    video.muted = !video.muted;
    unmute.textContent = video.muted ? '🔊' : '🔇';
  });

  setTimeout(() => { fire_tag(ALL_EVENT_TYPES.LOOP); location.reload(); }, 60000);
});
```

---

## Pattern 7: Live Data / Price Chart

**Use when:** Gold price, crypto, stock, or any real-time data.

### HTML
```html
<div class="chart-section">
  <div class="segmented-control">
    <input type="radio" name="period" id="today" checked /><label for="today">امروز</label>
    <input type="radio" name="period" id="week" /><label for="week">هفته</label>
    <input type="radio" name="period" id="month" /><label for="month">ماه</label>
  </div>
  <div class="price-display">
    <span class="live-dot"></span>
    <span class="price-value"></span>
  </div>
  <canvas id="priceChart"></canvas>
</div>
```

### Script
```javascript
const API_BASE = 'https://material.uranus-agency.ir/api';
const SYMBOL = 'gold_taline'; // change per campaign
let chartInstance = null;

async function fetchData(period) {
  const endpoint = period === 'today'
    ? `${API_BASE}/current-day/${SYMBOL}`
    : period === 'week'
    ? `${API_BASE}/average/7days/${SYMBOL}`
    : `${API_BASE}/average/30days/${SYMBOL}`;

  const res = await fetch(endpoint);
  return await res.json();
}

function renderChart(labels, data, color) {
  const ctx = document.getElementById('priceChart').getContext('2d');
  if (chartInstance) chartInstance.destroy();

  const gradient = ctx.createLinearGradient(0, 0, 0, 100);
  gradient.addColorStop(0, color + 'AA');
  gradient.addColorStop(1, color + '00');

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data,
        borderColor: color,
        backgroundColor: gradient,
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { mode: 'index' } },
      scales: { x: { display: false }, y: { display: false } },
      animation: { duration: 500 }
    }
  });
}

async function loadAndRender(period) {
  const data = await fetchData(period);
  const labels = data.map(d => d.hour || d.date);
  const values = data.map(d => d.price);
  const currentPrice = values[values.length - 1];

  const priceEl = document.querySelector('.price-value');
  gsap.to(priceEl, {
    opacity: 0, duration: 0.3,
    onComplete: () => {
      priceEl.textContent = Number(Math.round(currentPrice)).toLocaleString('fa-IR') + ' تومان';
      gsap.to(priceEl, { opacity: 1, duration: 0.3 });
    }
  });

  renderChart(labels, values, '#F59E0B');
}

// Period switchers with stopPropagation
['today', 'week', 'month'].forEach(id => {
  const el = document.getElementById(id);
  el.addEventListener('click', (e) => e.stopPropagation());
  el.addEventListener('change', () => loadAndRender(id));
});

loadAndRender('today');
setInterval(() => loadAndRender('today'), 60000);
```

---

## Pattern 8: Interactive Calculator / Slider

**Use when:** Loan calculator, savings estimator, insurance quote.

### HTML
```html
<div class="calc-section">
  <label class="calc-label">مبلغ وام</label>
  <input type="range" class="slider" min="0" max="5000000000" step="10000000" value="1000000000" />
  <div class="calc-output">
    <span class="calc-value"></span>
    <small>تومان</small>
  </div>
</div>
```

### Script
```javascript
const slider = document.querySelector('.slider');
const output = document.querySelector('.calc-value');

// Prevent slider drag from triggering page redirect
slider.addEventListener('click', (e) => e.stopPropagation());
slider.addEventListener('mousedown', (e) => e.stopPropagation());
slider.addEventListener('touchstart', (e) => e.stopPropagation());

function updateCalc() {
  const val = parseInt(slider.value);
  const result = val * 10; // example: loan amount x10
  output.textContent = Number(result).toLocaleString('fa-IR');
}

slider.addEventListener('input', updateCalc);
updateCalc();
```

---

## Pattern 9: Two-Slide Transition

**Use when:** Intro slide with interaction → main offer slide.

### Script
```javascript
function goToSlide2() {
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE02);
  gsap.to('.slide1', { x: '-100%', opacity: 0, duration: 1, ease: 'power2.inOut' });
  gsap.fromTo('.slide2',
    { x: '-100%' },
    { x: '0%', duration: 1, ease: 'power2.inOut' }
  );
}

// Trigger after interaction or timeout
setTimeout(goToSlide2, 9000);
```

---

## Pattern 10: Curtain Reveal

**Use when:** Dramatic brand reveal, luxury, suspense.

### CSS
```css
.curtain-left { position: fixed; left: 0; top: 0; width: 50%; height: 150px; background: var(--primary); z-index: 99999; }
.curtain-right { position: fixed; right: 0; top: 0; width: 50%; height: 150px; background: var(--primary); z-index: 99999; }
```

### Script
```javascript
setTimeout(() => {
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE02);
  gsap.to('.curtain-left', { x: '-100%', duration: 1.2, ease: 'power2.inOut' });
  gsap.to('.curtain-right', { x: '100%', duration: 1.2, ease: 'power2.inOut' });
}, 2000);
```

---

## Pattern 11: Video-as-Content with GIF Overlay

**Use when:** The video contains baked-in campaign text/copy, and you have a transparent GIF/character to complement it. The video IS the messaging — no text overlays needed.

**Layout:** Video right 60-70% (with rounded corners), transparent GIF left 30%, logo centered above video panel, CTA centered below.

### HTML
```html
<div class="rightContainer">
  <div class="cta" id="cta"
    style="font-size:0.8rem; color:#000; background:rgb(78,240,157); border:1.5px solid #000;">
    خــــریـــد
  </div>
</div>

<div class="logo" id="logoContainer" style="background:white; z-index:1;">
  <img id="logoImage" src="logo.png" />
</div>

<img id="product" class="product" src="character.gif" />

<div class="background" id="background"></div>

<div class="videoContainer" style="z-index:2;">
  <div style="position:relative; width:100%; height:100%;">
    <video id="videoBG" autoplay muted loop class="videoBG">
      <source id="videoSRC" src="video.mp4" type="video/mp4" />
    </video>
  </div>
</div>

<div class="glass" id="glass" style="opacity:0; background:white;"></div>
```

### CSS
```css
* {
  margin: 0; padding: 0; box-sizing: border-box;
  --radius: 10px;
  --side-margin: 5px;
  font-family: 'iranyekanx', sans-serif;
}

@font-face {
  font-family: 'iranyekanx';
  src: url('https://tasvir.yektanet.com/media/iframes/DCn/19WQ/24Qj/IRANYEKANX-MEDIUM.woff2') format('woff');
}

body, html { width: 100%; height: 100%; overflow: hidden; }

.videoContainer {
  position: fixed;
  right: var(--side-margin);
  height: 110px;
  bottom: 0;
  width: calc(70% - var(--side-margin));
  overflow: hidden;
  border-top-left-radius: var(--radius);
  border-top-right-radius: var(--radius);
}

.videoBG {
  position: absolute;
  bottom: -112px; /* starts off-screen */
  height: 132.5px;
  width: 100%;
  object-fit: cover;
  object-position: top;
  z-index: -200;
  border-top-left-radius: var(--radius);
  border-top-right-radius: var(--radius);
  border: 2px solid orange; /* brand accent */
  right: 0;
}

.glass {
  position: fixed;
  right: calc(var(--side-margin) + 1.5px);
  bottom: -112px;
  width: calc(70% - var(--side-margin) - 4px);
  height: 110.5px;
  border-top-left-radius: calc(var(--radius) - 2.5px);
  border-top-right-radius: calc(var(--radius) - 2.5px);
  z-index: -100;
  opacity: 0.3;
}

.logo {
  z-index: 5;
  max-width: 100px;
  min-width: 70px;
  position: fixed;
  right: calc(35% + var(--side-margin) / 2);
  top: 50px; /* starts off-screen, GSAP moves to top:0 */
  opacity: 0;
  transform: translateX(50%);
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top-left-radius: var(--radius);
  border-top-right-radius: var(--radius);
  padding: 4px;
  border: 2px solid orange; /* brand accent */
}

.logo img { height: 100%; width: 100%; scale: 1.35; object-fit: contain; }

.rightContainer {
  position: fixed;
  transform: translateX(50%);
  right: calc(35% + var(--side-margin) / 2);
  width: calc(70% - var(--side-margin));
  height: 108px;
  z-index: 9999;
  bottom: -8px;
  padding-block: 12.5px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
}

.cta {
  direction: rtl;
  padding: 2px 2vw;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  font-weight: 900;
  font-size: 0.6rem;
  border-radius: 999999px;
  min-width: 16vw;
  animation: tapesh 1s infinite linear;
}

@keyframes tapesh { 0%,100%{scale:1;} 50%{scale:1.2;} }

.product {
  position: fixed;
  left: calc(var(--side-margin) + 20px);
  height: 150px;
  z-index: 999999;
  top: -150px; /* starts off-screen */
  object-fit: contain;
  scale: 2.5;
  width: calc(30% - var(--side-margin) - 5px);
}
```

### Script
```javascript
const logo = document.querySelector('.logo');
const products = document.querySelectorAll('.product');
const cta = document.querySelector('.cta');
const bgs = document.querySelectorAll('.videoBG');

// Video slides up from bottom
bgs.forEach(bg => {
  bg.muted = true;
  bg.play();
  gsap.to(bg, { bottom: '0', duration: 1 });
});

gsap.to('.glass', { bottom: '0', duration: 1 });

// Logo fades in and drops to position
gsap.to(logo, {
  top: 0, delay: 1, duration: 1, opacity: 1,
  onComplete: () => {
    // GIF drops from top
    gsap.to(products[0], { top: '15px', duration: 1 });

    // CTA appears
    gsap.to(cta, { opacity: 1, duration: 1, delay: 0.5 });
  }
});

// Click tracking
logo.addEventListener('click', () => fire_tag(ALL_EVENT_TYPES.CLICK1));
cta.addEventListener('click', () => fire_tag(ALL_EVENT_TYPES.CLICK2));
products.forEach(p => p.addEventListener('click', () => fire_tag(ALL_EVENT_TYPES.CLICK3)));

// Reload
setTimeout(() => { fire_tag(ALL_EVENT_TYPES.LOOP); location.reload(); }, 30000);
```

---

## Pattern 12: Multi-Video Sequential Story

**Use when:** Campaign story told across 2-3 short video clips, with CTA overlay between clips.

### Script
```javascript
const video1 = document.querySelector('.video1');
const video2 = document.querySelector('.video2');
const video3 = document.querySelector('.video3');
const cta = document.querySelector('.custom-button');

let userClicked = false;

// Preload all videos
[video2, video3].forEach(v => { v.preload = 'auto'; v.currentTime = 0; });

// Video 1 → Video 2
video1.addEventListener('ended', () => {
  gsap.to(video1, { scale: 1.1, opacity: 0, duration: 0.6, ease: 'power2.in' });
  gsap.fromTo(video2, { scale: 1.1, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.6, ease: 'power2.out' });
  video2.currentTime = 0;
  video2.play();
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE02);
});

// Pause video2 at specific time, show CTA
video2.addEventListener('timeupdate', function() {
  if (this.currentTime >= 1.2 && !userClicked) {
    this.pause();
    gsap.to(cta, { opacity: 1, visibility: 'visible', duration: 0.6 });
    gsap.to(cta, { animation: 'pulse 0.8s ease-in-out infinite', duration: 0.1 });

    // Auto-continue after 10s if no click
    setTimeout(() => {
      if (!userClicked) playVideo3();
      gsap.set(cta, { display: 'none' });
    }, 10000);
  }
});

// CTA button interaction
cta.addEventListener('click', (e) => {
  e.preventDefault();
  e.stopPropagation();
  fire_tag(ALL_EVENT_TYPES.CLICK1);
  userClicked = true;
  // Play sound effect
  new Audio('./voice.mp3').play().catch(() => {});
  gsap.to(cta, { scale: 2, duration: 0.3 });
  playVideo3();
});

function playVideo3() {
  gsap.to(video2, { opacity: 0, duration: 2, ease: 'power2.inOut' });
  gsap.to(video3, { opacity: 1, duration: 2, ease: 'power2.inOut' });
  video3.currentTime = 0;
  video3.play();
  fire_tag(ALL_EVENT_TYPES.VISIT_SLIDE03);
}

video3.addEventListener('ended', () => location.reload());
```

---

## Pattern 13: GIF Intro with Slide Transition

**Use when:** Animated GIF serves as intro (character walks in, logo plays), then shrinks/moves aside as main content appears.

### Script
```javascript
const man = document.querySelector('.man');
const cloud = document.querySelector('.cloud');
const bg = document.querySelector('.bg');
const logo = document.querySelector('.logo');
const overline = document.querySelector('.overline');
const cta = document.querySelector('.cta');

// Phase 1: GIF character enters (0-7s)
man.style.opacity = 1;
gsap.to(man, { left: '-15%', duration: 1.5 });
gsap.to(cloud, { scale: 1, duration: 0.5, delay: 1 });

// Phase 2: Transition to main offer (7s)
setTimeout(() => {
  gsap.to(man, { opacity: 0, duration: 1 });
  gsap.to(cloud, { opacity: 0, duration: 1 });
  goToSlide2();
}, 7000);

function goToSlide2() {
  // New character appears left
  gsap.to('.man2', { left: '10px', duration: 1 });

  // Background panel slides in from right
  gsap.to(bg, { right: '5px', duration: 1, onComplete: () => {
    gsap.to(overline, { opacity: 1, duration: 1 });
    gsap.to(cta, { opacity: 1, duration: 1 });
  }});

  // Logo drops to position
  gsap.to(logo, { top: '0px', duration: 1 });
}

setTimeout(() => { fire_tag(ALL_EVENT_TYPES.LOOP); location.reload(); }, 30000);
```

---

## Pattern 14: Spotlight / Focus-Zoom Loop

**Use when:** Live data billboard that periodically zooms into the key number (price, percentage) then returns to full layout. Creates engagement without user interaction.

### Script
```javascript
function initIntroAnimation() {
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

  tl.fromTo('.bg', { opacity: 0, yPercent: 40, scaleX: 0.2 }, { duration: 1.2, opacity: 1, yPercent: -50, scaleX: 1 })
    .from('.logo', { opacity: 0, y: 45, scale: 0.85, rotation: -6, duration: 0.55, ease: 'back.out(1.6)' })
    .from('.overline', { opacity: 0, y: 40, scale: 0.88, rotation: 6, duration: 0.5, ease: 'back.out(1.5)' })
    .from('.heroPrice', { opacity: 0, y: 35, scale: 1.5, rotation: -5, duration: 0.65, ease: 'back.out(1.8)' })
    .from('.cta', { opacity: 0, y: 30, scale: 0.85, duration: 0.55, ease: 'back.out(1.6)' }, '+=0.8');

  tl.eventCallback('onComplete', () => gsap.delayedCall(10, spotlightSequence));
}

function spotlightSequence() {
  const tl = gsap.timeline();

  // Fade out supporting elements
  tl.to(['.bg', '.logo', '.overline', '.growth'], {
    opacity: 0, y: 30, duration: 0.45, ease: 'power2.in', stagger: 0.03
  }, '-=0.15');

  // Zoom hero price to center
  tl.to('.heroPrice', {
    opacity: 1, scale: 1, xPercent: -30, yPercent: -5,
    duration: 1, ease: 'power3.out'
  }, '-=0.6');

  // Move CTA to follow
  tl.to('.cta', { xPercent: -80, yPercent: -20, duration: 1, ease: 'power3.out' }, '<');

  // Hold 5s, then return everything
  tl.to('.heroPrice', {
    scale: 1, xPercent: 0, yPercent: 0, duration: 1, ease: 'power3.inOut', delay: 5,
    onComplete: () => {
      gsap.set('.heroPrice', { clearProps: 'transform,top,left,position' });
      gsap.set('.cta', { clearProps: 'transform' });
      gsap.to(['.bg', '.logo', '.overline', '.growth', '.cta'], {
        opacity: 1, y: 0, duration: 0.8, ease: 'power2.out', stagger: 0.05
      });
      gsap.delayedCall(10, spotlightSequence); // loop forever
    }
  });

  tl.to('.cta', { xPercent: 0, yPercent: 0, duration: 1, ease: 'power3.inOut' }, '<');
}
```

---

## Pattern 15: Fortune Wheel (Full Production from MelliGold)

**Use when:** Lucky draw, gamification, promotional wheel with LED lights.

### Key Implementation Details

**LED Ring (16 lights distributed in circle):**
```javascript
const lightContainers = document.querySelectorAll('.light-container');
lightContainers.forEach((lc, i) => {
  lc.style.transform = `translate(-50%, -50%) rotate(${(i * 360) / lightContainers.length}deg)`;
});

// Alternating flash with glow
function animateLights() {
  let isOddOn = true;
  function toggle() {
    const [onSet, offSet] = isOddOn ? [oddLights, evenLights] : [evenLights, oddLights];
    onSet.forEach(l => { l.style.opacity = '1'; l.style.filter = 'brightness(1.5) drop-shadow(0 0 10px rgba(255,255,0,0.8))'; });
    offSet.forEach(l => { l.style.opacity = '0.3'; l.style.filter = 'brightness(0.5)'; });
    isOddOn = !isOddOn;
    setTimeout(toggle, 500);
  }
  toggle();
}
```

**Spinner with blur during fast spin:**
```javascript
gsap.fromTo(spinnerInside, { rotate: 0, filter: 'blur(1px)' }, { rotate: 360, filter: 'blur(1px)', duration: 0.5, ease: 'linear', repeat: -1 });
```

**Dramatic slow stop with random position:**
```javascript
spinnerAnimation.kill();
const currentRotation = parseFloat(spinnerInside.style.transform.match(/rotate\(([^)]+)deg\)/)?.[1] || 0);
gsap.to(spinnerInside, {
  rotate: currentRotation + 360 + Math.random() * 360,
  filter: 'blur(0px)',
  ease: 'ease-in',
  duration: 2,
  onComplete: () => { /* reveal prize, reload */ }
});
```

**Full sequence:** Spinner drops from top → bg scales in → wheel moves left → header drops → CTA appears with tapesh → spinner fast-spins 10s → elements fade out + removed → spinner re-centers → slow dramatic stop → exits upward → reload

---

## Universal Utilities

### Persian Number Conversion
```javascript
function toPersian(n) {
  return Number(n).toLocaleString('fa-IR');
}
```

### Product Carousel (Simple Opacity Swap)
```javascript
const products = document.querySelectorAll('.product');
let idx = 0;
function cycleProducts() {
  products.forEach(p => gsap.to(p, { opacity: 0, bottom: '0px', duration: 0.8 }));
  gsap.to(products[idx], { opacity: 1, bottom: '72px', duration: 0.8 });
  idx = (idx + 1) % products.length;
}
cycleProducts();
setInterval(cycleProducts, 5000);
```

### Class Reflow Trick (Restart CSS Animation)
```javascript
element.classList.remove('animation-class');
void element.offsetWidth; // force browser reflow
element.classList.add('animation-class');
```

### Infinite DOM Carousel (No Memory Leak)
```javascript
gsap.to(wrapper, {
  x: `-=${itemWidth}px`,
  duration: 0.8,
  ease: 'power2.out',
  onComplete: () => {
    wrapper.appendChild(wrapper.firstElementChild);
    gsap.set(wrapper, { x: 0 });
  }
});
```

### Flying Clone Animation
```javascript
function flyTo(sourceEl, destEl, container) {
  const clone = sourceEl.cloneNode(true);
  const srcRect = sourceEl.getBoundingClientRect();
  const destRect = destEl.getBoundingClientRect();

  clone.style.position = 'absolute';
  clone.style.top = srcRect.top + 'px';
  clone.style.left = srcRect.left + 'px';
  clone.style.width = srcRect.width + 'px';
  clone.style.zIndex = '10000';
  container.appendChild(clone);

  gsap.to(clone, {
    top: destRect.top + 'px',
    left: destRect.left + 'px',
    scale: 0.4,
    rotation: 25,
    duration: 0.4,
    ease: 'power2.inOut',
    onComplete: () => clone.remove()
  });
}
```

### Sound Effect on Interaction
```javascript
const sfx = new Audio('sound.mp3');
sfx.volume = 0.5;
element.addEventListener('click', (e) => {
  e.stopPropagation();
  sfx.play().catch(() => {}); // ignore autoplay block
});
```

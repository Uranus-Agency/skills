# BB Creation: Azki Race — Key Learnings

## 1. Position Map Extraction (Python PIL) ⭐
**بهترین روش برای positioning دقیق asset هایی که محل دقیقشون مهمه (مثل چرخ روی بدنه ماشین)**

قبل از نوشتن هر CSS، با PIL یه position map از عکس می‌گیریم:
```python
from PIL import Image
import numpy as np

img = Image.open("Carnowheel.png").convert("RGBA")
data = np.array(img)
# پیدا کردن dark pixels (چرخ‌ها) در نصف پایین عکس
h, w = data.shape[:2]
bottom_half = data[h//2:, :, :]
dark_mask = (bottom_half[:,:,0]<45) & (bottom_half[:,:,1]<45) & (bottom_half[:,:,2]<45) & (bottom_half[:,:,3]>200)
# connected components → مرکز هر cluster = مرکز چرخ
```
خروجی: مختصات دقیق pixel → تبدیل به % با `x/w*100` و `y/h*100`

**چرا مهمه:** بدون این، چرخ‌ها روی بدنه ماشین float می‌کنن. با این، اول اجرا دقیقاً سر جاشن.

---

## 2. offsetLeft به‌جای getBoundingClientRect برای centering
**هر بار که body یه `transform: scale()` داره، getBoundingClientRect مقادیر scaled برمی‌گردونه و محاسبات centering غلط میشه.**

```javascript
// ❌ اشتباه — تحت تأثیر body scale
function xToCenter(id) {
  var r = document.getElementById(id).getBoundingClientRect();
  return 200 - (r.left + r.width / 2);
}

// ✅ درست — موقعیت CSS طبیعی، scale-independent
function xToCenter(id) {
  var el = document.getElementById(id);
  return 200 - el.offsetLeft - el.offsetWidth / 2;
}

// برای left-align با یه target:
function xForLeft(id) {
  return targetLeft - document.getElementById(id).offsetLeft;
}
```

---

## 3. Responsive Scale (fitBB)
**برای بیلبوردهای production — طراحی 400px ثابت، scale متناسب با viewport:**

```javascript
(function () {
  function fitBB() {
    var vw = window.innerWidth || document.documentElement.clientWidth;
    document.body.style.width           = '400px';
    document.body.style.transform       = 'scale(' + vw / 400 + ')';
    document.body.style.transformOrigin = 'top left';
  }
  fitBB();
  window.addEventListener('resize', fitBB);
})();
```
CSS: `html, body { width: 100%; height: 150px; }`  
اضافه کردن این به index.html — بعد از script.js و قبل از click_url script.

---

## 4. Single-File Delivery (bg.html inline)
**Ad network‌ها فقط یک HTML می‌پذیرن. bg.html رو inline کن:**

- محتوای `<body>` از bg.html برو داخل `<div id="bg-canvas">`
- CSS های bg رو با prefix scoped بذار توی `<style>` در index.html (مثلاً `#bg-canvas .bg-orb`)
- `#bg-canvas iframe` رو از style.css حذف کن
- فایل bg.html رو حذف کن
- `../gsap.min.js` → `https://cdn.yektanet.com/assets/3rdparty/gsap@3.12.5/gsap.min.js`

---

## 5. BG Mask Flip برای Mirror Layout
**وقتی ماشین از چپ به راست میره، background هم باید flip بشه:**

```javascript
var MASK_RIGHT  = 'linear-gradient(to right, transparent 0%, transparent 30%, rgba(0,0,0,0.6) 52%, black 68%, black 100%)';
var MASK_CENTER = 'linear-gradient(to right, transparent 0%, black 18%, black 82%, transparent 100%)';
var MASK_LEFT   = 'linear-gradient(to right, black 0%, black 32%, rgba(0,0,0,0.6) 48%, transparent 70%, transparent 100%)';

function setMask(mask) {
  var el = document.getElementById('bg-canvas');
  el.style.maskImage = el.style.webkitMaskImage = mask;
}
```

---

## 6. text-bg Mirror Technique
**به‌جای یه المان جدید برای left-side gradient، همون text-bg رو flip کن:**

```javascript
// scaleX:-1 → گرادیان برعکس میشه (solid-left به‌جای solid-right)
// x:-200    → المان به نصف چپ بیلبورد میره
tl.to('#text-bg', { scaleX: -1, x: -200, opacity: 1, duration: 0.35 });

// در resetAll:
gsap.set('#text-bg', { scaleX: 1, x: 0, opacity: 1 });
```

---

## 7. Phase Kill باید داخل tl.call باشه
```javascript
// ❌ اشتباه — synchronous، موقع build اجرا میشه نه موقع phase
if (ctaPulse) { ctaPulse.kill(); ctaPulse = null; }

// ✅ درست — داخل tl.call اجرا میشه در زمان درست timeline
tl.call(function () {
  if (ctaPulse) { ctaPulse.kill(); ctaPulse = null; }
  if (carIdle)  { carIdle.kill();  carIdle  = null; }
});
```

---

## 8. Timeline Delivery Checklist
قبل از آپلود هر بیلبورد:
- [ ] `width: 100%` روی body (نه 400px)
- [ ] fitBB script اضافه شده
- [ ] GSAP از CDN یکتانت (نه relative path)
- [ ] bg.html inline شده، فایل bg.html حذف
- [ ] click_url script ته index.html
- [ ] فقط فایل‌های استفاده‌شده در پوشه

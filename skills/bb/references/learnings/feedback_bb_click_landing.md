---
name: BB click tracking and landing page rule
description: Never use stopPropagation on elements that should open the landing page — it kills event bubbling to the click_url handler
type: feedback
---

## Click & Landing Rule

The `click_url` landing page is opened by this code in `index.html`:
```js
document.addEventListener("click", function() { open(click_url); });
```

This depends on **event bubbling**. If any child element calls `e.stopPropagation()`, the event never reaches the document, and the landing page never opens.

**Rules:**
- ✅ Elements that SHOULD open landing: only `fire_tag()`, no `stopPropagation()`
- ❌ Elements that should NOT open landing: use `stopPropagation()`

**Correct pattern:**
```js
cta.addEventListener("click", function() { fire_tag(ALL_EVENT_TYPES.CLICK1); });
char.addEventListener("click", function() { fire_tag(ALL_EVENT_TYPES.CLICK2); });
```

**Wrong pattern (landing never opens):**
```js
cta.addEventListener("click", function(e) { e.stopPropagation(); fire_tag(ALL_EVENT_TYPES.CLICK1); });
```

In practice: CTA, character, products, and the whole billboard area should all open the landing. Use `stopPropagation` only on UI elements that should specifically NOT navigate (e.g., a mute button on a video, a close button).

**Source:** Coworker correction during Azki billboard review.

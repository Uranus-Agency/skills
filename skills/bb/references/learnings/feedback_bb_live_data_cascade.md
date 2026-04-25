---
name: BB — live data with multi-source API cascade + realistic fallbacks
description: For billboards that display live numbers (prices, rates, scores), wire a cascade of APIs with realistic fallbacks; never ship obviously-wrong placeholder numbers.
type: feedback
---

## Rule: cascade APIs and keep fallbacks realistic

When a billboard displays live data (crypto prices, exchange rates, live scores), do NOT hardcode fake numbers. Wire at least one live API, add a fallback API, and — this is the part that surprised me — **make the hardcoded fallback realistic for today's market**, because the user WILL notice if it's wrong.

**Why:** On the Nobitex signup BB, v1 shipped with hardcoded placeholders (BTC ۴.۱۲ میلیارد تومان, etc.) that were randomly made up. User's reaction was immediate and harsh: *"قیمتات رو از کجا درآوردی؟ همش غلطه ها!"* ("Where did you get these prices? They're all wrong!"). When I updated to realistic values but still without live API, user escalated: *"حاجی قیمتات چرا غلط غولوطه کماکان؟! خب از یه apiای بگیر دیگه"* ("why are your prices still wrong? just fetch them from an API"). Every wrong number erodes trust in the brand's billboard. Display real data, period.

## The cascade pattern

```js
async function tryNobitex() {
  const r = await fetch('https://api.nobitex.ir/market/stats?srcCurrency=btc,eth,usdt&dstCurrency=rls', { mode: 'cors' });
  if (!r.ok) throw new Error('nobitex ' + r.status);
  const d = await r.json();
  if (!d || !d.stats) throw new Error('no stats');
  // apply to COINS[] ...
  LIVE_SOURCE = 'nobitex';
}

async function tryCoinGecko() {
  const r = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether&vs_currencies=usd&include_24hr_change=true');
  if (!r.ok) throw new Error('coingecko ' + r.status);
  const d = await r.json();
  const rate = COINS[2].price;  // local USDT → Toman rate to convert USD prices
  // apply to COINS[] ...
  LIVE_SOURCE = 'coingecko';
}

async function refreshLivePrices() {
  try { await tryNobitex();   return; } catch (_) {}
  try { await tryCoinGecko(); return; } catch (_) {}
  // silently stay on fallback — UI still works
}
refreshLivePrices();
setInterval(refreshLivePrices, 12000);  // refresh every 12s
```

**Key patterns:**
- Each attempt is wrapped in try/catch and a throw on non-200 / missing fields
- The cascade short-circuits on first success
- Silent failure → fallback values keep rendering (no broken UI)
- Refresh every 10-15s — more frequent is wasteful, less frequent feels stale
- Store `LIVE_SOURCE` so you can badge the data if needed (or just debug)

## Realistic fallback rule

The hardcoded `COINS[]` (or equivalent) must contain values roughly accurate for **the month you ship in**. Not just "plausible order of magnitude" — actually current. Check the market before coding. You won't always have the API working in preview (see below), so the user's first view in preview will be the fallback values. Wrong fallback = "your billboard is broken" even when the production deployment would work fine.

For Iran-facing crypto (April 2026): BTC ~10B Toman, ETH ~340M Toman, USDT ~150K Toman. Update every major shipment.

## Preview sandbox can't reach external APIs

The Claude preview sandbox has no external DNS — `curl api.nobitex.ir` returns "Could not resolve host", and `fetch()` throws "Failed to fetch" immediately. This means:

- You cannot verify the live API works inside preview. Period.
- The fallback is what shows in every preview screenshot.
- In production (publisher page served from a real domain), the browser CAN reach the APIs (if CORS allows).
- **Do not waste time debugging fetch failures in preview.** Confirm the URL is correct, the CORS mode is set, the response parsing is sound — then trust it will work in production.

When demonstrating to the user, screenshot the preview (showing fallback) and separately describe the cascade logic. Don't claim "live data works" without production verification.

## CORS caveat

- Nobitex public stats API supports CORS from any origin. Safe to use.
- CoinGecko free tier has CORS enabled. Safe.
- Most other Iranian exchanges (Ramzinex, Wallex) do NOT enable CORS. Attempting `fetch()` will fail from browser — use a proxy or skip them.
- Always verify CORS before adding to cascade. A cascade where every layer fails CORS is no better than static fallback.

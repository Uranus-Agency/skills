---
name: autopro
description: >
  Generate professional Persian-language HTML advertising documents for Yektanet.
  ALWAYS use this skill for ANY of these requests (Persian or English):
  مدیاپلن, پروپوزال, media plan, proposal, تبلیغات محیطی,
  گزارش کمپین, campaign report, گزارش عملکرد, performance report,
  تحقیقات بازار, market research, survey report, گزارش نظرسنجی, دموگرافیک, demographic.
  Use this skill even if the user just says "یه مدیاپلن بساز" or "گزارش کمپین بساز" or "یه سروی بساز".
  Do NOT attempt to generate these HTML documents without first reading the reference file.
---

# autopro — Yektanet Document Generator

You generate three types of professional Persian HTML advertising documents for Yektanet.
Follow all 5 steps below every time — skipping any step leads to incorrect output.

---

## Step 1: Detect document type

| Keywords (Persian / English) | Type |
|---|---|
| مدیاپلن، پروپوزال، media plan، proposal | **Media Plan** |
| گزارش کمپین، campaign report، گزارش عملکرد | **Campaign Report** |
| تحقیقات بازار، survey، نظرسنجی، دموگرافیک، market research | **Survey Report** |

If unclear, ask the user in Persian which type they need.

---

## Step 2: Read the reference file

Read the relevant file from the `references/` folder inside this skill directory:

- Media Plan → `references/mediaplan.md`
- Campaign Report → `references/campaign_report.md`
- Survey Report → `references/survey_report.md`

**Follow the reference file precisely** — it contains required inputs, key rules, and the full step-by-step automation flow.

---

## Step 3: Read the base template

Read the HTML template from disk:

| Document type | Template path |
|---|---|
| Media Plan | `C:\Users\m.khorshidsavar\Desktop\Projects\proposall\AUTOMATION\MEDIAPLAN\BASE_TEMPLATE_1.html` |
| Campaign Report | `C:\Users\m.khorshidsavar\Desktop\Projects\proposall\AUTOMATION\CAMPAIGN_REPORT\BASE_TEMPLATE_1.html` |
| Survey Report | `C:\Users\m.khorshidsavar\Desktop\Projects\proposall\AUTOMATION\SURVEY_REPORT\BASE_TEMPLATE_1.html` |

If the user specifies a different template number (e.g. "BASE_TEMPLATE_2"), use that instead.
Never modify the template file itself — write output to a new file.

---

## Step 4: Collect required inputs

Ask the user for anything missing. Common inputs:

- **Brand name** (نام برند) — always required
- **Logo path** — look in `C:\Users\m.khorshidsavar\Desktop\Projects\proposall\brand logo\[BrandName]\`
- **Data tables** — paste as text or tab-separated

---

## Step 5: Generate and save

Follow the automation flow from the reference file exactly.

**Critical rules:**
- HTML must have `<html lang="fa" dir="rtl">`
- Remove ALL old/placeholder brand data from the template before inserting new data
- Save file as UTF-8 without BOM

**Output naming and location:**

| Document type | Filename | Save to |
|---|---|---|
| Media Plan | `proposal_[brandname].html` | `C:\Users\m.khorshidsavar\Desktop\Projects\proposall\mb output\` |
| Campaign Report | `[brandname]_campaign_report.html` | same |
| Survey Report | `[brandname]_market_research_report.html` | same |

Confirm the saved file path and size to the user in Persian.
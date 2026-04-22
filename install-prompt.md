# نصب BB Skill

## مرحله ۱ — مسیر پوشه رو کپی کن

روی پوشه `bb-skill-share` راست‌کلیک → **Copy as path**

---

## مرحله ۲ — Claude Code رو باز کن و این پرامپت رو بده

متن زیر رو کپی کن، **[PATH]** رو با مسیر پوشه عوض کن:

---

```
BB Skill رو از این مسیر نصب کن: [PATH]

مراحل نصب:
1. مسیر نصب رو پیدا کن:
   %USERPROFILE%\.claude\plugins\marketplaces\claude-plugins-official\plugins\bb\
   (اگه پوشه‌ها وجود ندارن بسازشون)

2. محتوای [PATH] رو به مسیر بالا کپی کن:
   - plugin.json
   - پوشه commands (با محتوا)
   - پوشه skills (با محتوا و همه زیرپوشه‌ها)

3. تأیید کن این سه فایل سر جاشن:
   - ...\plugins\bb\plugin.json
   - ...\plugins\bb\skills\bb\SKILL.md
   - ...\plugins\bb\skills\bb\references\learnings\MEMORY.md

4. بهم بگو "نصب تموم شد" — بعد Claude Code رو ببند و دوباره باز کن
```

---

## مرحله ۳ — تست نصب

بعد از ری‌استارت، تایپ کن:

```
/bb
```

✅ اگه BB پرسید "سناریو و اسست‌هات رو بده" — نصب موفقه

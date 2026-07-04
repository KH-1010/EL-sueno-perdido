# 🎮 مكتبة الألعاب العربية — Arabic PlayStation Games Library

موقع لمكتبة ألعاب PlayStation الكلاسيكية مع دعم الألعاب المدبلجة والمترجمة عربياً.

## ✨ المميزات

- 🎯 **PS1 / PS2 / PS3** — مكتبة شاملة
- 🎙 **DUB** — ألعاب مدبلجة عربياً
- 📝 **SUB** — ألعاب مترجمة عربياً
- 🖼 **12,000+ غلاف** من Libretro
- 🔄 **تحديث تلقائي** عبر GitHub Actions يومياً
- 🚀 **Cloudflare Workers** — سرعة فائقة بدون تجمد

## 🏗 البنية

```
files/
├── index.html          # الموقع الكامل (SPA)
├── build.js            # بناء worker.js للنشر
├── scraper.js          # مراقب archive.org التلقائي
├── wrangler.toml       # إعدادات Cloudflare Workers
├── .github/workflows/  # GitHub Actions (مراقبة + نشر)
├── ps1.json            # بيانات PS1
├── ps2.json            # بيانات PS2
├── ps3.json            # بيانات PS3
├── Dub.json            # الألعاب المدبلجة
├── Sub.json            # الألعاب المترجمة
├── libretro_ps1.json   # غلافات PS1
├── libretro_ps2.json   # غلافات PS2
└── libretro_ps3.json   # غلافات PS3
```

## 🚀 النشر

```bash
node build.js      # بناء worker.js
wrangler deploy    # نشر على Cloudflare
```

## 🤖 الأتمتة (GitHub Actions)

الـ workflow يعمل تلقائياً:
- كل يوم الساعة 3 صباحاً (UTC)
- عند رفع ملفات JSON جديدة
- يدوياً من صفحة Actions

### الـ Secrets المطلوبة:
| Secret | المصدر |
|---|---|
| `CF_API_TOKEN` | Cloudflare Dashboard → API Tokens |
| `CF_ACCOUNT_ID` | Cloudflare Dashboard → Account ID |

## 🌐 الموقع

https://ps-games-library.alshariefk.workers.dev

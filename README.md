# 🎮 مكتبة الألعاب العربية — Arabic PlayStation Games Library & PSN Database

موقع لمكتبة ألعاب PlayStation الكلاسيكية مع دعم الألعاب المدبلجة والمترجمة عربياً، مبني بهندسة الأداء الفائق وبدون أي تجمد (Zero Lag Architecture)، ويعمل مباشرة على **GitHub Pages** بدون الحاجة لأي خوادم أو Cloudflare!

## ✨ المميزات والهندسة البرمجية

- 🚀 **100% Static & GitHub Pages Ready** — لا يحتاج إلى Cloudflare Workers أو خوادم خلفية؛ يعمل مباشرة من المتصفح بسرعة فائقة.
- ⚡ **Zero Lag Engine** — معمارية التمرير الافتراضي (Virtual Scrolling & Pagination) المستوحاة من مشروع [PSN-Content](https://github.com/PS3-Pro/PSN-Content)، مع تحميل تدريجي بدون تجمد المتصفح حتى مع وجود أكثر من 60,000 لعبة!
- 🎙 **DUB** — قسم مخصص للألعاب المدبلجة عربياً.
- 📝 **SUB** — قسم مخصص للألعاب المترجمة عربياً.
- 🖼 **12,000+ غلاف** — ربط مباشر مع مكتبة Libretro الكلاسيكية.
- 🎮 **قاعدة بيانات PSN كاملة (60,000+ عنصر)** — تضم ألعاب وDLCs وثيمات وأفاتار وديمو وتحديثات لكل من PS3 وPS Vita وPSP وPSX وPSM.
- 🔄 **تحديث تلقائي للمكتبة (Automated Scraper)** — أتمتة كاملة عبر **GitHub Actions** تراقب مواقع الأرشيف وتضيف الألعاب الجديدة تلقائياً وبشكل يومي دون تدخل يدوي.

## 🏗 البنية ومحتويات المستودع

```
EL-sueno-perdido/
├── index.html              # الموقع الرئيسي — مكتبة الألعاب العربية
├── psn.html                # واجهة PSN Network Database (60K+ عنصر)
├── scraper.js              # مراقب archive.org التلقائي للألعاب العربية
├── update-nps.py           # سكربت تحديث قاعدة بيانات NoPayStation
├── .github/workflows/      # أتمتة GitHub Actions
├── ps1.json / ps2.json / ps3.json  # بيانات الألعاب
├── Dub.json / Sub.json     # قاعدة بيانات الألعاب المدبلجة والمترجمة
├── libretro_ps1/ps2/ps3.json       # غلافات Libretro
├── files/
│   └── website/
│       ├── modern.html     # واجهة PSN-Content الحديثة
│       └── classic.html    # واجهة PS3 المحمولة
├── resources/
│   ├── database/
│   │   ├── content/official/  # ملفات NPS TSV المجمّعة
│   │   ├── content/latest/    # آخر الألعاب حسب التاريخ
│   │   └── covers/            # غلافات الألعاب
│   └── interface/             # ملفات الواجهة والصوتيات
└── psn-data/                # بيانات NPS بتنسيق JSON و TSV
```

## 🎮 قسم PSN Network Database

النظام يضم قاعدة بيانات كاملة من [NoPayStation](https://nopaystation.com) تُحدّث يومياً تلقائياً:

| المنصة | ألعاب | DLCs | ثيمات | أفاتار | ديمو | تحديثات |
|--------|-------|------|-------|--------|------|---------|
| PS3 | 8,157 | 12,068 | 938 | 1,605 | 484 | — |
| PS Vita | 3,885 | 21,895 | 1,444 | — | 395 | 2,019 |
| PSP | 2,183 | 2,652 | 149 | — | 119 | 67 |
| PSX | 1,654 | — | — | — | — | — |
| PSM | 736 | — | — | — | — | — |
| **المجموع** | **16,615** | **36,615** | **2,531** | **1,605** | **998** | **2,086** |

## 🔄 الأتمتة عبر GitHub Actions

| Workflow | الوظيفة | الجدولة |
|----------|---------|---------|
| `pages.yml` | تحديث NPS + سكربت الأرشيف + نشر الموقع | يومياً الساعة 03:00 UTC |
| `deploy-site.yml` | نشر الموقع عند كل دفنة (push) | عند كل push لـ master/main |

### كيفية التشغيل يدوياً:
```bash
# تحديث قاعدة بيانات NPS
python update-nps.py

# تشغيل سكربت الأرشيف
node scraper.js
```

## 🌐 تفعيل ونشر الموقع عبر GitHub Pages

لتشغيل الموقع مباشرة على حسابك:
1. اذهب إلى إعدادات المستودع (Settings) ⟵ **Pages**.
2. تحت قسم **Build and deployment**، اختر **GitHub Actions** كمصدر (Source).
3. سيقوم الـ Workflow التلقائي ببناء ونشر الموقع فوراً على الرابط:
   **https://kh-1010.github.io/EL-sueno-perdido/**

---
*تمت الهندسة والتطوير بأعلى معايير الأداء والسرعة.*

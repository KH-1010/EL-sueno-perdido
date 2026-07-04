# 🎮 مكتبة الألعاب العربية — Arabic PlayStation Games Library

موقع لمكتبة ألعاب PlayStation الكلاسيكية مع دعم الألعاب المدبلجة والمترجمة عربياً، مبني بهندسة الأداء الفائق وبدون أي تجمد (Zero Lag Architecture)، ويعمل مباشرة على **GitHub Pages** بدون الحاجة لأي خوادم أو Cloudflare!

## ✨ المميزات والهندسة البرمجية

- 🚀 **100% Static & GitHub Pages Ready** — لا يحتاج إلى Cloudflare Workers أو خوادم خلفية؛ يعمل مباشرة من المتصفح بسرعة فائقة.
- ⚡ **Zero Lag Engine** — معمارية التمرير الافتراضي (Virtual Scrolling & Pagination) المستوحاة من مشروع [PSN-Content](https://github.com/PS3-Pro/PSN-Content)، مع تحميل تدريجي بدون تجمد المتصفح حتى مع وجود أكثر من 60,000 لعبة!
- 🎙 **DUB** — قسم مخصص للألعاب المدبلجة عربياً.
- 📝 **SUB** — قسم مخصص للألعاب المترجمة عربياً.
- 🖼 **12,000+ غلاف** — ربط مباشر مع مكتبة Libretro الكلاسيكية.
- 🔄 **تحديث تلقائي للمكتبة (Automated Scraper)** — أتمتة كاملة عبر **GitHub Actions** تراقب مواقع الأرشيف وتضيف الألعاب الجديدة تلقائياً وبشكل يومي دون تدخل يدوي.

## 🏗 البنية ومحتويات المستودع

```
EL-sueno-perdido/
├── index.html          # الموقع الكامل ومحرك العرض الفوري
├── scraper.js          # مراقب archive.org التلقائي للألعاب العربية
├── .github/workflows/  # أتمتة GitHub Actions (Scraper + GitHub Pages)
├── ps1.json            # بيانات PS1
├── ps2.json            # بيانات PS2
├── ps3.json            # بيانات PS3
├── Dub.json            # قاعدة بيانات الألعاب المدبلجة
├── Sub.json            # قاعدة بيانات الألعاب المترجمة
├── libretro_ps1.json   # غلافات PS1
├── libretro_ps2.json   # غلافات PS2
└── libretro_ps3.json   # غلافات PS3
```

## 🌐 تفعيل ونشر الموقع عبر GitHub Pages

لتشغيل الموقع مباشرة على حسابك:
1. اذهب إلى إعدادات المستودع (Settings) ⟵ **Pages**.
2. تحت قسم **Build and deployment**، اختر **GitHub Actions** كمصدر (Source).
3. سيقوم الـ Workflow التلقائي ببناء ونشر الموقع فوراً على الرابط:
   **https://kh-1010.github.io/EL-sueno-perdido/**

---
*تمت الهندسة والتطوير بأعلى معايير الأداء والسرعة.*

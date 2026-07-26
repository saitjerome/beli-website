# Belis Elektrik — Site Dokümantasyonu

Bu klasör, `Belis - Kopya` altındaki statik web sitesinin genel dokümantasyonunu içerir.

## Genel Bakış

- **Canlı adres:** https://www.beliselektrik.com.tr/
- **Tür:** Şablonsuz, saf HTML/CSS/JS statik site (build aracı, framework veya sunucu tarafı kod yok).
- **Sayfalar:** `index.html`, `hakkimizda.html`, `hizmetler.html`, `projeler.html`, `referanslar.html`, `iletisim.html`.
- **Varlıklar:** Tüm görseller, script'ler ve stil dosyaları `assets/` klasöründe.

## Kullanılan Teknolojiler

- **Tailwind CSS** — 5 sayfa (`index`, `hakkimizda`, `hizmetler`, `projeler`, `iletisim`) önceden derlenmiş `assets/tailwind.css` dosyasını kullanır. `referanslar.html` ise Tailwind'i CDN üzerinden (JIT derleyici) yükler — bu yüzden diğer sayfalarla birebir aynı yapıda değildir.
- **Google Fonts** — Inter (gövde metni) ve JetBrains Mono (etiketler), `media="print" onload="this.media='all'"` tekniğiyle render-bloklamadan asenkron yüklenir.
- **Material Symbols Outlined** — ikon fontu, aynı asenkron teknikle yüklenir.
- **OGL (`assets/circular-gallery.js`)** — index.html'deki dairesel proje galerisi için WebGL kütüphanesi, `cdn.jsdelivr.net` üzerinden ES modülü olarak içe aktarılır. IntersectionObserver ile yalnızca galeri görünüme yaklaşınca başlatılır.

## Önemli Yapısal Not: Şablon Sistemi Yok

Header, footer ve mobil menü gibi tekrarlanan bölümler **6 dosyada da elle senkron tutulan kopya markup**'tır (include/partial sistemi yoktur). Bir header/footer/mobil menü değişikliği yapılacaksa bu değişikliğin altı dosyaya da uygulanması gerekir. Bkz. [update-scripts.md](update-scripts.md) — bu tür toplu değişiklikleri script ile yapmanın örnekleri için.

## Klasör Yapısı

```
Belis - Kopya/
├── index.html          Ana sayfa (hero, vizyon kartları, dairesel galeri)
├── hakkimizda.html      Hakkımızda (vizyon/misyon/kalite/teknoloji kartları)
├── hizmetler.html        Hizmetler (masaüstü: 2 kolon liste+detay panel / mobil: kart ızgarası + bottom sheet)
├── projeler.html         Projeler (filtrelenebilir kart ızgarası + modal detay)
├── referanslar.html      Referanslar (müşteri logoları ızgarası)
├── iletisim.html         İletişim (form, adres, harita embed)
├── assets/
│   ├── tailwind.css       Önceden derlenmiş Tailwind (5 sayfa için)
│   ├── circular-gallery.js  WebGL proje galerisi (yalnızca index.html)
│   ├── banner_*.jpg        Sayfa üstü banner/hero görselleri
│   ├── proje_*.jpg         Proje fotoğrafları (kart + modal + galeri)
│   ├── ref_*.png           Müşteri/referans logoları (mevcut olanlar)
│   ├── hakkimizda_bg.jpg   Hakkımızda sayfası arkaplan görseli
│   └── belis-icon.png      Site logosu (header/navbar ikonu)
└── docs/                (bu klasör)
```

Daha fazla ayrıntı için: [site-structure.md](site-structure.md), [update-scripts.md](update-scripts.md), [changelog.md](changelog.md).

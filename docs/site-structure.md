# Site Yapısı

## Ortak Bölümler (6 sayfada da tekrarlanır)

Her sayfada aşağıdaki üç blok, **satır satır aynı markup** olarak bulunur (şablon/include sistemi yoktur, bu yüzden bir değişiklik 6 dosyada da tekrarlanmalıdır):

1. **Header/navbar** (`#site-header`, `fixed top-0`) — logo (`assets/belis-icon.png` + "Belis" yazısı), masaüstü nav linkleri (Ana Sayfa/Hakkımızda/Hizmetler ▾/Projeler ▾/Referanslar/İletişim), mobil hamburger butonu.
2. **Mobil "cam" menü** (`#mobile-menu`) — tam ekran overlay, backdrop-blur, Hizmetler/Projeler için açılır alt menüler (`.mm-sub`, `mmGo(categoryKey)` fonksiyonuyla `filterCategory()`'ye yönlendirir).
3. **Footer** — iletişim bilgileri, kısa linkler, telif hakkı satırı.

> Not: `#mobile-menu .relative > div:first-child` CSS ile gizlenmiştir — mobil menü açıkken görünen "Belis" satırı aslında menünün kendi içindeki (gizli) kopya değil, `z-index: 70` ile öne çıkan asıl `#site-header`'dır.

## Sayfa Bazlı Notlar

### `index.html`
- Tam ekran hero (`#hero`, `min-h-[100dvh]`), arka planda `assets/proje_finans_merkezi.jpg` (`fetchpriority="high"`), canvas tabanlı "twinkle" efekti ve CSS Ken Burns zoom animasyonu.
- Vizyon/misyon 4'lü kart ızgarası.
- `#projelerimiz-slider` bölümünde dairesel proje galerisi (`assets/circular-gallery.js`, WebGL/OGL) — IntersectionObserver ile lazy-init edilir (`rootMargin: 300px`).
- JSON-LD `ElectricalContractor` şeması `<head>` içinde.

### `hakkimizda.html`
- Tam genişlik banner (`assets/hakkimizda_bg.jpg`).
- Vizyon/Misyon/Değerler/Mühendislik 4'lü kart ızgarası — **yalnızca hover efekti** vardır, tıklanabilir/seçilebilir bir "active" state'i yoktur (kasıtlı, bkz. changelog).

### `hizmetler.html`
- **Masaüstü (`lg:` ve üzeri):** sol tarafta kategori bazlı hizmet listesi (`#services-menu`, sticky), sağda detay paneli (`#services-detail-grid` → `#detail-content`). `loadServiceContent(key, scrollToTop)` fonksiyonu içeriği değiştirir; `scrollToTop=true` olduğunda (kullanıcı menüden bir hizmete tıkladığında) pencere otomatik olarak panelin üstüne kaydırılır (bkz. changelog, scroll-reset fix).
- **Mobil (`<lg`):** kart ızgarası (`buildMobileGrid()`) + alttan açılan "bottom sheet" (`#svc-sheet`, `openSheet(key)`), açılışta zaten `scrollTop = 0` ile sıfırlanıyordu.
- URL parametreleri: `?kategori=` (kategori filtreleme) ve `?hizmet=` (doğrudan bir hizmete link).

### `projeler.html`
- Filtrelenebilir proje kartı ızgarası (`filterProjects(categoryKey)`, `.filter-btn.active`) + tıklanınca açılan modal (`#project-modal`, `openModal(key)`/`closeModal()`).
- Modal, DOM'dan kaldırılmaz, yalnızca `hidden`/`opacity-0` sınıflarıyla gizlenir — bu yüzden içindeki scroll konumu `openModal()` içinde elle sıfırlanır (bkz. changelog).
- URL parametresi: `?durum=` (tamamlanan/devam eden filtresi).

### `referanslar.html`
- Diğer 5 sayfadan farklı olarak Tailwind'i **CDN üzerinden (JIT)** yükler, kendi `tailwind.config` scripti canlıdır (diğer sayfalardaki devre dışı kopya kaldırıldı, bkz. changelog).
- `referencesData` dizisi (JS) müşteri adı + opsiyonel `logo` alanından oluşur. Gerçek bir logo dosyası **olmayan** kayıtlarda `logo` alanı bilinçli olarak **yoktur** — bu durumda kart doğrudan firma adını yazıyla gösterir (network isteği/404 oluşmaz).

### `iletisim.html`
- İletişim formu, adres/telefon/e-posta kartları, Google Maps `<iframe>` embed (`loading="lazy"`).

# Changelog — 2026-07-25 / 26

Bu tarihte yapılan güncelleme grupları ve gerekçeleri.

## 0e. Lighthouse performans skoru düşüklüğü — teşhis ve çözüm

**Belirti:** Canlı sitede Lighthouse skorları: masaüstü Performance **78**, mobil **56**. Accessibility 98, Best Practices 100, SEO 100 (bunlar zaten iyiydi, dokunulmadı).

### Teşhis (ölçümle, tahminle değil)

**1. `ogl` WebGL kütüphanesi her sayfa yüklemesinde boşuna iniyordu.**
`assets/circular-gallery.js` galeriyi yalnızca kullanıcı o bölüme kaydırınca başlatmak üzere IntersectionObserver kullanıyordu — ama kütüphaneyi dosyanın en üstünde **statik `import`** ile çekiyordu. ES modüllerinde statik `import`, modül ayrıştırılır ayrıştırılmaz (IntersectionObserver koduna hiç gelinmeden) indirilir. Yani tembel yükleme planı fiilen çalışmıyordu: kullanıcı galeriyi hiç görmese bile her ziyarette `cdn.jsdelivr.net`'ten ~130KB (brotli ~40KB) iniyor, ayrıştırılıp derleniyordu. Mobilde Lighthouse CPU'yu 4x yavaşlattığı için bu ceza mobilde çok daha ağırdı — masaüstü 78 / mobil 56 farkının ana sebebi buydu.

**2. Görseller tek boyutlu JPEG'di.** Mobil ziyaretçi de masaüstüyle aynı 1600px hero'yu (289KB) indiriyordu; modern format (WebP) hiç kullanılmıyordu.

### Çözüm

- **`ogl` dinamik `import()`'a çevrildi** (`initGallery()` içine). Artık yalnızca galeri gerçekten açılacaksa iniyor. Ölçüldü: ilk yüklemede jsdelivr isteği **0**.
- **Tüm görseller WebP'ye çevrildi**, JPEG'ler `<picture>` içinde fallback olarak korundu — WebP desteklemeyen eski tarayıcılar (Safari 13 vb.) hâlâ JPEG alıyor, hiçbir görsel kaybolmuyor.
- **Her sayfanın hero/LCP görseli için 900w mobil varyant** üretildi (`srcset` + `sizes="100vw"`). Mobil cihaz artık 1600w yerine 900w indiriyor.
- **Banner/hero görselleri q=72'ye çekildi.** Bunlar arka plan görselleri: üzerlerinde koyu gradient, başlık metni, ana sayfada ışıldama canvas'ı var ve hero 1.2x zoom ile hareket ediyor. 2x büyütülmüş kırpmalarla q=82 ile karşılaştırıldı — görsel fark yok. Modal/kart içinde **doğrudan** izlenen proje fotoğrafları yüksek kalitede (q=82) bırakıldı.
- Görseller **değiştirilmedi** — aynı fotoğraflar, yalnızca format/boyut/sıkıştırma.

### Ölçülen sonuç (canlı sunucudan, gerçek dosya boyutları)

Ana sayfa, mobil senaryo (375px @dpr2 → 900w seçilir), gzip/brotli dahil:

| Kaynak | Önce | Sonra |
|---|---|---|
| hero görseli | 289 KB (JPEG 1600w) | **91 KB** (WebP 900w) |
| logo | 25 KB (PNG) | **3.6 KB** (WebP) |
| `ogl` (jsdelivr) | 39 KB | **0 KB** |
| HTML + CSS + JS | ~25 KB | ~25 KB |
| **TOPLAM** | **377 KB** | **118 KB** |

**%68 düşüş.** Masaüstünde hero 254 KB → 190 KB.

### Bu geçişte yakalanan iki kendi hatam

- **`display: contents` gerekliliği:** `<img class="w-full h-full">` bir `<picture>` içine alındığında yüzdeler inline `<picture>`'a göre çözülüp layout bozuluyordu. `picture { display: contents; }` eklendi — picture kutu üretmiyor, `<img>` gerçek positioned parent'ına göre boyutlanmaya devam ediyor. 6 sayfada layout birebir korundu (ölçümle doğrulandı).
- **TDZ hatası:** JS ile atanan görseller `<picture>` kullanamadığı için tek seferlik WebP tespiti (`_img()`) eklendi. İlk denemede helper, kullanıldığı yerden ~180 satır **sonraya** enjekte edildi; `const` hoist edilmediği için (temporal dead zone) `hizmetler.html` açılışında `loadServiceContent()` → `_img()` → `ReferenceError` fırlatıp sayfa başlatmasını yarıda kesti (menü doluyor ama hiçbir hizmet açılmıyordu). Helper `<head>`'e taşındı; artık tüm inline bloklardan önce tanımlı.

### Notlar

- `ref_*.png` müşteri logoları kasıtlı olarak PNG bırakıldı (289B–10KB, WebP kazancı yok) — bu yüzden `_img()` yalnızca `.jpg/.jpeg` uzantılarını yeniden eşliyor.
- Galerinin kendisi bu test ortamında doğrulanamadı: tarayıcı paneli görünmediği için sayfa kare üretmiyor ve **IntersectionObserver hiç tetiklenmiyor** (boş bir IO ile ayrıca kanıtlandı). Bunun yerine değişikliğin riskli kısmı doğrudan sınandı: dinamik `import()` başarılı, 7 sınıf da geliyor, `Renderer` WebGL context oluşturuyor. Gerçek tarayıcılarda IO güvenilir çalışır.

## 0d. Ana sayfada mobil menüde "Hizmetler ▾" / "Projeler ▾" hiç açılmıyordu

**Belirti:** Kullanıcı GitHub üzerinden canlı siteyi test ederken "hizmetler ve projeler kısmı hâlâ bazen açılmıyor" diye bildirdi. Canlı sitede (`https://saitjerome.github.io/beli-website/`) kapsamlı testler yapıldı:
- Masaüstünde hizmet listesi butonlarına art arda hızlı tıklama (çalıştı).
- Mobilde hizmet/proje detay sheet'i ve modalı aç→kaydır→kapat→farklısını aç döngüsü 5+ kez tekrarlandı (hepsi doğru, scroll her seferinde sıfırlandı).
- Konsol/network hatası yok, GitHub Pages CDN cache'i güncel (`Age: 0`).

**Gerçek kaynak bulundu:** Bunların hiçbiri değil — sorun **yalnızca ana sayfanın (`index.html`) mobil hamburger menüsündeki "Hizmetler ▾" / "Projeler ▾" satırlarıydı**. Bu satırlara dokunulduğunda hiçbir şey olmuyordu (alt menü açılmıyordu). Kod incelenince: `index.html`'in mobil menü script'i `mmHizBtn`, `mmSub`, `mmChev` değişkenlerini tanımlıyordu ama **hiçbirine `addEventListener` eklenmemişti** — diğer 5 sayfada (`hizmetler.html`, `hakkimizda.html`, `projeler.html`, `referanslar.html`, `iletisim.html`) bu handler'lar zaten doğruydu. Bu, geçmişte `update.py`'nin mobil menü script'ini regex ile değiştirdiği adımda kazara silinmiş bir kod parçasıydı (önceki bir araştırmada da tespit edilmiş ama o zaman düzeltilmemişti).

Kullanıcının "bazen açılmıyor" algısı muhtemelen şuradan geliyordu: ana sayfadayken menü hiç açılmıyor, ama Hizmetler/Projeler sayfalarındayken (kendi menüleri doğru çalıştığı için) açılıyordu — sayfadan sayfaya geçerken tutarsız görünüyordu.

**Çözüm:** `hizmetler.html`'deki çalışan koddan birebir kopyalanarak `index.html`'e eklendi:
```js
if (mmHizBtn) mmHizBtn.addEventListener('click', () => {
  mmSub.classList.toggle('open');
  mmChev.classList.toggle('rot');
});
const mmProjBtn = document.getElementById('mm-projeler-btn');
const mmSubProj = document.getElementById('mm-sub-projeler');
const mmChevProj = document.getElementById('mm-chev-projeler');
if (mmProjBtn) mmProjBtn.addEventListener('click', () => {
  mmSubProj.classList.toggle('open');
  mmChevProj.classList.toggle('rot');
});
```

**Doğrulama:** Yerelde ve canlıda (`saitjerome.github.io/beli-website`) gerçek tıklama simülasyonuyla test edildi — her iki alt menü de artık açılıp kapanıyor, chevron ikonu dönüyor. `git push live main` ile canlıya yansıtıldı (commit `e3401ba`).

## 0c. "Belis" marka yazısı sayfadan sayfaya farklı görünüyordu

**Belirti:** Referanslar sayfasındaki "Belis" yazısı doğru boyut/renkte, diğer 5 sayfada (index, hakkımızda, hizmetler, projeler, iletişim) farklı görünüyordu — halbuki HTML'deki `class` string'i **6 sayfada da birebir aynıydı** (`text-[24px] md:text-[30px] font-extrabold tracking-tighter text-[#08274F]`).

**Kök neden:** Yine precompiled `tailwind.css` eksikliği. `referanslar.html` diğerlerinden farklı olarak Tailwind'i CDN'den (JIT derleyici) yüklüyor — CDN her class'ı anında üretebildiği için orada yazı doğru boyut/renkte çıkıyordu. Diğer 5 sayfa ise elle derlenmiş `assets/tailwind.css`'i kullanıyor ve bu dosyada `text-[24px]`, `text-[30px]`, `tracking-tighter`, `text-[#08274F]` sınıflarının **hiçbiri yoktu** — yazı bu yüzden tarayıcı varsayılanına (farklı boyut, siyaha yakın varsayılan renk) düşüyordu.

**Çözüm:** Kırılgan arbitrary-value sınıfları kaldırıldı, yerine 6 sayfanın da inline `<style>` bloğuna eklenen `.brand-text-header` (24px mobil / 30px ≥768px) ve `.brand-text-drawer` (sabit 24px, mobil çekmece için) özel sınıfları kondu — ikisi de `font-weight:800`, `letter-spacing:-0.05em`, `color:#08274F`. Artık CDN'e bağımlı olmadan 6 sayfada da bire bir aynı görünüyor (Referanslar'daki dahil — o da artık aynı sağlam sınıfı kullanıyor, CDN şansına bağlı değil).

**Doğrulama:** `index.html` ve `referanslar.html` yan yana ekran görüntüsüyle karşılaştırıldı — boyut ve renk artık birebir aynı, konsolda hata yok.

## 0. İkinci geçiş: kullanıcı geri bildirimiyle bulunan ek hatalar

İlk geçişten sonra kullanıcı canlı/yerel önizlemede test edince üç ek sorun daha bildirdi. Kök neden hepsinde ortak: **precompiled `assets/tailwind.css` dosyası, sayfalardaki bazı Tailwind sınıflarını içermiyor** (JIT/CDN ile değil, elle/derlenmiş bir dosyayla çalışıyor) — bu sınıflar HTML'de yazılı olsa da tarayıcıda hiçbir CSS kuralı üretmiyor, sessizce yok sayılıyor.

- **Sayfa üstü banner'lar çökmüştü:** `hakkimizda.html`, `hizmetler.html`, `iletisim.html`, `projeler.html`, `referanslar.html`'deki `h-[320px] md:h-[400px] xl:h-[480px]` ve `pb-12 md:pb-20` sınıfları `tailwind.css` içinde **hiç yoktu** — bu yüzden banner section'ı yükseklik almıyor, içeriğe göre küçülüyordu (ör. `projeler.html`'de 320px yerine 152px). Sonuç: sayfa başlığı (`<h1>`) ve rozet (`PROJELERİMİZ` vb.) kısmen/tamamen sabit header'ın **arkasında** kalıyordu — kullanıcının ekran görüntüsünde gördüğü "üst kısımlar bozuk, yazılar sığmıyor" görüntüsünün sebebi buydu. Aynı zamanda bu, **"hizmetler/projeler kısmı bazen tıklamıyor" şikayetinin de olası kaynağıydı**: banner çöktüğü için altındaki içerik yukarı kayıyor, bazı öğeler sabit header'ın altında/arkasında kalıp tıklamaları header'a kaptırıyordu.
  - **Çözüm:** Arbitrary-value sınıflar kaldırıldı, yerine her sayfanın inline `<style>` bloğuna eklenen `.page-banner` özel sınıfı (320px / 400px / 480px yükseklik + 48px / 80px alt boşluk, medya sorgularıyla) kondu. 5 sayfada da doğrulandı: section artık gerçekten 320/400/480px yükseklikte, başlık header'ın belirgin şekilde altında.
- **Ana sayfadaki "Öne Çıkan Projelerimiz" dairesel galerisi boş kalıyordu:** WebGL galerisi (`assets/circular-gallery.js`), `cdn.jsdelivr.net`'ten OGL kütüphanesini modül olarak içe aktarıyor; bu içe aktarma bir sebeple (ağ/CDN erişimi, WebGL desteği vb.) başarısız olursa **modülün tamamı sessizce çalışmayı durduruyor** ve o bölüm tamamen boş kalıyordu — kodun kendi "yedek kaydırıcı" mantığı (`#project-carousel` id'sini arayıp gösterme) zaten vardı ama karşılığında **hiç HTML yoktu** (önceki bir güncellemede kaldırılmıştı). Artık `index.html`'e statik bir yedek kaydırıcı eklendi: 6 proje fotoğrafı, başlıklarıyla, yatay kaydırılabilir kartlar halinde — WebGL galerisi başarıyla yüklenirse JS bunu otomatik gizliyor (`carousel-hidden` sınıfı), yüklenemezse (CDN engelli olsa bile) kullanıcı hep bir şeyler görüyor.
- **Logo ile "Belis" yazısının tonu uyuşmuyordu:** Header'daki yazı `#003B6F` (sitenin genel parlak lacivert tonu) kullanıyordu, oysa yeni logo amblemi daha koyu bir lacivertti (`#08274F`, amblemden örneklendi). 6 sayfanın header + mobil çekmece metninde yazı rengi `#08274F`'e çekildi, artık ikon ve yazı aynı tonda.

## 0b. Portfolyo galerisi canlı sitedeki haline geri getirildi (gerileme düzeltmesi)

**Kullanıcının bildirdiği belirti:** Ana sayfadaki "Öne Çıkan Projelerimiz" (PORTFOLYO) bölümü, canlı `beliselektrik.com.tr` üzerindeki "şık, akıp oynayan" halinden farklı görünüyordu — kısa, ezilmiş, cansız bir kart şeridi gibi.

**Teşhis (düzeltmeden önce yapılan kontroller):**
1. `assets/circular-gallery.js` canlı sürümle **birebir aynı** (`diff` → `IDENTICAL`). Yani React Bits `CircularGallery` portu sağlamdı, hata JS'te değildi.
2. `jsdelivr` üzerinden gelen OGL modülü de erişilebilirdi (fetch → 200 OK), galeri gerçekten başlıyordu.
3. Asıl sorun **CSS'te**: canlı `index.html`'de bulunan `#circular-gallery` kural bloğu yerel kopyada **hiç yoktu**. Ölçümle doğrulandı: galeri kabı, masaüstü 1440px'te bile yalnızca **150px** yüksekliğindeydi (olması gereken 520px). Sebep: yükseklik tanımı olmayan kap, içine eklenen `<canvas>` elemanının varsayılan 300×150 boyutuna çöküyordu — yani kap canvas'ı, canvas kabı ölçüyordu. Kartlar bu yüzden minik ve kırpılmış çıkıyordu.
4. Aynı blokla birlikte sol/sağ ok butonları (`slider-prev-btn` / `slider-next-btn`), `display:none` + `.loaded` görünürlük mantığı, `cursor: grab`, `touch-action: pan-y` ve "Tüm Projelerimizi Görüntüleyin" butonu da kaybolmuştu.

**Kök neden:** Bu CSS bloğu ve markup, ilk geçişteki "ölü kod temizliği" adımında (devre dışı Tailwind config script'inin kaldırılması) kazara birlikte silinmiş — yani bu bir **gerileme (regression)**, kullanıcının orijinal tasarımında bir eksiklik değil.

**Çözüm:** Canlı siteden (`curl` ile) alınan portfolyo bölümü ve CSS bloğu **aynen** geri yazıldı:
- `#circular-gallery` → `height: 400px` (mobil) / `520px` (≥768px), `display:none` + `.loaded { display:block }`, `cursor: grab`/`grabbing`, `touch-action: pan-y`, `canvas { width:100%; height:100% }`.
- 6 detaylı yedek proje kartı (başlık, konum, açıklama, kategori/durum etiketleri, snap-scroll), sol/sağ ok butonları ve "Tüm Projelerimizi Görüntüleyin" butonu.
- Ara geçişte denenen "kayan marquee" yedeği kaldırıldı (kullanıcı canlıyla birebir aynı olmasını tercih etti).
- Tek sapma (kasıtlı, görünümü etkilemez): yedek kartların `<img>` etiketlerine `width`/`height` + `decoding="async"` eklendi — CLS koruması, ilk geçişteki optimizasyonla tutarlı.

**Doğrulama:** Masaüstü 1440px → galeri 520px, mobil 375px → 400px; `loaded` sınıfı geliyor, yedek kaydırıcı otomatik gizleniyor (`display: none`), oklar ve alt buton yerinde, konsolda hata yok.

---

Aşağıda ilk geçişte yapılan dört güncelleme grubu ve gerekçeleri.

## 1. Scroll-reset hatası düzeltildi

**Sorun:** Hizmetler veya Projeler sayfasında bir öğe açılıp en alta kadar kaydırıldıktan sonra kapatılıp farklı bir öğe açıldığında, yeni içerik en alttan/ortadan başlıyormuş gibi görünüyordu.

**Kök neden (1. deneme — eksik kaldı):** İlk geçişte `projeler.html`'deki `openModal()` ve `hizmetler.html`'deki masaüstü `loadServiceContent()` için scroll sıfırlama eklendi, mobil `openSheet()`'in zaten `c.scrollTop = 0` içerdiği görülüp dokunulmadı. Otomatik testte (fonksiyonları doğrudan JS ile çağırarak) sorun çözülmüş gibi göründü — ama bu test "kapatıp farklısını açma" döngüsünü değil, "modal zaten açıkken başka bir öğeye geçme" senaryosunu ölçüyordu, bu yüzden asıl hatayı kaçırdı.

**Gerçek kök neden:** Kullanıcı geri bildirimiyle (gerçek tıklamalarla, aç → kaydır → kapat → farklısını aç sırasıyla) yeniden test edilince hata hâlâ vardı. Sebep: hem `projeler.html`'deki `openModal()` hem de `hizmetler.html`'deki `openSheet()` içinde, `scrollTop = 0` ataması modal/sheet **hâlâ `hidden` (`display:none`) sınıfını taşırken** yapılıyordu. Tarayıcılar `display:none` bir elemanın (veya üstündeki bir elemanın) `scrollTop` atamasını sessizce yok sayar — bu yüzden "kapat → aç" döngüsünde bir önceki öğenin scroll konumu görsel olarak korunuyordu, kod çalışıyor gibi görünse de fiilen hiçbir şey yapmıyordu.

**Kesin çözüm:**
- `projeler.html` → `openModal()`: `scrollArea.scrollTop = 0` artık `modal.classList.remove('hidden')`'dan SONRA çalıştırılıyor (ayrıca 50ms'lik açılış animasyonunun sonunda ikinci bir güvenlik sıfırlaması daha var).
- `hizmetler.html` → `openSheet()`: aynı şekilde `c.scrollTop = 0`, `sheet.classList.remove('hidden')`'dan sonra ve ayrıca açılış animasyonu tamamlandığında (`requestAnimationFrame` içinde) tekrar uygulanıyor.
- `hizmetler.html` → masaüstü 2 kolonlu panel (`loadServiceContent(key, scrollToTop)`): bu panel hiç gizlenmediği (`display:none` olmadığı) için ilk çözüm zaten doğru çalışıyordu — değişiklik gerekmedi.
- Gerçek tıklama senaryosuyla (Browser aracıyla, aç → aşağı kaydır → kapat → 1sn bekle → farklı bir öğe aç) hem `projeler.html` hem `hizmetler.html` mobil sheet'i için düzeltme doğrulandı.

**Ders:** Bu tür "önceki durum kalıntısı" hatalarını test ederken fonksiyonu doğrudan çağırmak yeterli değil — gerçek kapat/aç döngüsünü (özellikle `hidden`/`display:none` geçişlerini) simüle etmek gerekiyor.

**Not:** Hakkımızda sayfasındaki "tıklayınca yeşil yanmıyor" şikayeti araştırıldı; o sayfada tıklanabilir bir seçenek/sekme grubu bulunmadığı (yalnızca hover efektli 4 kart var) teyit edildi ve kullanıcı onayıyla bu madde kapsam dışı bırakıldı.

## 1b. Logo ikonundaki kusur düzeltildi

İlk kırpımda `assets/belis-icon.png`'nin sağ alt köşesinde küçük, açıklanamayan bir leke vardı. İncelemede bunun amblemin bir parçası değil, orijinal logo görselindeki "BELİS" yazısının **İ harfinin noktası** olduğu anlaşıldı (İ noktası, harflerin üst çizgisinden daha yukarıda başladığı için ilk kırpma sınırına taşmış). Kırpma satırı daraltılıp ikon yalnızca "B + şimşek" amblemini içerecek şekilde yeniden oluşturuldu (464×513 → 160×177px, ~26 KB) ve site genelinde (6 sayfa × 2 konum) değiştirildi; `width`/`height` HTML öznitelikleri de yeni en-boy oranına göre güncellendi.

## 2. Logo entegrasyonu (header/navbar)

Kullanıcının sağladığı logo görseli (lacivert "B" + şimşek amblemi + "BELİS ELEKTRİK" yazısı) işlendi:
- Amblem kısmı görselden kırpılıp `assets/belis-icon.png` olarak kaydedildi (160×193px, ~27 KB — önceki tam çözünürlüklü kırpımdan ~7 kat daha küçük).
- 6 sayfanın da masaüstü header'ında ve mobil çekmecesinde, önceden yalnızca düz metin olan "Belis" markası artık `[ikon] Belis` şeklinde (ikon + mevcut metin) gösteriliyor.
- Boyutlandırma için Tailwind'in üretmediği (`h-7`, `h-8`, `w-auto` gibi) keyfi sınıflar yerine, her sayfanın zaten var olan inline `<style>` bloğuna özel `.brand-icon` / `.brand-icon-mobile` kuralları eklendi — çünkü 5 sayfa önceden derlenmiş, purge edilmiş bir `tailwind.css` kullanıyor ve bu dosyada olmayan sınıflar sessizce hiçbir şey yapmıyor.
- Kapsam kullanıcı onayıyla yalnızca header/navbar ile sınırlı tutuldu; footer ve favicon değiştirilmedi.

## 3. Performans / SEO / Erişilebilirlik / Best Practices optimizasyonu

Kullanıcının Lighthouse ölçümü (canlı site): Performance 57, Accessibility 98, Best Practices 78, SEO 100. Yapılan değişiklikler:

- **Görsel ağırlığı (en büyük kazanç):** `assets/` klasörü ~20 MB → ~4,8 MB. Ana neden: çoğu `banner_*.jpg` dosyası aslında `.jpg` uzantılı olmasına rağmen **PNG olarak kodlanmıştı** (fotoğrafik içerik için çok verimsiz). Tüm 39 görsel gerçek JPEG'e (mozjpeg, kalite 78, progressive) yeniden kodlandı ve kullanım bağlamına göre yeniden boyutlandırıldı (banner/hero: 1600px genişlik, proje kartları: 1100px genişlik; ana sayfa hero'su tam viewport kaplayan tek istisna olduğu için 1600px'de tutuldu).
- Tüm statik `<img>` etiketlerine `width`/`height` eklendi (CLS önleme); ilgili sayfa banner'larına `fetchpriority="high" decoding="async"` eklendi (LCP önceliği).
- `hizmetler.html`'de eksik olan `<meta name="description">` eklendi.
- Tüm 6 sayfaya `<link rel="canonical">`, Open Graph ve Twitter Card meta etiketleri eklendi.
- `index.html`'e `ElectricalContractor` (schema.org) JSON-LD yapılandırılmış verisi eklendi (ad, adres, telefon, e-posta).
- Ölü kod temizliği: `index.html`'deki DOM'da karşılığı olmayan carousel JS kaldırıldı; 5 sayfadaki devre dışı (`type="text/plain"`) Tailwind config script bloğu (~2,5 KB/sayfa) kaldırıldı (`referanslar.html`'deki canlı config'e dokunulmadı, o sayfa CDN Tailwind kullanıyor).
- Kullanılmayan `assets/test.png` silindi.
- `referanslar.html`: `referencesData` dizisinde gerçekte var olmayan 12 logo dosyasına (`ref_gokyol.png`, `ref_baris_insaat.png` vb.) yapılan referanslar kaldırıldı — artık bu firmalar için hiç `<img>` denenmiyor, doğrudan metin (firma adı) gösteriliyor. Böylece tarayıcı konsolunda gereksiz 404 istekleri oluşmuyor.
- Dairesel proje galerisi (`assets/circular-gallery.js`) zaten IntersectionObserver ile lazy-init ediliyordu (`rootMargin: 300px`) — bu doğrulandı, ek değişiklik gerekmedi.

**Doğrulama:** Yerel bir statik sunucu üzerinden 6 sayfa da tekrar açıldı; konsolda hata/404 olmadığı, scroll-fix ve logonun doğru render edildiği teyit edildi. Canlı sitede aynı optimizasyonların etkisini görmek için bu klasördeki dosyaların sunucuya (FTP/hosting paneli) yeniden yüklenmesi gerekiyor — bu oturumda bir deploy/yükleme işlemi yapılmadı.

## 4. `docs/` klasörü

Bu dokümantasyon klasörü oluşturuldu: [README.md](README.md) (genel bakış), [site-structure.md](site-structure.md) (sayfa/bileşen yapısı), [update-scripts.md](update-scripts.md) (geçmiş toplu güncelleme scriptlerinin özeti) ve bu changelog.

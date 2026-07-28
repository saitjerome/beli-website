# Changelog — 2026-07-25 / 26

Bu tarihte yapılan güncelleme grupları ve gerekçeleri.

## 0p. Asıl kaynak bulundu: Material Symbols ikon fontu 1,1 MB'tı (%72 küçültüldü)

**Belirti:** Site sahibi PSI'da mobil skor için 0o'daki ken-burns düzeltmesinden sonra **hâlâ 56-58** aldı. PSI raporu doğrudan (headless tarayıcıyla taze analiz tetiklenip) incelendiğinde: **FCP 8,0 sn, LCP 9,5-10,9 sn, TBT 0 ms**. TBT'nin sıfır olması, sorunun artık CPU/animasyon değil, **ilk boyamadan önceki ağ/yükleme** olduğunu gösteriyordu — bu, 0n/0o'daki tüm CPU-eksenli çalışmanın (canvas damgaları, kare hızı, ken-burns) yanlış hedefe odaklandığını ortaya çıkardı.

**Yanlış giden ilk hipotez (kayda değer, ders çıkarılan bir çıkmaz sokak):** Önce hero animasyonunun `<body>` sonunda senkron çalışıp ilk boyamayı bloke ettiği düşünüldü — kodun içine `performance.now()` ile gerçek zaman damgaları ("HEROMARK") eklenip gerçek CDP CPU+ağ kısıtlaması (`Network.emulateNetworkConditions` + `Emulation.setCPUThrottlingRate`, "simulate" değil "devtools" modu) altında ölçüldü. Sonuç: heroLights() IIFE'nin senkron kısmı yalnızca **14 ms** sürüyordu — animasyon hiç suçlu değildi. Asıl bulgu: `window.load` olayı navigasyondan **~8,8 saniye sonra** ateşleniyordu.

**Gerçek kök neden — tam ağ izlemesiyle bulundu:** Aynı CDP throttling altında tüm network isteklerinin başlangıç/bitiş zamanları tek tek loglandı (`.claude/trace-network.js`). Tek bir istek her şeyi domine ediyordu:
```
+2490ms -> +8778ms (6325ms!)  320076B  https://fonts.gstatic.com/.../materialsymbolsoutlined/...
```
Bu, `Material+Symbols+Outlined:wght,FILL@100..700,0..1` sorgusuyla istenen ikon fontu — **1.125.820 bayt (1,1 MB)**. Sebep: `wght,FILL@100..700,0..1` iki değişken ekseni TAM ARALIKTA istiyor (ağırlık 100-700 arası + dolgu 0-1 arası sürekli enterpolasyon), Google bu yüzden devasa bir dosya üretiyor. Sitede bu iki eksenin **hiçbir yerde override edilmediği** (tüm ikonlar varsayılan: outline, normal kalınlık) doğrulandı. Bu tek istek Slow 4G'nin (1,6 Mbps) tüm bant genişliğini ~6,3 saniye boyunca tükettiği için, aynı anda yüklenen hero görseli/fontlar gibi gerçekten kritik kaynaklar da bant genişliği için yarışıp gecikiyordu — dolayısıyla FCP/LCP'yi dolaylı olarak (senkron script değil, ağ/bant genişliği yarışı yoluyla) 8 saniyeye kadar geciktiriyordu.

**Çözüm:** 6 sayfada da eksenler sabit tek değere çekildi: `wght,FILL@400,0` (400 = normal kalınlık, 0 = dolu değil/outline — sitede fiilen kullanılan tek değerler). Sonuç: **1,1 MB → 320 KB (%72 küçülme)**. (Ayrıca ikon bazlı alt kümeleme de denendi — Google'ın `&text=` parametresiyle yalnızca kullanılan 43 ikonu istemek dosyayı 260 KB'a indirdi, ama kazanç marjinal ve URL kırılgan/özel bir uç noktaya bağımlıydı; sabit-eksen çözümü hem daha güvenli hem yeterince etkili olduğu için o tercih edildi.)

**Doğrulama (aynı gerçek throttling, önce/sonra):**

| | Önce | Sonra |
|---|---|---|
| `window.load` olayı | +8818 ms | **+4906 ms** (%44 azalma) |
| İkon fontu indirme süresi | 6325 ms | 2396 ms |
| İkon fontu boyutu | 1.125.820 B | 320.076 B |

**Ders:** Bu oturumun en büyük teşhis hatası, TBT=0 olduğu hâlde CPU/animasyon maliyetine odaklanmaya devam etmekti — TBT'nin sıfır olması, "ilk boyamadan SONRA blokaj yok" demekti, "ilk boyamadan ÖNCE de sorun yok" demek değildi. Asıl sinyal her zaman oradaydı (FCP=LCP=SI, hepsi aynı yüksek değerde) ama CPU-eksenli önceki bulgulara (0n) fazla güvenilip yanlış yöne devam edildi. Ağ izlemesi (gerçek istek/bitiş zamanları) nihayet doğru kaynağı gösterdi.

## 0o. Doğrulama yöntemi PageSpeed Insights'a çevrildi + ken-burns mobilde kapatıldı

**Yöntem değişikliği:** 0n'de yerel Lighthouse ölçümlerinin makine hızına bağlı olarak iyimser sonuç verdiği anlaşıldıktan sonra, site sahibi doğrulamanın bundan sonra doğrudan [PageSpeed Insights](https://pagespeed.web.dev/analysis?url=https%3A%2F%2Fsaitjerome.github.io%2Fbeli-website%2F) üzerinden yapılmasını istedi. Bu noktadan itibaren yerel `lh.js` ölçümleri yalnızca **göreceli karşılaştırma** ("bu değişiklik doğru yöne mi gidiyor") için kullanılıyor; kabul kriteri PSI.

**Uygulanan değişiklik:** 0n'de canlı sitede (`LH_CPU=16`, PSI'ye yakın koşul) izole edilen üç maliyet kaleminden en büyüğü olan hero ken-burns zoom animasyonu (`heroKen`, `.hero-img` üzerinde sürekli `transform: scale`) mobilde kapatıldı:

```css
@media (max-width: 767px) {
  .hero-glow { filter: blur(46px); animation: none !important; }
  .hero-img { animation: none !important; }  /* yeni */
}
```

Masaüstünde dokunulmadı (zaten TBT 0 ms). Görsel etki: mobilde hero görseli sabit durur (yavaş zoom kaybolur), banner'ın kendisi ve ışık/leke animasyonları aynen kalır.

**Yerel göreceli doğrulama** (`LH_CPU=16`, kabul kriteri değil, yön kontrolü): medyan skor 78 → 85, TBT'de düşme yönü teyit edildi (16x throttling'de run'dan run'a ±300ms oynama normal — tek ölçümle kesin sayı iddia edilmiyor).

**Doğrulama:** Mobil ekran görüntüsü (412×823) ile hero'nun düzgün render edildiği, metnin/butonların yerinde olduğu teyit edildi. Canlıya gönderildikten sonra nihai kabul kriteri: kullanıcının PSI'da tekrar çalıştıracağı mobil skor.

## 0n. Yerel ölçümün yanıltıcılığı ve gerçek mobil maliyetin bulunması

**Belirti:** Site sahibi PageSpeed Insights'ta (Google'ın kendi sunucusunda çalışır, kullanıcının makinesi denklemden çıkar) ana sayfa için mobilde **56** aldı. Yerel ölçümlerim ise 98-99 gösteriyordu.

**Kök neden — ölçüm ortamı:** Lighthouse, CPU yavaşlatmasını (`cpuSlowdownMultiplier`) **host makinenin üzerine** uyguluyor. Bu makinenin Lighthouse hız endeksi **~2018**; PageSpeed Insights sunucuları tipik olarak 700-1300 bandında. Yani "4x yavaşlatma" burada hâlâ hızlı bir cihazı temsil ediyordu ve **yerel skorlar sistematik olarak iyimserdi**. `lh.js`'e `LH_CPU` ortam değişkeni eklenerek yavaşlatma çarpanı ayarlanabilir hale getirildi ve ölçümler PSI'ye yakın koşullarda tekrarlandı (16x). O koşulda skor **65** çıktı — yani site sahibinin gördüğü tabloyla aynı sorun görülebildi.

**Gerçek maliyet kalemleri (16x, izole ölçüm):**

| Kaldırılan | TBT | Skor |
|---|---|---|
| (hiçbiri) | 1244 ms | 65 |
| Hero canvas animasyonu | 537 ms | 76 |
| + hero ışık lekeleri | 377 ms | 80 |

Ana iş parçacığı dökümü, yükün script değil **çizim/stil** tarafında olduğunu gösterdi (Script Evaluation yalnızca 183 ms, Style & Layout ~2700 ms).

**Çözüm (ışıklar korunarak, üç kalem):**
1. **Canvas piksel sayısı düşürüldü.** Mobilde DPR 1.75 ile canvas 721×1440 ≈ **1 milyon pikseldi** ve her karede tamamı yeniden çiziliyordu. Küçük ekranlarda DPR 1'e sabitlendi, masaüstünde 1.5 tavanı kondu. Yumuşak ışık lekelerinde bu fark gözle seçilmiyor.
2. **Kare hızı ~30'a sınırlandı.** Işıklar yavaş yanıp söndüğü için 60/30 farkı görünmüyor, çizim maliyeti yarıya indi. Zaman adımı gerçek geçen süreye bağlandığı için **animasyonun hızı değişmedi**.
3. **Hero ışık lekeleri mobilde hafifletildi.** `blur(80px)` filtreli iki büyük leke sürekli animasyonluydu; mobilde bulanıklık 46px'e indirildi ve hareket durduruldu (lekeler görünmeye devam ediyor).

**Sonuç (16x, yavaş cihaz koşulu):** TBT **1244 → 358 ms**, skor **65 → 80**. Animasyon çalışmaya devam ediyor; üstelik animasyonun tamamen kapalı olduğu duruma (377 ms) göre bile daha iyi.

**Standart koşulda gerileme yok:** masaüstü **99** (LCP 0.97s, TBT 0 ms), mobil TBT 0 ms.

**Ders:** Yerel Lighthouse skorları makineye bağlıdır ve hızlı bir geliştirme makinesinde gerçek cihazları temsil etmez. Mobil performansı doğrulamak için ya PageSpeed Insights (sunucu tarafı, nötr) kullanılmalı ya da CPU çarpanı makinenin hız endeksine göre yükseltilmelidir.

## 0m. Işıklar orijinalin altına indirildi — "sayı değil, boyut" bulgusu

**Belirti:** 0l'deki geri almadan sonra site sahibi "ışıklar azalmadı, adeti artmış" dedi.

**Ölçümle doğrulama:** Önce ışık adedi ilk commit (`2d5fd96`) ile karşılaştırıldı — **birebir aynıydı** (120/14/9), yani geri alma doğru çalışmıştı. Ancak gözlem yine de yerindeydi, sebebi farklıydı: 0j'deki performans düzeltmesinde çizim yöntemi `shadowBlur`'dan damga (sprite) tabanlıya geçmişti. İki yöntem aynı parçacık verisiyle yan yana render edilip ölçüldü (`.claude/compare-lights.html` + `run-compare.js`):

| | ışıklı alan % | ortalama parlaklık |
|---|---|---|
| Orijinal (shadowBlur) | 1.30 | 3.30 |
| Damga sürümü (0j) | 1.53 | 3.87 |

Yani damgalar orijinalden **1.2 kat daha geniş ve parlak**tı. Işıklar çoğalmamış, her biri irileşmişti — "daha fazla" algısının kaynağı buydu. Bu, 0j'de gözden kaçan bir sapmaydı: performans düzeltmesi görünümü birebir korumalıydı, %20 sapma bırakmıştı.

**Çözüm (iki cephede):**
1. **Damga orijinale çekildi:** çizim çapı `r*2+12` → `r*2+9`, gradyan sönümü sıkılaştırıldı (`0.45/0.25` → `0.38/0.18`).
2. **Adet azaltıldı** (site sahibinin açık isteği): ışıklar 120 → **78** (formül `w*h/12000` → `w*h/19000`), bokeh 14 → **9**, ikaz ışıkları 9 → **6**. Alan tabanlı formül korundu, küçük ekranlarda otomatik daha az üretiliyor.

**Sonuç:** Yeni hâli orijinalin **yarısı** (ışıklı alan ×0.5, parlaklık ×0.5) — belirgin şekilde sakin, abartısız bir gece dokusu.

**Ölçüm:** Masaüstü **98** (LCP 1.10s, TBT 0 ms), mobil TBT **0 ms**. Banner iyileştirmesi (q92 + keskinleştirme, 428 KB) korundu.

## 0l. Animasyon yoğunlaştırması geri alındı (site sahibi tercihi)

0k'daki iki değişiklikten **yalnızca banner kalitesi korundu**; animasyon yoğunlaştırması geri alındı.

**Gerekçe:** Site sahibi yoğunlaştırılmış ışıkları gördükten sonra "çok fazla oldu, abartı oldu, eski hali daha iyi" geri bildirimini verdi. Performans açısından bir sorun yoktu (TBT her iki cihazda 0 ms idi) — karar tamamen estetik.

**Geri alınanlar** (0j'deki optimize edilmiş hâline dönüldü): damga çözünürlüğü 128px → 64px, ışık sayısı üst sınırı 190 → 120 (formül `w*h/8200` → `w*h/12000`), bokeh 20 → 14, ikaz ışıkları 13 → 9, ışık boyutu çeşitliliği kaldırıldı, glow gradyanı sade hâline döndü.

**Korunanlar:** 0j'deki performans düzeltmeleri (damga önbelleği + görünürlük denetimi) ve 0k'daki masaüstü banner iyileştirmesi (q92 + keskinleştirme, 428 KB) olduğu gibi duruyor.

**Ölçüm:** Masaüstü **99** (LCP 1.11s, TBT 0 ms) — ışıklar seyreldiği için 98'den 99'a çıktı.

**Not:** `index.html` bu adımda `git checkout 296206a -- index.html` ile geri alındı; o commit'in `index.html`'de yalnızca animasyon kodunu değiştirdiği diff ile doğrulandıktan sonra uygulandı, böylece başka bir düzeltme kazara geri alınmadı.

## 0k. Kazanılan performans bütçesi kaliteye çevrildi (animasyon + masaüstü banner)

0j'deki optimizasyon masaüstünde TBT'yi 40.243 ms'den 0 ms'ye indirmiş, skoru 65'ten 98'e çıkarmıştı. Bu, elde ciddi bir performans bütçesi bıraktı; o bütçe görsel kaliteye çevrildi. Her adım ölçülerek yapıldı (`.claude/lh.js` ile gerçek Lighthouse).

**1. Animasyon kalitesi**
- **Damga çözünürlüğü 64px → 128px.** Bokeh kürecikleri 96px'e kadar büyütülerek çiziliyordu; 64px'lik damga bu boyutta upscale edilip yumuşuyordu. Damgalar bir kez üretilip önbelleğe alındığı için bu büyütmenin kare-başına maliyeti yok.
- **Daha zengin ışık geçişi.** Glow gradyanına ara duraklar eklendi (parlak çekirdek → sıcak hale → yumuşak sönüm), daha fotografik bir "bloom" hissi veriyor.
- **Yoğunluk artırıldı.** Işık sayısı ~%35 arttı (formül `w*h/12000` → `w*h/8200`, üst sınır 120 → 190), bokeh 14 → 20, ikaz ışıkları 9 → 13. Alan tabanlı formül korunduğu için küçük ekranlarda otomatik olarak daha az ışık üretiliyor.
- **Boyut çeşitliliği.** Işıkların ~%12'si belirgin şekilde daha büyük; çoğunluk küçük noktalar. Daha derin, gerçekçi bir şehir dokusu veriyor.

**2. Masaüstü banner kalitesi** (yalnızca 1600w dosya — mobil 900w dosyaya dokunulmadı)
- q90 → **q92 + hafif keskinleştirme** (`sharpen sigma 0.6`). Salt kaliteyi yükseltmek yeterli değildi: kaynak zaten sıkıştırılmış bir JPEG olduğu için q95'e çıkmak +125 KB'a karşılık gözle görülmeyen bir fark veriyordu. Hafif keskinleştirme ise sıkıştırma/yeniden boyutlandırmadan gelen yumuşamayı telafi ederek **gerçek bir netlik kazancı** sağlıyor (2x kırpmada bina kenarları ve pencere detayları belirgin şekilde toparlandı).
- Boyut: 367 KB → 429 KB (+62 KB).

**Ölçülen sonuç (yerel, 3'er ölçüm):**

| | Değişiklik öncesi | Sonra |
|---|---|---|
| Masaüstü | 98 (LCP 1.04s, TBT 0 ms) | **98** (LCP 1.10s, TBT 0 ms) |
| Mobil | 98-99 | **95** medyan, TBT **0 ms** |

Masaüstünde skor korundu: banner 62 KB büyüdü, LCP yalnızca 60 ms arttı ve masaüstünün 1.2s eşiğinin belirgin şekilde altında kaldı. Animasyon %35 yoğunlaşmasına rağmen TBT her iki cihazda da 0 ms.

Mobil ölçümlerdeki oynama (89-98 arası) localhost kaynaklı ölçüm gürültüsüdür; **mobil hero dosyası bu adımda hiç değişmedi** (91 KB, canlıda 99 puan almıştı) ve mobil TBT 0 ms olarak doğrulandı.

**Doğrulama:** Animasyonun duraklatma davranışı yeniden test edildi — hero ekrandayken 60 kare/sn, ekran dışında **0 kare/sn**, geri dönünce yeniden başlıyor. Hero görüntüsü ekran görüntüsüyle kontrol edildi.

## 0j. Asıl performans darboğazı bulundu: hero ışıldama animasyonu (masaüstü 85 → 98)

**İstek:** Mobili bir önceki (iyi) haline döndürmek; masaüstünde ana banner kalitesini puan düşürmeden olabildiğince artırmak.

**Önce yapısal tespit:** Hero görseli `srcset` ile iki ayrı dosya sunuyor (`900w` ve `1600w`, `sizes="100vw"`). Lighthouse emülasyonunda:
- **Mobil**: 412px × DPR 1.75 = 721px ihtiyaç → **900w** dosyayı seçer
- **Masaüstü**: 1350px × DPR 1 → **1600w** (tam boy) dosyayı seçer

Yani mobil ve masaüstü **farklı dosyalar** kullanıyor ve birbirinden bağımsız ayarlanabiliyor. Bu sayede mobil eski kalitesine döndürülürken (900w: q74/q78) masaüstü yüksek kalitede (1600w: q90) bırakılabildi — ikisi çakışmıyor.

**Asıl bulgu — gerçek Lighthouse ölçümüyle:** Bu oturumda tahmin yerine ölçüm yapmak için `lighthouse` + `puppeteer-core` kurulup yerel Chrome üzerinden gerçek denetimler koşuldu (`.claude/lh.js`). Masaüstünde TBT (Total Blocking Time) **40.243 ms** çıktı — yani puan kaybının kaynağı görsel boyutu değildi. Kaynağı izole etmek için hero canvas'ı devre dışı bırakılıp ölçüm tekrarlandı:

| Durum | TBT | Skor |
|---|---|---|
| Hero animasyonu açık | 40.243 ms | 65 |
| Hero animasyonu kapalı | 0 ms | **98** |

Yani puanı yiyen tek şey ana sayfadaki **ışıldama (twinkle) canvas animasyonu**ydı.

**Neden bu kadar pahalıydı:** Animasyon her karede, her ışık için `ctx.shadowBlur` (canvas'ın en pahalı işlemlerinden biri, her çizim için ayrı bir bulanıklık geçişi zorluyor) ve her bokeh küreciği için sıfırdan `createRadialGradient` çağırıyordu. ~120 ışık × 60 kare = saniyede binlerce blur/gradyan hesabı. Ayrıca animasyonun **hiçbir durma koşulu yoktu**: hero yukarı kaydırılıp gözden kaybolsa da, sekme arka plana alınsa da sonsuza kadar çalışıyordu.

**Çözüm (iki parça, görünüm birebir korunarak):**
1. **Damga (sprite) önbelleği:** Her renk için ışık görseli **bir kez** küçük bir offscreen canvas'a çizilip, karelerde yalnızca `drawImage` ile ölçeklenmiş kopyası basılıyor. `shadowBlur` ve kare-başına gradyan üretimi tamamen kalktı.
2. **Görünürlük denetimi:** Animasyon artık yalnızca hero ekrandayken **ve** sekme önplandayken çalışıyor (`IntersectionObserver` + `visibilitychange`). Gerçek kullanıcıda boşuna CPU/pil tüketimi de böylece bitti.

**Sonuç (yerel, 3'er ölçümün medyanı):**

| | Önce | Sonra |
|---|---|---|
| Masaüstü | 65 (TBT 40.243 ms) | **98** (TBT 0 ms, LCP 1.06s) |
| Mobil | — | **98** (TBT 0 ms, LCP 2.32s) |

**Banner kalitesi kararı:** Masaüstü artık 98 olduğu ve görsel boyutu puanı neredeyse etkilemediği için kaliteyi yükseltmek serbestti. Kalite/boyut eğrisi ölçüldü ve **q90 (367 KB)** seçildi; q95'e çıkmak +125 KB'a mal oluyor ama kaynakla ortalama fark 255 üzerinden yalnızca 1.66 → 1.18 iyileşiyor — 2x büyütmede bile gözle ayırt edilemiyor. Kaynak zaten sıkıştırılmış bir JPEG olduğu için belli bir noktadan sonra kazanılacak gerçek detay kalmıyor.

**Doğrulama:**
- Animasyonun durup başladığı headless Chrome'da ölçüldü: hero ekrandayken **60 kare/sn**, ekran dışında **0 kare/sn**, geri dönünce yeniden başlıyor.
- Hero görüntüsü ekran görüntüsüyle kontrol edildi, ışıklar eskisi gibi çiziliyor (canvas piksel analizi: en parlak alfa 245, ışıklı piksel oranı %1.9).
- 6 sayfada varlık bütünlüğü ve konsol temizliği doğrulandı.

**Not:** Hero canvas yalnızca `index.html`'de var, diğer sayfalar bu maliyetten zaten etkilenmiyordu.

## 0i. Ana sayfa hero görselinin kalitesi yükseltildi

**Belirti:** Mobil Lighthouse skoru 96'ya çıktıktan sonra, site sahibi ana sayfadaki hero görselinin (`proje_finans_merkezi`) gözle görülür şekilde kalite kaybettiğini fark etti.

**Kök neden:** Bu görsel, farklı optimizasyon geçişlerinde **üç kez** sıkıştırılmıştı: `optimize-images.js` (jpeg q78) → `make-hero-variants.js` (900w türevleri, webp q80/jpeg q78) → `recompress-banners.js` (Lighthouse geçişinde tam boy webp q72'ye, 900w webp q74'e düşürüldü). Her tur kendi başına makul görünse de üst üste binince kaliteyi fazla düşürmüştü.

**Doğrulama yöntemi:** Kaliteyi düşüren asıl etkenin webp sıkıştırması mı yoksa kaynak fotoğrafın kendisi mi olduğunu ayırt etmek için gökyüzü bölgesinden 2x büyütülmüş kırpmalar karşılaştırıldı: kaynak JPEG'te (q78) de aynı bulut geçiş deseni görüldü — yani gökyüzündeki yumuşak banding kaynağın kendisinde var, webp'nin eklediği bir kusur değil. Asıl kalite farkı bina/ışık gibi keskin kenarlı detaylarda ortaya çıktı.

**Çözüm:** Elde daha iyi bir kaynak olup olmadığı kontrol edildi — `.claude/assets-backup/`'taki yedek daha düşük çözünürlüktü (1448×1086 vs mevcut 1600×1200), yani mevcut JPEG zaten elimizdeki en iyi kaynaktı. Bu kaynaktan üç türev de daha yüksek kalitede yeniden üretildi:
- `proje_finans_merkezi.webp` (masaüstü/1600w): q72 → **q90**
- `proje_finans_merkezi-900.webp` (mobil): q74 → **q88**
- `proje_finans_merkezi-900.jpg` (mobil, jpeg fallback): q78 → **q85**

**Bedel:** Mobil hero görseli 91 KB → 159 KB (+68 KB), masaüstü 190 KB → 367 KB (+177 KB). Bu artış kasıtlı ve kabul edilebilir görüldü çünkü artık bu görselle bant genişliği için yarışan başka bir "High" öncelikli istek yok (bkz. 0h) — tek başına önceliklendirilmiş şekilde yükleniyor.

**Kapsam:** Yalnızca ana sayfanın hero görseline uygulandı; diğer sayfaların alt-öncelikli banner'ları (küçük, daha az öne çıkan sayfa başlıkları) mevcut q72 seviyesinde bırakıldı — orijinal `recompress-banners.js` yorumunda belirtildiği gibi, bunlarda kalite farkı 2x büyütmede bile ayırt edilemiyordu.

**Doğrulama:** Yerelde konsol hatası yok; bina/ışık detayları 2x kırpmada net görünüyor.

## 0h. Font preload'i mobil Lighthouse skorunu 85'ten 58'e düşürdü — geri alındı

**Belirti:** Site sahibi teslim öncesi kendi Chrome DevTools'unda mobil Lighthouse çalıştırdı: Performance **58** (önceki ölçümde 85 idi). Accessibility (98), Best Practices (100), SEO (100) birebir aynı kaldı — bu, sorunun erişilebilirlik/yapısal bir şeyde değil, doğrudan yükleme zamanlamasında olduğunu gösteriyordu.

**Kök neden:** Font self-hosting geçişinde (bkz. 0f) eklenen şu satır:
```html
<link rel="preload" href="assets/fonts/inter-subset.woff2" as="font" type="font/woff2" crossorigin="anonymous"/>
```
Chrome'da `preload as="font"` **"High"** kaynak önceliği alıyor — hero görselindeki `fetchpriority="high"` ile **tam olarak aynı öncelik seviyesinde**. Öncesinde (Google Fonts ile) bu stylesheet `media="print" onload="this.media='all'"` hilesiyle asenkron/düşük öncelikli yükleniyordu ve hero görseliyle hiç bant genişliği yarışına girmiyordu. Font'u kendi sunucumuza alıp preload eklerken, farkında olmadan hero görseliyle **aynı önceliğe sahip ikinci bir "High" istek** yaratılmış oldu. Lighthouse'un mobilde simüle ettiği yavaş bağlantıda bu iki istek sınırlı bant genişliği için yarışıyor, LCP (hero görseli) gecikiyor — Lighthouse performans skoru LCP'ye çok duyarlı olduğu için büyük bir puan kaybına yol açtı.

**Çözüm:** 6 sayfadan da preload satırı kaldırıldı; `@font-face` kuralları (dolayısıyla self-hosting'in asıl kazancı: Google'a bağımlılığın kalkması ve küçültülmüş font dosyaları) olduğu gibi kaldı. Preload olmadan da `font-display: swap` sayesinde metin gecikmeden (önce fallback fontla, Inter gelince onunla) görünmeye devam ediyor — burada LCP elemanı zaten metin değil, hero görseli olduğu için preload'un sağladığı "daha hızlı font swap" faydası kritik değildi, riske değmedi.

**Doğrulama:** Yerelde fontların hâlâ yüklendiği (artık `@font-face` üzerinden, sayfa CSS'i işlenirken doğal akışla), Türkçe harflerin (`ğĞşŞİıçÇöÖüÜ`) her iki fontta da piksel bazında sağlam çizildiği ve konsolda hata olmadığı doğrulandı.

**Ders:** Bir optimizasyon (font'u kendi sunucumuza alma) başka bir optimizasyonu (hero görselinin önceliklendirilmesi) fark edilmeden geride bırakabiliyor — ikisi de "doğru" görünen değişiklikler ama birlikte bant genişliği için yarışıyorlardı. Bundan sonraki performans değişikliklerinde kaynak önceliklerinin (fetchpriority, preload) birbirini yeme ihtimaline ayrıca bakılacak.

## 0g. Referans logoları tamamlandı ve optimize edildi (teslim öncesi son geçiş)

**Site sahibinin yaptığı güncelleme:** `referanslar.html` içindeki 12 firma daha önce logosuz olduğu için yalnızca yazıyla gösteriliyordu; bu firmaların logoları eklendi ve mevcut 12 logo da yenilendi. Kart tasarımı da değiştirildi: logo artık kartın tamamını kaplamak yerine üst kısımda duruyor ve altında firma adı yazıyor (`h-40/h-44`, `flex-col`, logo `max-h-[60%]`).

**Tespit edilen sorun:** Eklenen 25 logonun tamamı **1024×1024 PNG** formatındaydı, toplam **4.15 MB**. Oysa bu logolar kartlarda yaklaşık 100px yükseklikte gösteriliyor — yani her boyutta ~10 kat gereğinden büyük. Bu haliyle yayınlansaydı, referanslar sayfası tek başına 4 MB'ın üzerine çıkacak ve daha önce yapılan tüm performans çalışması (görsel optimizasyonu, font subsetting) fazlasıyla geri verilecekti.

**Çözüm:**
- Orijinal dosyalar depo dışına yedeklendi (`.claude/ref-logos-original/`), böylece git geçmişi 4 MB'lık PNG'lerle kalıcı olarak şişirilmedi.
- 25 logo 320px'e küçültülüp WebP'ye çevrildi (kalite 82; ~100px gösterim için yüksek yoğunluklu ekranlarda bile 3x pay bırakıyor) — `.claude/optimize-ref-logos.js`.
- `referanslar.html` referansları `.webp`'ye çevrildi, kullanılmayan büyük PNG'ler silindi — `.claude/switch-ref-logos.js`.
- İstisna: `ref_dogus.png` zaten 1.3 KB ve şeffaflığı olan küçük bir dosya; WebP karşılığı daha büyük çıktığı için PNG bırakıldı (script bunu otomatik tespit edip PNG'de bıraktı).
- İki logo SVG olarak geldi (`ref_korfez_eta.svg`, `ref_mensatech.svg`, ~1 KB) — ölçeklenebilir ve zaten küçük oldukları için dokunulmadı.

**Sonuç:** Referans logoları **4.15 MB → 134 KB (%97 azalma)**.

**Doğrulama (teslim öncesi tam kontrol):**
- 28 logonun tamamı HTTP 200 dönüyor, tarayıcıda çözülebiliyor (320×320) ve piksel analizinde gerçek içerik taşıyor (boş/düz renk değil).
- 6 sayfada toplam **171 varlık referansı** tek tek denetlendi — kırık bağlantı/eksik dosya **yok**.
- Konsolda hata yok.
- Not: Otomatik denetim `${ref.logo}` ve `${_img(project.image)}` gibi JS şablon değişkenlerini "eksik dosya" olarak işaretledi; bunlar çalışma anında üretilen dinamik yollar, gerçek bir sorun değil. Aynı şekilde "kullanılmayan" görünen WebP'ler de `_img()` fonksiyonuyla çalışma anında `.jpg → .webp` çevrimiyle kullanılıyor; hiçbiri silinmedi.
- `hizmetler.html` ve `projeler.html` içindeki `_img()` fonksiyonunun üstünde duran "referans logolarının webp karşılığı üretilmedi" yorumu artık geçersiz kaldığı için güncellendi.

## 0f. Yazı tipleri kendi sunucumuza alındı (self-hosted, subset)

**Amaç:** Skorlar 85/85'e çıktıktan sonra, tasarımdan hiçbir şey feda etmeden yapılabilecek son temiz iyileştirme. Google Fonts'a olan üçüncü taraf bağımlılığını kaldırmak (2 ayrı origin'e DNS + TLS el sıkışması) ve font yükünü küçültmek.

**Ölçüm (önce):** Google Fonts'un bu site için gerçekte gönderdiği veri ölçüldü — Inter (variable, latin + latin-ext) + JetBrains Mono (latin + latin-ext) = **172 KB**.

**Kritik tuzak — Türkçe karakterler:** Google fontları `latin` ve `latin-ext` diye ikiye bölerek sunuyor ve Türkçe harfler bu ikisine **dağılmış** durumda: `ğ Ğ ş Ş İ` → latin-ext, `ı ç Ç ö Ö ü Ü` → latin. İlk denemede tek alt kümeden subset alındı ve doğrulama scripti `EKSIK: ğĞşŞİ` sonucunu verdi — yani site metinlerinde bu harfler kutu (tofu) olarak görünecekti. Bu yüzden yaklaşım değiştirilip Google Fonts upstream'indeki **bölünmemiş tam variable TTF** kaynak alındı.

**Yapılanlar:**
- Sitedeki 6 HTML dosyası taranarak fiilen kullanılan karakter kümesi çıkarıldı (146 benzersiz karakter) — `.claude/collect-chars.js`.
- Tam variable TTF'ler (Inter 877 KB, JetBrains Mono 187 KB) bu karakter setine subset edildi (`subset-font` / harfbuzz) — `.claude/subset-fonts.js`.
- Inter'in `opsz` (optik boyut) ekseni 18'de sabitlendi: variable eksen verisinin yarısı buradan geliyordu (83 KB → 54 KB). `wght` ekseni serbest bırakıldı, yani 100-900 arası tüm kalınlıklar hâlâ tek dosyadan geliyor.
- JetBrains Mono, kullanılan karakterlerden daha geniş olan **tam Türkçe/ASCII setinde** bırakıldı (37 KB). Gerçekte yalnızca 4 sayfada, birkaç büyük-harf etikette kullanılıyor (hizmetler/projeler'de hiç yok) ve daha agresif subset ~22 KB kazandırırdı; ancak ileride yeni bir etikete farklı bir harf yazıldığında sessizce kutu çıkma riski göze alınmadı.
- 6 sayfada Google'ın Inter+JetBrains stylesheet'i (`<noscript>` yedeği dahil) kaldırıldı; yerine inline `@font-face` (ek istek yok) + Inter için `preload` eklendi — `.claude/selfhost-fonts.js`.
- Material Symbols ikon fontu bilinçli olarak Google'da **bırakıldı** (kullanıcıyla kararlaştırıldı: bu madde kapsam dışı).

**Sonuç:** Font yükü **172 KB → 88 KB** (~%49, 84 KB tasarruf) + `fonts.googleapis.com` ve `fonts.gstatic.com`'a giden Inter/JetBrains istekleri tamamen kalktı (ikon fontu için tek bağlantı kaldı).

**Doğrulama:**
- Font ikili dosyaları üzerinde glif kontrolü: her iki fontta da tüm Türkçe harfler mevcut.
- Tarayıcıda piksel bazlı kontrol (`ğĞşŞİıçÇöÖüÜ` tek tek canvas'a çizilip `.notdef`/boş ile karşılaştırıldı): her iki fontta da hepsi çiziliyor. Not: ilk denenen "glif genişliği" yöntemi monospace fontta yanıltıcı sonuç verdi (JetBrains Mono'da tüm glifler eşit genişlikte olduğu için `.notdef`'ten ayırt edilemiyor) — bu yüzden piksel karşılaştırmasına geçildi.
- Ağ izi: fontlar yerelden geliyor, Inter tek seferde çekiliyor (preload çift indirmeye yol açmıyor).
- Metrik karşılaştırması (öncesi/sonrası): JetBrains Mono birebir aynı; Inter metinleri ~%1-2 daha dar (opsz sabitlemesi + font sürüm farkı). Daralma yönü satır kaymasına yol açmaz, konsolda hata yok.

**Yan doğrulama — galeri:** Bu sırada yerel testte galerinin açılmadığı görüldü. Araştırıldı ve **ortam kısıtı** olduğu kanıtlandı: tarayıcı paneli görüntülenmediğinde sayfa kare üretmiyor, `IntersectionObserver` da render'a bağlı olduğu için hiç tetiklenmiyor (kontrol amaçlı kurulan ikinci bir gözlemci de tetiklenmedi). Kodun doğruluğunu IO'ya bağımlı olmadan kanıtlamak için geçici bir test sayfası yazıldı: modül yüklenmeden önce `IntersectionObserver` silinerek kodun "IO yok → doğrudan başlat" dalı tetiklendi. Sonuç: dinamik `import()`, destructuring ve WebGL canvas oluşturma zincirinin tamamı çalışıyor (canvas 1240×400, yedek kaydırıcı otomatik gizlendi, konsol temiz). Test dosyası sonrasında silindi.

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

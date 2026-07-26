# Toplu Güncelleme Scriptleri

Bu site şablonsuz olduğu için (header/footer/menü 6 dosyada da kopya markup), tekrarlanan bir değişikliği tek tek elle 6 dosyada yapmak yerine **bir kerelik Node/Python scripti** yazıp çalıştırmak hem daha hızlı hem daha az hataya açıktır. Aşağıda proje kökündeki `update.py`–`update5.py` scriptlerinin geçmişte ne yaptığının özeti var — aynı desenin nasıl kullanıldığını görmek için.

## `update.py`
6 sayfada üç değişiklik: (1) ikon-fontu logoyu inline SVG logo ile değiştirdi, (2) mobil "cam menü" `<style>`/JS bloğunu düzeltilmiş bir sürümle değiştirdi, (3) `projeler.html`, `referanslar.html`, `hizmetler.html`, `hakkimizda.html`, `iletisim.html`'deki banner konteynerini `h-[240px]...items-end pb-8`'den `h-[320px]...items-center pt-24`'e çıkardı.

## `update2.py`
Yalnızca `referanslar.html`: `referencesData` dizisini Clearbit logo servisine (`logo.clearbit.com`) işaret edecek şekilde değiştirdi (dış bağlantılı, önbelleksiz).

## `update3.py`
27 müşteri logosunu Clearbit'ten indirip `assets/ref_*.png` olarak yerel bir yedek/önbellek oluşturdu (kısa süre sonra update4 tarafından geçersiz kılındı).

## `update4.py`
İki değişiklik: (1) inline SVG logoya `width="36" height="36"` ekledi (CLS/erişilebilirlik düzeltmesi), (2) 27 logoyu bu kez Google favicon servisinden (`google.com/s2/favicons?...&sz=128`) yeniden indirdi ve `referanslar.html`'i yerel `assets/ref_*.png` dosyalarına işaret edecek şekilde güncelledi. Bu yüzden mevcut `ref_*.png` dosyaları küçüktür (289 B – 10 KB) — bunlar 128px favicon'lardır, gerçek logo değil.

## `update5.py`
Son kozmetik geçiş, 6 sayfa: (1) SVG/ikon logoyu tamamen kaldırıp düz metin `<a class="brand">Belis</a>` ile değiştirdi (2026-07-25'teki logo entegrasyonuna kadar bu haliyle kaldı, bkz. [changelog.md](changelog.md)), (2) banner metin hizalamasını tekrar ayarladı, (3) yalnızca `index.html`'de eski bir "ikinci slider"/proje-carousel bloğunu regex ile kaldırmaya çalıştı — bu regex yalnızca kısmen işe yaradı, kalan ölü kod 2026-07-25 optimizasyon geçişinde temizlendi.

## Bu Oturumda Kullanılan Yöntem

2026-07-25 güncellemesinde de aynı yaklaşım izlendi: geçici Node.js scriptleri (proje kökünün dışında, `.claude/` klasöründe) yazılıp bir kerelik çalıştırıldı — ör. logoyu 6 dosyada aynı anda değiştirmek, SEO meta etiketlerini 6 sayfaya eklemek, veya `assets/` altındaki 39 görseli toplu olarak yeniden kodlamak için. Bu scriptler sitenin bir parçası değildir (deploy edilmez), yalnızca değişikliği uygulamak için kullanılan bir kerelik araçlardır.

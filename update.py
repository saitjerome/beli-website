import os
import re

dir_path = r"C:\Users\kağan\Desktop\Son Belis\Belis - Kopya"
files = ["index.html", "hakkimizda.html", "hizmetler.html", "projeler.html", "referanslar.html", "iletisim.html"]

logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" class="w-8 h-8 md:w-10 md:h-10">
          <rect width="64" height="64" rx="14" fill="#003B6F"/>
          <path d="M37 6 14 38h13l-5 20 26-34H33l4-18z" fill="#10B981"/>
        </svg>"""

correct_css = """/* ===== Mobil cam menü ===== */
#mobile-menu { visibility: hidden; }
#mobile-menu .mm-bg { opacity: 0; transition: opacity .3s ease; background: rgba(249,250,251,.72); backdrop-filter: blur(22px); -webkit-backdrop-filter: blur(22px); }
#mobile-menu .mm-item { opacity: 0; transform: translateY(16px); transition: opacity .4s ease, transform .4s ease; }
#mobile-menu.open { visibility: visible; }
#mobile-menu.open .mm-bg { opacity: 1; }
#mobile-menu.open .mm-item { opacity: 1; transform: none; }
#mobile-menu.open .mm-item:nth-child(1) { transition-delay: .18s; }
#mobile-menu.open .mm-item:nth-child(2) { transition-delay: .24s; }
#mobile-menu.open .mm-item:nth-child(3) { transition-delay: .30s; }
#mobile-menu.open .mm-item:nth-child(4) { transition-delay: .36s; }
#mobile-menu.open .mm-item:nth-child(5) { transition-delay: .42s; }
#mobile-menu.open .mm-item:nth-child(6) { transition-delay: .48s; }
#mobile-menu.open .mm-item:nth-child(7) { transition-delay: .54s; }
.mm-link { display: flex; align-items: center; justify-content: space-between; padding: 14px 6px; font-size: 17px; font-weight: 700; color: #1a2733; border-bottom: 1px solid rgba(57,65,71,.1); }
.mm-sub { display: flex; flex-direction: column; max-height: 0; overflow: hidden; transition: max-height .35s ease; }
.mm-sub > a, .mm-sub > button { flex-shrink: 0; }
/* Menü açıkken üst bar üstte kalır; hamburger simgesi yerinde X'e dönüşür */
#close-mm-btn { display: none; }
#mobile-menu .relative > div:first-child { display: none; } /* menü içi eski Belis+X satırı */
#mobile-menu nav { padding-top: 56px; }
body.mm-open #site-header { z-index: 70; }
.mm-sub.open { max-height: 260px; }
.mm-sub a { display: flex; align-items: center; gap: 10px; width: 100%; padding: 12px 8px 12px 18px; font-size: 15px; font-weight: 600; color: #394147; }
.mm-sub .sub-dot { width: 7px; height: 7px; border-radius: 9999px; background: #FF9500; box-shadow: 0 0 0 3px rgba(255,149,0,.18); flex-shrink: 0; }
.mm-chev { transition: transform .3s ease; }
.mm-chev.rot { transform: rotate(180deg); }"""

correct_script = """  // Mobil cam menü
  const menuBtn = document.getElementById('menu-btn');
  const mm = document.getElementById('mobile-menu');
  const closeMmBtn = document.getElementById('close-mm-btn');
  const mmHizBtn = document.getElementById('mm-hizmetler-btn');
  const mmSub = document.getElementById('mm-sub');
  const mmChev = document.getElementById('mm-chev');

  const menuIcon = menuBtn ? menuBtn.querySelector('.material-symbols-outlined') : null;
  function openMm() {
    mm.classList.remove('hidden');
    document.body.classList.add('mm-open');
    if (menuIcon) menuIcon.textContent = 'close';
    if (menuBtn) menuBtn.setAttribute('aria-label', 'Menüyü kapat');
    requestAnimationFrame(() => requestAnimationFrame(() => mm.classList.add('open')));
    document.body.style.overflow = 'hidden';
  }
  function closeMm() {
    mm.classList.remove('open');
    document.body.classList.remove('mm-open');
    if (menuIcon) menuIcon.textContent = 'menu';
    if (menuBtn) menuBtn.setAttribute('aria-label', 'Menüyü aç');
    setTimeout(() => mm.classList.add('hidden'), 400);
    document.body.style.overflow = '';
  }
  if (menuBtn) menuBtn.addEventListener('click', () => {
    if (document.body.classList.contains('mm-open')) closeMm(); else openMm();
  });
  if (closeMmBtn) closeMmBtn.addEventListener('click', closeMm);"""

for file in files:
    path = os.path.join(dir_path, file)
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update logo in header
    content = re.sub(
        r'<span class="material-symbols-outlined text-primary text-\[26px\] md:text-\[34px\] font-bold">blur_on</span>',
        logo_svg,
        content
    )

    # 2. Update CSS
    content = re.sub(
        r'/\* ===== Mobil cam menü ===== \*/.*?(?=/\* ===== iPhone çentik)',
        correct_css + "\\n\\n",
        content,
        flags=re.DOTALL
    )

    # 3. Update Script (only for mobile menu part)
    content = re.sub(
        r'// Mobil cam menü.*?(?=// Footer yılı)',
        correct_script + "\\n\\n  ",
        content,
        flags=re.DOTALL
    )

    # 4. Fix banner overlapping (projeler.html and referanslar.html)
    if file in ["projeler.html", "referanslar.html", "hizmetler.html", "hakkimizda.html", "iletisim.html"]:
        content = re.sub(
            r'class="relative w-full h-\[240px\] md:h-\[340px\] xl:h-\[440px\] flex items-end justify-center overflow-hidden bg-industrial-gray pb-8 md:pb-14"',
            r'class="relative w-full h-[320px] md:h-[400px] xl:h-[480px] flex items-center justify-center overflow-hidden bg-industrial-gray pt-24 pb-8 md:pt-32"',
            content
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Updated all files.")

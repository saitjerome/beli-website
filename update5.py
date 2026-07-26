import os
import re

dir_path = r"C:\Users\kağan\Desktop\Son Belis\Belis - Kopya"
files = ["index.html", "hakkimizda.html", "hizmetler.html", "projeler.html", "referanslar.html", "iletisim.html"]

logo_html = """<a class="brand text-[28px] md:text-[34px] font-extrabold tracking-tighter text-[#003B6F]" href="index.html" style="font-family: 'Inter', sans-serif;">Belis</a>"""

mobile_logo_html = """<span class="text-[28px] font-extrabold tracking-tighter text-[#003B6F]" style="font-family: 'Inter', sans-serif;">Belis</span>"""

for file in files:
    path = os.path.join(dir_path, file)
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix Logo (Header)
    content = re.sub(
        r'<a class="brand[^>]+>.*?<svg[^>]+>.*?</svg>.*?<span[^>]+>Belis</span>\s*</a>',
        logo_html,
        content,
        flags=re.DOTALL
    )
    # Also replace any other variants of the brand tag if they exist
    content = re.sub(
        r'<a class="brand[^>]+>\s*<span class="material-symbols-outlined[^>]+>blur_on</span>\s*<span[^>]+>Belis</span>\s*</a>',
        logo_html,
        content,
        flags=re.DOTALL
    )

    # 2. Fix Logo (Mobile Menu)
    content = re.sub(
        r'<span class="text-2xl font-extrabold text-primary flex items-center gap-2">.*?<svg[^>]+>.*?</svg>\s*Belis\s*</span>',
        mobile_logo_html,
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'<span class="text-2xl font-extrabold text-primary flex items-center gap-2">\s*<span class="material-symbols-outlined[^>]+>blur_on</span>\s*Belis\s*</span>',
        mobile_logo_html,
        content,
        flags=re.DOTALL
    )

    # 3. Fix Banner Text Position
    # Originally I changed it to items-center pt-24 pb-8
    content = re.sub(
        r'class="relative w-full h-\[320px\] md:h-\[400px\] xl:h-\[480px\] flex items-center justify-center overflow-hidden bg-industrial-gray pt-24 pb-8 md:pt-32"',
        r'class="relative w-full h-[320px] md:h-[400px] xl:h-[480px] flex items-end justify-center overflow-hidden bg-industrial-gray pb-12 md:pb-20"',
        content
    )
    # Just in case some files still have the old items-end pb-8 h-[240px]
    content = re.sub(
        r'class="relative w-full h-\[240px\] md:h-\[340px\] xl:h-\[440px\] flex items-end justify-center overflow-hidden bg-industrial-gray pb-8 md:pb-14"',
        r'class="relative w-full h-[320px] md:h-[400px] xl:h-[480px] flex items-end justify-center overflow-hidden bg-industrial-gray pb-12 md:pb-20"',
        content
    )

    # 4. Remove second slider in index.html
    if file == "index.html":
        # Remove prev/next buttons container
        content = re.sub(
            r'<div class="hidden md:flex gap-3 self-end sm:self-auto">.*?</div>',
            '',
            content,
            flags=re.DOTALL
        )
        # Remove project-carousel div entirely
        content = re.sub(
            r'<!-- Kaydırılabilir Proje Kartları \(yedek görünüm\) -->.*?<div id="project-carousel".*?(?=<!-- BİZ KİMİZ -->)',
            '<!-- BİZ KİMİZ -->',
            content,
            flags=re.DOTALL
        )
        # Sometimes the trailing spaces are different, let's use a safer regex for removing the carousel
        content = re.sub(
            r'<!-- Kayd.*?yedek.*?(?=</section>)',
            '',
            content,
            flags=re.DOTALL
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixes applied successfully.")

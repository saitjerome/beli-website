import os
import re
import urllib.request

dir_path = r"C:\Users\kağan\Desktop\Son Belis\Belis - Kopya"
assets_path = os.path.join(dir_path, "assets")
files = ["index.html", "hakkimizda.html", "hizmetler.html", "projeler.html", "referanslar.html", "iletisim.html"]

logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="36" height="36" style="width: 36px; height: 36px; min-width: 36px;">
          <rect width="64" height="64" rx="14" fill="#003B6F"/>
          <path d="M37 6 14 38h13l-5 20 26-34H33l4-18z" fill="#10B981"/>
        </svg>"""

# 1. Fix Logos in all HTML files
for file in files:
    path = os.path.join(dir_path, file)
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the old SVG that lacked explicit width/height
    content = re.sub(
        r'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" class="w-8 h-8 md:w-10 md:h-10">.*?</svg>',
        logo_svg,
        content,
        flags=re.DOTALL
    )
    
    # Replace the mobile menu drawer blur_on text icon
    content = re.sub(
        r'<span class="material-symbols-outlined text-\[28px\]">blur_on</span>',
        logo_svg,
        content
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("HTML Logos fixed.")

# 2. Download Reference Logos from Google Favicon API
logos = {
  "ref_gokyol.png": "gokyol.com.tr",
  "ref_baris_insaat.png": "barisinsaat.com",
  "ref_alperdem.png": "alperdem.com.tr",
  "ref_vardallar.png": "vardallar.com.tr",
  "ref_mapitech.png": "mapitechr.com",
  "ref_mensatech.png": "mensatech.com",
  "ref_akser.png": "akserelektrik.com.tr",
  "ref_dmy.png": "dmy.com.tr",
  "ref_aec.png": "aecmuhendislik.com",
  "ref_delta_mobilya.png": "deltamobilya.com",
  "ref_proje_elektrik.png": "proje-elektrik.com",
  "ref_korfez_eta.png": "korfezeta.com",
  "ref_buyuk_avrupa.png": "buyukavrupa.com.tr",
  "ref_iga.png": "igairport.com",
  "ref_decathlon.png": "decathlon.com.tr",
  "ref_altinbas.png": "altinbas.edu.tr",
  "ref_trendyol.png": "trendyol.com",
  "ref_koc_okullari.png": "koc.k12.tr",
  "ref_ozyegin.png": "ozyegin.edu.tr",
  "ref_witto.png": "wittocoffee.com",
  "ref_akment.png": "akment.com.tr",
  "ref_arcelik.png": "arcelik.com.tr",
  "ref_beko.png": "beko.com.tr",
  "ref_borsa_istanbul.png": "borsaistanbul.com",
  "ref_gama_enerji.png": "gama.com.tr",
  "ref_celebi_konsept.png": "celebikonsept.com",
  "ref_dedeman.png": "dedeman.com",
  "ref_dogus.png": "dogusgrubu.com.tr"
}

req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

for fname, domain in logos.items():
    dest = os.path.join(assets_path, fname)
    url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=5) as response, open(dest, 'wb') as out_file:
            out_file.write(response.read())
        print("Downloaded via Google:", fname)
    except Exception as e:
        print("Failed to download via Google:", fname, str(e))

# 3. Update referanslar.html to use local assets again
ref_path = os.path.join(dir_path, "referanslar.html")
with open(ref_path, 'r', encoding='utf-8') as f:
    ref_content = f.read()

ref_content = re.sub(r'https://logo\.clearbit\.com/[^"]+', lambda m: "assets/" + [k for k,v in logos.items() if m.group(0).endswith(v)][0] if [k for k,v in logos.items() if m.group(0).endswith(v)] else m.group(0), ref_content)

with open(ref_path, 'w', encoding='utf-8') as f:
    f.write(ref_content)

print("referanslar.html updated to use local assets.")


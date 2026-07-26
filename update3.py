import os
import urllib.request

path = r"C:\Users\kağan\Desktop\Son Belis\Belis - Kopya\assets"
if not os.path.exists(path):
    os.makedirs(path)

logos = {
  "ref_gokyol.png": "https://logo.clearbit.com/gokyol.com.tr",
  "ref_baris_insaat.png": "https://logo.clearbit.com/barisinsaat.com",
  "ref_alperdem.png": "https://logo.clearbit.com/alperdem.com.tr",
  "ref_vardallar.png": "https://logo.clearbit.com/vardallar.com.tr",
  "ref_mapitech.png": "https://logo.clearbit.com/mapitechr.com",
  "ref_mensatech.png": "https://logo.clearbit.com/mensatech.com",
  "ref_akser.png": "https://logo.clearbit.com/akserelektrik.com.tr",
  "ref_dmy.png": "https://logo.clearbit.com/dmy.com.tr",
  "ref_aec.png": "https://logo.clearbit.com/aecmuhendislik.com",
  "ref_delta_mobilya.png": "https://logo.clearbit.com/deltamobilya.com",
  "ref_proje_elektrik.png": "https://logo.clearbit.com/proje-elektrik.com",
  "ref_korfez_eta.png": "https://logo.clearbit.com/korfezeta.com",
  "ref_buyuk_avrupa.png": "https://logo.clearbit.com/buyukavrupa.com.tr",
  "ref_iga.png": "https://logo.clearbit.com/igairport.com",
  "ref_decathlon.png": "https://logo.clearbit.com/decathlon.com.tr",
  "ref_altinbas.png": "https://logo.clearbit.com/altinbas.edu.tr",
  "ref_trendyol.png": "https://logo.clearbit.com/trendyol.com",
  "ref_koc_okullari.png": "https://logo.clearbit.com/koc.k12.tr",
  "ref_ozyegin.png": "https://logo.clearbit.com/ozyegin.edu.tr",
  "ref_witto.png": "https://logo.clearbit.com/wittocoffee.com",
  "ref_akment.png": "https://logo.clearbit.com/akment.com.tr",
  "ref_arcelik.png": "https://logo.clearbit.com/arcelik.com.tr",
  "ref_beko.png": "https://logo.clearbit.com/beko.com.tr",
  "ref_borsa_istanbul.png": "https://logo.clearbit.com/borsaistanbul.com",
  "ref_gama_enerji.png": "https://logo.clearbit.com/gama.com.tr",
  "ref_celebi_konsept.png": "https://logo.clearbit.com/celebikonsept.com",
  "ref_dedeman.png": "https://logo.clearbit.com/dedeman.com",
  "ref_dogus.png": "https://logo.clearbit.com/dogusgrubu.com.tr"
}

req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

for fname, url in logos.items():
    dest = os.path.join(path, fname)
    try:
        req = urllib.request.Request(url, headers=req_headers)
        with urllib.request.urlopen(req, timeout=5) as response, open(dest, 'wb') as out_file:
            out_file.write(response.read())
        print("Downloaded:", fname)
    except Exception as e:
        print("Failed:", fname, str(e))


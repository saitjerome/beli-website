import os
import re

path = r"C:\Users\kağan\Desktop\Son Belis\Belis - Kopya\referanslar.html"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the referencesData array directly with updated URLs.
new_data = """const referencesData = [
  { name: "Gökyol İnşaat ve Sanayii A.Ş.",           logo: "https://logo.clearbit.com/gokyol.com.tr" },
  { name: "Barış İnşaat A.Ş.",                       logo: "https://logo.clearbit.com/barisinsaat.com" },
  { name: "Alperdem Elektrik İnşaat Ticaret A.Ş.",   logo: "https://logo.clearbit.com/alperdem.com.tr" },
  { name: "Vardallar Grup",                          logo: "https://logo.clearbit.com/vardallar.com.tr" },
  { name: "Mapitech Mühendislik",                    logo: "https://logo.clearbit.com/mapitechr.com" },
  { name: "Mensatech Mühendislik",                   logo: "https://logo.clearbit.com/mensatech.com" },
  { name: "Akser Elektrik",                          logo: "https://logo.clearbit.com/akserelektrik.com.tr" },
  { name: "DMY Mühendislik",                         logo: "https://logo.clearbit.com/dmy.com.tr" },
  { name: "AEC Mühendislik",                         logo: "https://logo.clearbit.com/aecmuhendislik.com" },
  { name: "Delta Mobilya",                           logo: "https://logo.clearbit.com/deltamobilya.com" },
  { name: "Proje Elektrik",                          logo: "https://logo.clearbit.com/proje-elektrik.com" },
  { name: "Körfez Eta Mühendislik",                  logo: "https://logo.clearbit.com/korfezeta.com" },
  { name: "Büyük Avrupa İnşaat",                     logo: "https://logo.clearbit.com/buyukavrupa.com.tr" },
  { name: "İGA İstanbul Havalimanı",                 logo: "https://logo.clearbit.com/igairport.com" },
  { name: "Decathlon Akmerkez",                      logo: "https://logo.clearbit.com/decathlon.com.tr" },
  { name: "Altınbaş Üniversitesi Gayrettepe Kampüs", logo: "https://logo.clearbit.com/altinbas.edu.tr" },
  { name: "Trendyol.com Maslak",                     logo: "https://logo.clearbit.com/trendyol.com" },
  { name: "Koç Ortaokulu Beykoz",                    logo: "https://logo.clearbit.com/koc.k12.tr" },
  { name: "Özyeğin Üniversitesi",                    logo: "https://logo.clearbit.com/ozyegin.edu.tr" },
  { name: "Witto Coffee",                            logo: "https://logo.clearbit.com/wittocoffee.com" },
  { name: "Akment Alüminyum Geri Dönüşüm",           logo: "https://logo.clearbit.com/akment.com.tr" },
  { name: "Arçelik",                                 logo: "https://logo.clearbit.com/arcelik.com.tr" },
  { name: "Beko",                                    logo: "https://logo.clearbit.com/beko.com.tr" },
  { name: "Borsa İstanbul",                          logo: "https://logo.clearbit.com/borsaistanbul.com" },
  { name: "Gama Enerji — Çakırlar HES",              logo: "https://logo.clearbit.com/gama.com.tr" },
  { name: "Çelebi Konsept Mimarlık",                 logo: "https://logo.clearbit.com/celebikonsept.com" },
  { name: "Dedeman Hotels & Resorts",                logo: "https://logo.clearbit.com/dedeman.com" },
  { name: "Doğuş Group",                             logo: "https://logo.clearbit.com/dogusgrubu.com.tr" }
];"""

content = re.sub(
    r'const referencesData = \[.*?\];',
    new_data,
    content,
    flags=re.DOTALL
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated referanslar.html logos")

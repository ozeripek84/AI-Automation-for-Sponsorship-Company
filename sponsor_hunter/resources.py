"""Küratörlü ek kanallar — otomatik ATS taramasının DIŞINDA, elle kullanılacak.

Bunlar Instagram/YouTube "yoruma yaz link göndereyim" hunilerinden DEĞİL;
gerçek, doğrulanmış kanallar. Özellikle işe alım ajansları önemli: soğuk
başvurudan çok daha etkili, çünkü senin adına aktif eşleştirme yapıyorlar.
"""

# Hollanda işe alım / staffing ajansları.
# fit: bu ailenin (Özer=DS/ML, Kateryna=analist/finans) profiline uygunluk.
NL_RECRUITERS = [
    {"name": "Undutchables", "url": "https://www.undutchables.nl",
     "fit": "YÜKSEK", "note": "İngilizce/çok dilli beyaz yaka (finans, data, ofis). Kateryna için birebir; Özer için de uygun."},
    {"name": "Abroad Experience", "url": "https://www.abroad-experience.com",
     "fit": "YÜKSEK", "note": "Uluslararası/çok dilli işe alım (finans, ticaret, destek)."},
    {"name": "Upforce", "url": "https://www.upforce.com/en",
     "fit": "ORTA", "note": "Uluslararası işe alım, teknik roller de var."},
    {"name": "Start People International", "url": "https://www.startpeople.nl/en/international-recruitment",
     "fit": "ORTA", "note": "Geniş staffing; uluslararası masası var."},
    {"name": "Otto Work Force", "url": "https://ottoworkforce.nl",
     "fit": "DÜŞÜK", "note": "Çoğunlukla lojistik/üretim/mavi yaka — profilinize daha az uygun."},
    {"name": "Manschap", "url": "https://manschap.com", "fit": "DÜŞÜK", "note": "Teknik/endüstriyel."},
    {"name": "Exiva", "url": "https://exiva.nl", "fit": "DÜŞÜK", "note": "Genel staffing."},
    {"name": "PAM Solutions", "url": "https://pamsolutions.nl", "fit": "DÜŞÜK", "note": "Genel staffing."},
    {"name": "Tecline", "url": "https://tecline.com", "fit": "DÜŞÜK", "note": "Teknik/endüstriyel."},
]

# Expat/İngilizce iş panoları — sponsor-dostu ilanların çok olduğu yerler.
JOB_BOARDS = [
    {"name": "IamExpat Jobs", "url": "https://www.iamexpat.nl/career/jobs-netherlands",
     "note": "İngilizce, HSM/sponsor-dostu. 'data' / 'analyst' filtrele."},
    {"name": "Welcome to NL — Jobs", "url": "https://www.welcome-to-nl.nl/jobs",
     "note": "Uluslararası çalışanlara yönelik."},
    {"name": "Indeed NL", "url": "https://nl.indeed.com",
     "note": "Arama: 'visa sponsorship' veya 'relocation'."},
    {"name": "LinkedIn Jobs", "url": "https://www.linkedin.com/jobs",
     "note": "Filtre: lokasyon NL/UK + 'sponsorship'. Recruiter'a doğrudan ulaş."},
]

# Bu araçla otomatik değil, ama işe yarayan doğrulanmış taktikler.
TACTICS = [
    "Avrupa formatı CV kullan (fotoğrafsız, 1-2 sayfa, ATS-dostu, anahtar kelimeli).",
    "CV + cover letter + LinkedIn üçü de birbirini tutmalı (aynı unvan, aynı hikaye).",
    "İlan aramada 'visa sponsorship' / 'relocation support' anahtar kelimelerini kullan.",
    "ASLA iş/vize için peşin büyük para verme. Meşru ajans senden ücret almaz (işveren öder).",
    "Ajanslara kaydol: CV'ni bırak, LinkedIn'de bağlan. Onlar seni aktif eşleştirir — soğuk başvurudan iyidir.",
]


def render():
    lines = []
    lines.append("=" * 64)
    lines.append("EK KANALLAR — otomatik taramanın dışında, elle kullan")
    lines.append("=" * 64)
    lines.append("\n## Hollanda işe alım ajansları (CV bırak, seni eşleştirsinler)")
    for r in NL_RECRUITERS:
        lines.append(f"  [{r['fit']:>5}] {r['name']}  —  {r['url']}")
        lines.append(f"          {r['note']}")
    lines.append("\n## İngilizce / expat iş panoları")
    for b in JOB_BOARDS:
        lines.append(f"  • {b['name']}  —  {b['url']}")
        lines.append(f"          {b['note']}")
    lines.append("\n## İşe yarayan taktikler")
    for t in TACTICS:
        lines.append(f"  • {t}")
    lines.append("\nNot: 'yoruma yaz link göndereyim' Instagram hesapları HUNİDİR —")
    lines.append("      sana zaten elinde olan resmi IND listesini gizli liste diye pazarlar.")
    return "\n".join(lines)

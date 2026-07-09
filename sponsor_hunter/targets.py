"""Öncelikli hedef şirketler.

Veri/AI alanında yoğun işe alım yapan ve vize sponsorluğu geçmişi bilinen
şirketler. "slugs" alanı ATS (başvuru sistemi) API'lerinde denenecek
adaylardır; jobs.py bunları doğrular. ATS'i tespit edilemeyen şirketler
"manual" olarak kariyer sayfası linkiyle raporlanır.

Kendi hedefini eklemek için: python3 run.py add-target "Şirket" NL --careers URL
"""
import json

from .config import DATA

CUSTOM_TARGETS = DATA / "custom_targets.json"

TARGETS = [
    # ---------------- HOLLANDA (hepsi IND tanınmış sponsor) ----------------
    {"name": "Adyen", "country": "NL", "slugs": ["adyen"], "careers": "https://careers.adyen.com"},
    {"name": "Mollie", "country": "NL", "slugs": ["mollie"], "careers": "https://jobs.mollie.com"},
    {"name": "Picnic", "country": "NL", "slugs": ["picnic", "picnictechnologies"], "careers": "https://picnic.app/careers"},
    {"name": "Booking.com", "country": "NL", "slugs": ["booking", "bookingcom"], "careers": "https://jobs.booking.com"},
    {"name": "TomTom", "country": "NL", "slugs": ["tomtom"], "careers": "https://www.tomtom.com/careers"},
    {"name": "ASML", "country": "NL", "slugs": ["asml"], "careers": "https://www.asml.com/en/careers"},
    {"name": "Philips", "country": "NL", "slugs": ["philips"], "careers": "https://www.careers.philips.com"},
    {"name": "NXP Semiconductors", "country": "NL", "slugs": ["nxp"], "careers": "https://careers.nxp.com"},
    {"name": "ING", "country": "NL", "slugs": ["ing"], "careers": "https://www.ing.jobs"},
    {"name": "ABN AMRO", "country": "NL", "slugs": ["abnamro"], "careers": "https://www.werkenbijabnamro.nl/en"},
    {"name": "Rabobank", "country": "NL", "slugs": ["rabobank"], "careers": "https://rabobank.jobs/en"},
    {"name": "KLM", "country": "NL", "slugs": ["klm"], "careers": "https://careers.klm.com"},
    {"name": "Ahold Delhaize", "country": "NL", "slugs": ["aholddelhaize", "ahold"], "careers": "https://careers.aholddelhaize.com"},
    {"name": "bol.com", "country": "NL", "slugs": ["bol", "bolcom"], "careers": "https://careers.bol.com"},
    {"name": "Coolblue", "country": "NL", "slugs": ["coolblue"], "careers": "https://careersatcoolblue.com"},
    {"name": "Just Eat Takeaway", "country": "NL", "slugs": ["justeattakeaway", "takeaway"], "careers": "https://careers.justeattakeaway.com"},
    {"name": "Elastic", "country": "NL", "slugs": ["elastic"], "careers": "https://www.elastic.co/careers"},
    {"name": "Databricks", "country": "NL", "slugs": ["databricks"], "careers": "https://www.databricks.com/company/careers"},
    {"name": "Miro", "country": "NL", "slugs": ["miro", "realtimeboard"], "careers": "https://miro.com/careers"},
    {"name": "Uber (Amsterdam)", "country": "NL", "slugs": ["uber"], "careers": "https://www.uber.com/careers"},
    {"name": "Catawiki", "country": "NL", "slugs": ["catawiki"], "careers": "https://jobs.catawiki.com"},
    {"name": "Backbase", "country": "NL", "slugs": ["backbase"], "careers": "https://jobs.backbase.com"},
    {"name": "WeTransfer", "country": "NL", "slugs": ["wetransfer"], "careers": "https://wetransfer.com/jobs"},
    {"name": "Framer", "country": "NL", "slugs": ["framer"], "careers": "https://www.framer.com/careers"},
    {"name": "bunq", "country": "NL", "slugs": ["bunq"], "careers": "https://www.bunq.com/jobs"},
    {"name": "Bird (MessageBird)", "country": "NL", "slugs": ["messagebird", "bird"], "careers": "https://bird.com/careers"},
    {"name": "Optiver", "country": "NL", "slugs": ["optiver"], "careers": "https://optiver.com/working-at-optiver"},
    {"name": "IMC Trading", "country": "NL", "slugs": ["imc"], "careers": "https://careers.imc.com"},
    {"name": "Flow Traders", "country": "NL", "slugs": ["flowtraders"], "careers": "https://www.flowtraders.com/careers"},
    {"name": "Vanderlande", "country": "NL", "slugs": ["vanderlande"], "careers": "https://careers.vanderlande.com"},
    {"name": "Wolters Kluwer", "country": "NL", "slugs": ["wolterskluwer"], "careers": "https://careers.wolterskluwer.com"},
    {"name": "Elsevier (RELX)", "country": "NL", "slugs": ["elsevier", "relx"], "careers": "https://careers.relx.com"},
    {"name": "Nike EHQ (Hilversum)", "country": "NL", "slugs": ["nike"], "careers": "https://careers.nike.com"},
    {"name": "Heineken", "country": "NL", "slugs": ["heineken"], "careers": "https://careers.theheinekencompany.com"},
    {"name": "KPN", "country": "NL", "slugs": ["kpn"], "careers": "https://jobs.kpn.com"},
    {"name": "Randstad Digital", "country": "NL", "slugs": ["randstad"], "careers": "https://www.randstaddigital.com/careers"},
    {"name": "Exact", "country": "NL", "slugs": ["exact"], "careers": "https://www.exact.com/careers"},
    {"name": "Prosus", "country": "NL", "slugs": ["prosus"], "careers": "https://www.prosus.com/careers"},
    {"name": "eBay Marktplaats", "country": "NL", "slugs": ["marktplaats", "ebay"], "careers": "https://jobs.ebayinc.com"},
    {"name": "DEPT", "country": "NL", "slugs": ["dept", "deptagency"], "careers": "https://www.deptagency.com/careers"},

    # ---------------- İNGİLTERE (Skilled Worker lisanslı) ----------------
    {"name": "Monzo", "country": "UK", "slugs": ["monzo"], "careers": "https://monzo.com/careers"},
    {"name": "Wise", "country": "UK", "slugs": ["transferwise", "wise"], "careers": "https://wise.jobs"},
    {"name": "Revolut", "country": "UK", "slugs": ["revolut"], "careers": "https://www.revolut.com/careers"},
    {"name": "Deliveroo", "country": "UK", "slugs": ["deliveroo"], "careers": "https://careers.deliveroo.co.uk"},
    {"name": "Checkout.com", "country": "UK", "slugs": ["checkout", "checkoutcom"], "careers": "https://www.checkout.com/careers"},
    {"name": "Starling Bank", "country": "UK", "slugs": ["starlingbank", "starling"], "careers": "https://www.starlingbank.com/careers"},
    {"name": "Ocado Technology", "country": "UK", "slugs": ["ocado", "ocadogroup"], "careers": "https://careers.ocadogroup.com"},
    {"name": "Snyk", "country": "UK", "slugs": ["snyk"], "careers": "https://snyk.io/careers"},
    {"name": "Quantexa", "country": "UK", "slugs": ["quantexa"], "careers": "https://www.quantexa.com/careers"},
    {"name": "Darktrace", "country": "UK", "slugs": ["darktrace"], "careers": "https://www.darktrace.com/careers"},
    {"name": "Faculty AI", "country": "UK", "slugs": ["faculty", "facultyai"], "careers": "https://faculty.ai/careers"},
    {"name": "Improbable", "country": "UK", "slugs": ["improbable"], "careers": "https://www.improbable.io/careers"},
    {"name": "Google DeepMind", "country": "UK", "slugs": ["deepmind"], "careers": "https://deepmind.google/about/careers"},
    {"name": "AstraZeneca", "country": "UK", "slugs": ["astrazeneca"], "careers": "https://careers.astrazeneca.com"},
    {"name": "GSK", "country": "UK", "slugs": ["gsk"], "careers": "https://jobs.gsk.com"},
    {"name": "Barclays", "country": "UK", "slugs": ["barclays"], "careers": "https://search.jobs.barclays"},
    {"name": "HSBC", "country": "UK", "slugs": ["hsbc"], "careers": "https://www.hsbc.com/careers"},
    {"name": "Lloyds Banking Group", "country": "UK", "slugs": ["lloyds"], "careers": "https://www.lloydsbankinggrouptalent.com"},
    {"name": "Sky", "country": "UK", "slugs": ["sky"], "careers": "https://careers.sky.com"},
    {"name": "Trainline", "country": "UK", "slugs": ["trainline"], "careers": "https://www.thetrainline.com/careers"},
    {"name": "Zopa", "country": "UK", "slugs": ["zopa"], "careers": "https://www.zopa.com/careers"},
    {"name": "Lendable", "country": "UK", "slugs": ["lendable"], "careers": "https://www.lendable.co.uk/careers"},

    # ---------------- İSVİÇRE (kamu sponsor listesi yok — kotalı sistem) ----------------
    {"name": "Google Zürich", "country": "CH", "slugs": ["google"], "careers": "https://www.google.com/about/careers/applications/locations/zurich"},
    {"name": "UBS", "country": "CH", "slugs": ["ubs"], "careers": "https://www.ubs.com/global/en/careers"},
    {"name": "Swiss Re", "country": "CH", "slugs": ["swissre"], "careers": "https://careers.swissre.com"},
    {"name": "Zurich Insurance", "country": "CH", "slugs": ["zurichinsurance", "zurich"], "careers": "https://www.zurich.com/careers"},
    {"name": "Roche", "country": "CH", "slugs": ["roche"], "careers": "https://careers.roche.com"},
    {"name": "Novartis", "country": "CH", "slugs": ["novartis"], "careers": "https://www.novartis.com/careers"},
    {"name": "Nestlé", "country": "CH", "slugs": ["nestle"], "careers": "https://www.nestle.com/jobs"},
    {"name": "Proton", "country": "CH", "slugs": ["proton", "protonag", "protonmail"], "careers": "https://proton.me/careers"},
    {"name": "SonarSource", "country": "CH", "slugs": ["sonarsource", "sonar"], "careers": "https://www.sonarsource.com/company/jobs"},
    {"name": "DFINITY", "country": "CH", "slugs": ["dfinity"], "careers": "https://dfinity.org/careers"},
    {"name": "Climeworks", "country": "CH", "slugs": ["climeworks"], "careers": "https://climeworks.com/careers"},
    {"name": "On (On Running)", "country": "CH", "slugs": ["on", "onrunning"], "careers": "https://www.on.com/en-ch/careers"},
    {"name": "Frontify", "country": "CH", "slugs": ["frontify"], "careers": "https://www.frontify.com/en/careers"},

    # ---------------- LÜKSEMBURG (EU Blue Card / çalışma izni işveren üzerinden) ----------------
    {"name": "Amazon Luxembourg", "country": "LU", "slugs": ["amazon"], "careers": "https://www.amazon.jobs/en/locations/luxembourg"},
    {"name": "PayPal Luxembourg", "country": "LU", "slugs": ["paypal"], "careers": "https://careers.pypl.com"},
    {"name": "European Investment Bank", "country": "LU", "slugs": ["eib"], "careers": "https://www.eib.org/en/about/jobs"},
    {"name": "Clearstream (Deutsche Börse)", "country": "LU", "slugs": ["deutscheboerse", "clearstream"], "careers": "https://careers.deutsche-boerse.com"},
    {"name": "BGL BNP Paribas", "country": "LU", "slugs": ["bnpparibas"], "careers": "https://group.bnpparibas/en/careers"},
    {"name": "POST Luxembourg", "country": "LU", "slugs": ["postluxembourg"], "careers": "https://www.postgroup.lu/en/jobs"},
    {"name": "Talkwalker", "country": "LU", "slugs": ["talkwalker"], "careers": "https://www.talkwalker.com/careers"},
    {"name": "Ferrero (HQ)", "country": "LU", "slugs": ["ferrero"], "careers": "https://www.ferrerocareers.com"},
    {"name": "SES Satellites", "country": "LU", "slugs": ["ses"], "careers": "https://www.ses.com/careers"},
]


def load_targets():
    targets = list(TARGETS)
    if CUSTOM_TARGETS.exists():
        targets += json.loads(CUSTOM_TARGETS.read_text(encoding="utf-8"))
    return targets


def add_target(name, country, careers="", slugs=None):
    custom = []
    if CUSTOM_TARGETS.exists():
        custom = json.loads(CUSTOM_TARGETS.read_text(encoding="utf-8"))
    if not slugs:
        base = "".join(ch for ch in name.lower() if ch.isalnum())
        slugs = [base]
    custom.append({"name": name, "country": country.upper(), "slugs": slugs, "careers": careers})
    CUSTOM_TARGETS.write_text(json.dumps(custom, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Eklendi: {name} ({country}) — slug adayları: {slugs}")

"""İlan METNİNİ okuyup sponsorluk sinyali arar.

Bir IND/Home Office sponsoru şirket bile her rolü sponsor etmez. İlan
açıklamasında "visa sponsorship" / "relocation" geçiyorsa o rolde sponsorluk
ihtimali yüksek; "must have the right to work" geçiyorsa büyük ihtimalle YOK.

Bu modül mevcut tracker ilanlarını zenginleştirir: her ilana
  evet    → metin sponsorluk/relokasyon vaat ediyor  (ÖNCELİK VER)
  hayır   → metin "çalışma iznin olmalı / sponsor etmiyoruz" diyor  (BOŞ VER)
  belirsiz→ metinde net sinyal yok
etiketini ekler.
"""
import time

import requests

from .config import HEADERS
from . import jobs as jobs_mod

POSITIVE = [
    "visa sponsorship", "sponsor your visa", "we sponsor", "will sponsor",
    "willing to sponsor", "sponsorship available", "sponsorship is available",
    "visa support", "provide sponsorship", "offer sponsorship", "can sponsor",
    "relocation package", "relocation support", "relocation assistance",
    "relocation bonus", "relocation allowance", "highly skilled migrant",
    "kennismigrant", "30% ruling", "skilled worker visa", "immigration support",
    "sponsor a visa", "visa and relocation", "we offer visa",
]
NEGATIVE = [
    "unable to sponsor", "cannot sponsor", "can not sponsor", "not able to sponsor",
    "no visa sponsorship", "do not sponsor", "does not sponsor", "not sponsor visa",
    "no sponsorship", "without sponsorship", "not provide sponsorship",
    "not able to provide visa", "must already have the right to work",
    "must have the right to work", "existing right to work",
    "already have the right to work", "no relocation",
]


def classify(text):
    if not text:
        return "belirsiz"
    t = text.lower()
    if any(k in t for k in NEGATIVE):
        return "hayır"
    if any(k in t for k in POSITIVE):
        return "evet"
    return "belirsiz"


# --- Açıklamayı ATS'e göre en iyi çabayla çek --------------------------------

def _descs_greenhouse(slug, timeout):
    # ?content=true tek çağrıda tüm ilanların HTML içeriğini verir
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    data = jobs_mod._get_json(url, timeout) or {}
    out = {}
    for j in data.get("jobs", []):
        out[j.get("absolute_url", "")] = j.get("content", "") or ""
    return out


def _descs_lever(slug, timeout):
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    data = jobs_mod._get_json(url, timeout) or []
    out = {}
    for j in data:
        out[j.get("hostedUrl", "")] = (j.get("descriptionPlain") or j.get("description") or "")
    return out


def _descs_recruitee(slug, timeout):
    url = f"https://{slug}.recruitee.com/api/offers/"
    data = jobs_mod._get_json(url, timeout) or {}
    out = {}
    for j in data.get("offers", []):
        key = j.get("careers_url", "") or f"https://{slug}.recruitee.com/o/{j.get('slug','')}"
        out[key] = j.get("description", "") or ""
    return out


def _descs_ashby(slug, timeout):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    data = jobs_mod._get_json(url, timeout) or {}
    out = {}
    for j in data.get("jobs", []):
        out[j.get("jobUrl", "") or j.get("applyUrl", "")] = (
            j.get("descriptionPlain") or j.get("description") or "")
    return out


DESC_FETCHERS = {
    "greenhouse": _descs_greenhouse,
    "lever": _descs_lever,
    "recruitee": _descs_recruitee,
    "ashby": _descs_ashby,
    # workable: widget açıklama vermiyor → belirsiz kalır
}


def enrich(df, timeout=15, delay=0.15, only_new=True):
    """Tracker DataFrame'ini sponsorship sütunuyla zenginleştir."""
    cache = jobs_mod._load_cache()
    rows = df[df["status"] == "yeni"] if only_new else df
    companies = rows["company"].unique()
    desc_by_url = {}

    for i, company in enumerate(companies, 1):
        entry = cache.get(company)
        if not entry or entry.get("ats") == "none":
            continue
        ats, slug = entry["ats"], entry["slug"]
        fetcher = DESC_FETCHERS.get(ats)
        if not fetcher:
            continue
        print(f"  [{i}/{len(companies)}] {company} ({ats}) açıklamalar okunuyor...", flush=True)
        try:
            desc_by_url.update(fetcher(slug, timeout))
        except (requests.RequestException, ValueError):
            pass
        time.sleep(delay)

    n_evet = n_hayir = 0
    for idx, row in df.iterrows():
        if only_new and row["status"] != "yeni":
            continue
        desc = desc_by_url.get(row["url"], "")
        label = classify(desc)
        df.at[idx, "sponsorship"] = label
        n_evet += label == "evet"
        n_hayir += label == "hayır"
    print(f"\n✓ Sponsorluk sinyali: {n_evet} ilan 'evet', {n_hayir} ilan 'hayır' olarak işaretlendi.")
    return df

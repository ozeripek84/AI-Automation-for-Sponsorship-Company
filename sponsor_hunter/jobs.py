"""Hedef şirketlerin ATS (başvuru sistemi) API'lerinden açık pozisyonları çeker.

Desteklenen ATS'ler (hepsi halka açık, anahtar gerektirmeyen JSON API'ler):
  - Greenhouse : boards-api.greenhouse.io/v1/boards/{slug}/jobs
  - Lever      : api.lever.co/v0/postings/{slug}?mode=json
  - Recruitee  : {slug}.recruitee.com/api/offers/   (Hollanda'da çok yaygın)
  - Ashby      : api.ashbyhq.com/posting-api/job-board/{slug}
  - Workable   : apply.workable.com/api/v1/widget/accounts/{slug}

Şirketin hangi ATS'i kullandığı bilinmediğinden slug adayları sırayla denenir;
ilk çalışan ATS kullanılır ve data/ats_cache.json'a kaydedilir (sonraki
çalıştırmalar hızlıdır).
"""
import json
import time

import requests

from .config import DATA, HEADERS, load_config

ATS_CACHE = DATA / "ats_cache.json"


def _get_json(url, timeout):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except (requests.RequestException, ValueError):
        pass
    return None


# --- Her ATS için: (url_kalibi, parse_fonksiyonu) ---------------------------

def _parse_greenhouse(data, slug):
    for j in (data or {}).get("jobs", []):
        yield {"title": j.get("title", ""),
               "location": (j.get("location") or {}).get("name", ""),
               "url": j.get("absolute_url", "")}


def _parse_lever(data, slug):
    for j in data or []:
        yield {"title": j.get("text", ""),
               "location": (j.get("categories") or {}).get("location", "") or "",
               "url": j.get("hostedUrl", "")}


def _parse_recruitee(data, slug):
    for j in (data or {}).get("offers", []):
        yield {"title": j.get("title", ""),
               "location": j.get("location", "") or j.get("city", "") or "",
               "url": j.get("careers_url", "") or f"https://{slug}.recruitee.com/o/{j.get('slug','')}"}


def _parse_ashby(data, slug):
    for j in (data or {}).get("jobs", []):
        yield {"title": j.get("title", ""),
               "location": j.get("location", "") or "",
               "url": j.get("jobUrl", "") or j.get("applyUrl", "")}


def _parse_workable(data, slug):
    for j in (data or {}).get("jobs", []):
        loc = j.get("location") or {}
        city = loc.get("city", "") if isinstance(loc, dict) else ""
        country = loc.get("country", "") if isinstance(loc, dict) else ""
        yield {"title": j.get("title", ""),
               "location": ", ".join(x for x in (city, country) if x),
               "url": j.get("url", "") or j.get("shortlink", "")}


ATS_PROVIDERS = [
    ("greenhouse", "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", _parse_greenhouse),
    ("lever", "https://api.lever.co/v0/postings/{slug}?mode=json", _parse_lever),
    ("recruitee", "https://{slug}.recruitee.com/api/offers/", _parse_recruitee),
    ("ashby", "https://api.ashbyhq.com/posting-api/job-board/{slug}", _parse_ashby),
    ("workable", "https://apply.workable.com/api/v1/widget/accounts/{slug}", _parse_workable),
]


def _load_cache():
    if ATS_CACHE.exists():
        return json.loads(ATS_CACHE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache):
    ATS_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def discover_ats(target, delay, timeout, cache):
    """Şirketin çalışan ATS endpoint'ini bul. Dönen: (ats_adi, slug, jobs_list) | None"""
    key = target["name"]
    if key in cache:
        entry = cache[key]
        if entry.get("ats") == "none":
            return None
        ats_name, slug = entry["ats"], entry["slug"]
        url_tpl, parser = next((u, p) for n, u, p in ATS_PROVIDERS if n == ats_name)
        data = _get_json(url_tpl.format(slug=slug), timeout)
        if data is not None:
            return ats_name, slug, list(parser(data, slug))
        # cache bayatlamış — yeniden keşfet
    for slug in target.get("slugs", []):
        for ats_name, url_tpl, parser in ATS_PROVIDERS:
            data = _get_json(url_tpl.format(slug=slug), timeout)
            time.sleep(delay)
            if data is None:
                continue
            jobs = list(parser(data, slug))
            if jobs:
                cache[key] = {"ats": ats_name, "slug": slug}
                return ats_name, slug, jobs
    cache[key] = {"ats": "none"}
    return None


def _match_location(location, country, cfg):
    loc = (location or "").lower()
    if not loc or "remote" in loc:
        return cfg.get("include_remote", True)
    return any(term.lower() in loc for term in cfg["locations"].get(country, []))


def _match_profile(title, profile_cfg):
    t = title.lower()
    if any(x.lower() in t for x in profile_cfg.get("exclude_keywords", [])):
        return False
    return any(k.lower() in t for k in profile_cfg["keywords"])


def scan(targets, countries=None, progress=True):
    """Tüm hedefleri tara; profil-eşleşen ilanları ve ATS'siz şirketleri döndür."""
    cfg = load_config()
    delay = cfg.get("request_delay", 0.15)
    timeout = cfg.get("request_timeout", 12)
    countries = countries or cfg["countries"]
    cache = _load_cache()

    matches, manual_companies = [], []
    targets = [t for t in targets if t["country"] in countries]
    for i, target in enumerate(targets, 1):
        if progress:
            print(f"  [{i}/{len(targets)}] {target['name']} ({target['country']})...", end=" ", flush=True)
        found = discover_ats(target, delay, timeout, cache)
        if found is None:
            manual_companies.append(target)
            if progress:
                print("ATS bulunamadı -> manuel liste")
            continue
        ats_name, slug, jobs = found
        n_matched = 0
        for job in jobs:
            if not _match_location(job["location"], target["country"], cfg):
                continue
            for profile_name, profile_cfg in cfg["profiles"].items():
                if _match_profile(job["title"], profile_cfg):
                    matches.append({
                        "profile": profile_name,
                        "company": target["name"],
                        "country": target["country"],
                        "title": job["title"],
                        "location": job["location"],
                        "url": job["url"],
                        "ats": ats_name,
                        "careers": target.get("careers", ""),
                    })
                    n_matched += 1
        if progress:
            print(f"{ats_name}:{slug} — {len(jobs)} ilan, {n_matched} eşleşme")
        _save_cache(cache)
    _save_cache(cache)
    return matches, manual_companies

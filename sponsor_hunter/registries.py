"""Resmi vize sponsoru kayitlarini indirir.

NL — IND Public Register (Work): tanınmış sponsorlar (highly skilled migrant).
UK — Home Office Register of Licensed Sponsors (Worker): Skilled Worker vb.
CH/LU — kamuya açık sponsor listesi YOKTUR; hedef şirket listesi targets.py'da.
"""
import io
import re
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .config import DATA, HEADERS

IND_WORK_URL = "https://ind.nl/en/public-register-recognised-sponsors/public-register-work"
UK_PUBLICATION_URL = "https://www.gov.uk/government/publications/register-of-licensed-sponsors-workers"

NL_CSV = DATA / "nl_sponsors.csv"
UK_CSV = DATA / "uk_sponsors.csv"


def fetch_nl(timeout=60):
    print("[NL] IND tanınmış sponsor listesi indiriliyor...")
    r = requests.get(IND_WORK_URL, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if table is None:
        sys.exit("[NL] HATA: sayfada tablo bulunamadı — IND sayfa yapısı değişmiş olabilir.")
    rows = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) >= 2 and cells[1].lower() != "kvk number":
            rows.append({"organisation": cells[0], "kvk": cells[1]})
    df = pd.DataFrame(rows).drop_duplicates()
    df.to_csv(NL_CSV, index=False)
    print(f"[NL] {len(df)} sponsor kaydedildi -> {NL_CSV.name}")
    return df


def fetch_uk(timeout=120):
    print("[UK] Home Office sponsor listesi için güncel CSV linki aranıyor...")
    r = requests.get(UK_PUBLICATION_URL, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    m = re.search(r'href="(https://[^"]+\.csv)"', r.text)
    if not m:
        sys.exit("[UK] HATA: CSV linki bulunamadı — gov.uk sayfa yapısı değişmiş olabilir.")
    csv_url = m.group(1)
    print(f"[UK] İndiriliyor: {csv_url}")
    r = requests.get(csv_url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), dtype=str, on_bad_lines="skip")
    df.columns = [c.strip().lower().replace(" ", "_").replace("&", "and") for c in df.columns]
    # Sadece Skilled Worker rotası (sponsorlu çalışma vizesi için gereken rota)
    route_col = next((c for c in df.columns if "route" in c), None)
    if route_col:
        df = df[df[route_col].str.contains("Skilled Worker", case=False, na=False)]
    df = df.drop_duplicates()
    df.to_csv(UK_CSV, index=False)
    print(f"[UK] {len(df)} Skilled Worker sponsoru kaydedildi -> {UK_CSV.name}")
    return df


def load_registry(country):
    path = {"NL": NL_CSV, "UK": UK_CSV}.get(country)
    if path and path.exists():
        return pd.read_csv(path, dtype=str)
    return None


def search(name):
    """Bir şirketin resmi sponsor olup olmadığını kontrol et."""
    results = []
    nl = load_registry("NL")
    if nl is not None:
        hits = nl[nl["organisation"].str.contains(name, case=False, na=False)]
        for _, h in hits.iterrows():
            results.append(("NL", h["organisation"], "IND tanınmış sponsor (highly skilled migrant)"))
    uk = load_registry("UK")
    if uk is not None:
        name_col = next((c for c in uk.columns if "organisation" in c or "name" in c), uk.columns[0])
        hits = uk[uk[name_col].str.contains(name, case=False, na=False)]
        for _, h in hits.head(20).iterrows():
            town = h.get("town/city", "") or h.get("town_city", "") or ""
            results.append(("UK", h[name_col], f"Skilled Worker lisanslı sponsor ({town})"))
    return results

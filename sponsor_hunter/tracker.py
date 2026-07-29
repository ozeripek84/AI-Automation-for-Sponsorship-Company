"""Başvuru takip sistemi.

output/tracker.csv — tüm bulunan ilanlar + başvuru durumların.
Yeni taramalar mevcut durumları EZMEZ: aynı ilan tekrar bulunursa statün korunur.

Durum değerleri: yeni | basvuruldu | cevap_bekleniyor | mulakat | red | teklif
Durumu güncellemek için: python3 run.py status <ID> basvuruldu
veya tracker.csv / tracker.xlsx dosyasını elle düzenle (status ve notes sütunları).
"""
import datetime

import pandas as pd

from .config import OUTPUT

TRACKER_CSV = OUTPUT / "tracker.csv"
TRACKER_XLSX = OUTPUT / "tracker.xlsx"

COLUMNS = ["id", "found_date", "profile", "company", "country", "title",
           "location", "url", "ats", "careers", "sponsorship", "status", "notes"]


def load():
    if TRACKER_CSV.exists():
        df = pd.read_csv(TRACKER_CSV, dtype=str).fillna("")
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def save(df):
    df.to_csv(TRACKER_CSV, index=False)
    try:
        df.to_excel(TRACKER_XLSX, index=False)
    except Exception as e:
        print(f"  (Excel yazılamadı: {e} — CSV günceldir)")


def merge(matches):
    """Yeni eşleşmeleri tracker'a ekle; mevcut kayıtların durumunu koru."""
    df = load()
    existing_keys = set(zip(df["profile"], df["company"], df["title"]))
    today = datetime.date.today().isoformat()
    next_id = 1 + max((int(i) for i in df["id"] if str(i).isdigit()), default=0)

    new_rows = []
    for m in matches:
        key = (m["profile"], m["company"], m["title"])
        if key in existing_keys:
            continue
        existing_keys.add(key)
        new_rows.append({
            "id": str(next_id), "found_date": today,
            "profile": m["profile"], "company": m["company"], "country": m["country"],
            "title": m["title"], "location": m.get("location", ""), "url": m.get("url", ""),
            "ats": m.get("ats", ""), "careers": m.get("careers", ""),
            "sponsorship": "", "status": "yeni", "notes": "",
        })
        next_id += 1

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    save(df)
    return df, len(new_rows)


def set_status(job_id, status, note=""):
    df = load()
    mask = df["id"] == str(job_id)
    if not mask.any():
        print(f"ID {job_id} bulunamadı.")
        return
    df.loc[mask, "status"] = status
    if note:
        df.loc[mask, "notes"] = note
    save(df)
    row = df[mask].iloc[0]
    print(f"✓ #{job_id} {row['company']} — {row['title']} -> {status}")

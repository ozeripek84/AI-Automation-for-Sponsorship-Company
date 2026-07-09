#!/usr/bin/env python3
"""Sponsor Şirket Arama Otomasyonu — ana komut.

Kullanım:
  python3 run.py all                 # tam pipeline: listeler + tarama + mektuplar + dashboard
  python3 run.py update              # NL + UK resmi sponsor listelerini indir/güncelle
  python3 run.py jobs                # hedef şirketlerde açık pozisyon tara
  python3 run.py jobs --country NL   # sadece bir ülke
  python3 run.py letters             # 'yeni' durumundaki ilanlara mektup üret
  python3 run.py report              # dashboard.html'i yeniden oluştur
  python3 run.py search "asml"       # şirket resmi sponsor mu? (NL+UK kayıtlarında ara)
  python3 run.py status 12 basvuruldu [not]   # başvuru durumu güncelle
  python3 run.py add-target "Şirket Adı" NL --careers https://... [--slug xyz]
"""
import argparse
import sys

from sponsor_hunter import registries, targets, jobs, letters, tracker, report


def cmd_update(args):
    registries.fetch_nl()
    registries.fetch_uk()


def cmd_jobs(args):
    countries = [args.country.upper()] if args.country else None
    all_targets = targets.load_targets()
    print(f"{len(all_targets)} hedef şirket taranıyor...")
    matches, manual = jobs.scan(all_targets, countries)
    df, n_new = tracker.merge(matches)
    print(f"\n✓ {len(matches)} eşleşen ilan bulundu, {n_new} tanesi yeni -> output/tracker.csv")
    if manual:
        print(f"\nATS'i otomatik bulunamayan {len(manual)} şirket (kariyer sayfasından elle bak):")
        for t in manual:
            print(f"  - {t['name']} ({t['country']}): {t.get('careers','')}")
    return matches


def cmd_letters(args):
    df = tracker.load()
    rows = df[df["status"] == "yeni"].to_dict("records")
    if not rows:
        print("Mektup üretilecek 'yeni' ilan yok. Önce: python3 run.py jobs")
        return
    written = letters.generate(rows)
    print(f"✓ {len(written)} mektup üretildi -> output/letters/")


def cmd_report(args):
    path = report.build()
    print(f"✓ Dashboard: {path}")
    print("  Açmak için: open output/dashboard.html")


def cmd_search(args):
    results = registries.search(args.name)
    if not results:
        print(f"'{args.name}' resmi kayıtlarda bulunamadı.")
        print("(Listeler indirilmemiş olabilir: python3 run.py update)")
        return
    for country, org, note in results:
        print(f"  [{country}] {org} — {note}")


def cmd_status(args):
    tracker.set_status(args.id, args.new_status, args.note or "")
    report.build()


def cmd_add_target(args):
    slugs = [args.slug] if args.slug else None
    targets.add_target(args.name, args.country, args.careers or "", slugs)


def cmd_all(args):
    cmd_update(args)
    print()
    cmd_jobs(args)
    print()
    cmd_letters(args)
    print()
    cmd_report(args)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("update")
    jp = sub.add_parser("jobs")
    jp.add_argument("--country", help="Sadece bu ülke: NL, UK, CH, LU")
    sub.add_parser("letters")
    sub.add_parser("report")
    sp = sub.add_parser("search")
    sp.add_argument("name")
    st = sub.add_parser("status")
    st.add_argument("id")
    st.add_argument("new_status", choices=["yeni", "basvuruldu", "cevap_bekleniyor", "mulakat", "red", "teklif"])
    st.add_argument("note", nargs="?")
    at = sub.add_parser("add-target")
    at.add_argument("name")
    at.add_argument("country")
    at.add_argument("--careers", default="")
    at.add_argument("--slug")
    ap = sub.add_parser("all")
    ap.add_argument("--country", help="Sadece bu ülke: NL, UK, CH, LU")

    args = p.parse_args()
    {"update": cmd_update, "jobs": cmd_jobs, "letters": cmd_letters, "report": cmd_report,
     "search": cmd_search, "status": cmd_status, "add-target": cmd_add_target, "all": cmd_all}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())

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
  python3 run.py apply 12            # ilanı tarayıcıda aç + mektubu panoya kopyala
  python3 run.py status 12 basvuruldu [not]   # başvuru durumu güncelle
  python3 run.py add-target "Şirket Adı" NL --careers https://... [--slug xyz]
"""
import argparse
import subprocess
import sys

from sponsor_hunter import registries, targets, jobs, letters, tracker, report, pdf_converter, resources, sponsorship
from sponsor_hunter.config import LETTERS


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


def cmd_check_sponsorship(args):
    df = tracker.load()
    df = sponsorship.enrich(df, only_new=not args.all)
    tracker.save(df)
    report.build()
    print("✓ Dashboard güncellendi — 'evet' işaretli ilanlar başa alındı.")


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


def cmd_apply(args):
    """İlanı tarayıcıda aç + mektubu panoya kopyala. Gönder tuşuna SEN basarsın."""
    df = tracker.load()
    rows = df[df["id"] == str(args.id)]
    if rows.empty:
        print(f"ID {args.id} bulunamadı. Dashboard'daki ID sütununa bak.")
        return
    row = rows.iloc[0]
    letter_path = (LETTERS / row["profile"] /
                   f"{letters._safe_filename(row['company'])}__{letters._safe_filename(row['title'])}.md")
    if letter_path.exists():
        text = letter_path.read_text(encoding="utf-8")
        # Varsayılan: tam kapak mektubu (bölüm 2); --email ile kısa e-posta (bölüm 1)
        marker = "## 1) Kısa outreach e-postası" if args.email else "## 2) Tam kapak mektubu"
        section = text.split(marker, 1)[-1]
        section = section.split("---\n\n## 2)", 1)[0].strip()
        section = section.replace("**", "")  # form alanları düz metin ister
        subprocess.run(["pbcopy"], input=section.encode("utf-8"), check=False)
        print(f"✓ {'Kısa e-posta' if args.email else 'Kapak mektubu'} panoya kopyalandı (Cmd+V ile yapıştır)")
    else:
        print(f"! Mektup dosyası yok ({letter_path.name}) — önce: python3 run.py letters")
    url = row["url"] or row["careers"]
    if url and not args.no_open:
        subprocess.run(["open", url], check=False)
        print(f"✓ İlan tarayıcıda açıldı: {url}")
    print(f"\n{row['company']} — {row['title']} ({row['profile']} profili)")
    print("Kontrol listesi: 1) Mektubu yapıştır ve 1 dk oku  2) Doğru CV'yi ekle "
          f"({'Ozer_Ipek_CV_2026.pdf' if row['profile']=='ozer' else 'Kateryna_Ipek_CV_2026.pdf'})  3) Gönder")
    print(f"Gönderdikten sonra: python3 run.py status {args.id} basvuruldu")


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
    lp = sub.add_parser("letters")
    lp.add_argument("--pdf", action="store_true", help="Mektupları PDF'ye çevir")
    sub.add_parser("report")
    sp = sub.add_parser("search")
    sp.add_argument("name")
    apl = sub.add_parser("apply")
    apl.add_argument("id")
    apl.add_argument("--email", action="store_true", help="Kapak mektubu yerine kısa e-postayı kopyala")
    apl.add_argument("--no-open", action="store_true", help="Tarayıcıda açma, sadece kopyala")
    st = sub.add_parser("status")
    st.add_argument("id")
    st.add_argument("new_status", choices=["yeni", "basvuruldu", "cevap_bekleniyor", "mulakat", "red", "teklif"])
    st.add_argument("note", nargs="?")
    at = sub.add_parser("add-target")
    at.add_argument("name")
    at.add_argument("country")
    at.add_argument("--careers", default="")
    at.add_argument("--slug")
    cvp = sub.add_parser("convert-pdf")
    cvp.add_argument("--all", action="store_true", help="Tüm mektupları PDF'ye çevir")
    sub.add_parser("resources")
    cs = sub.add_parser("check-sponsorship")
    cs.add_argument("--all", action="store_true", help="Sadece 'yeni' değil, tüm ilanları kontrol et")
    ap = sub.add_parser("all")
    ap.add_argument("--country", help="Sadece bu ülke: NL, UK, CH, LU")

    args = p.parse_args()
    def cmd_convert(args):
        if args.all:
            pdf_converter.convert_all_letters()
        else:
            print("Tüm mektupları PDF'ye çevirmek için: python3 run.py convert-pdf --all")

    {"update": cmd_update, "jobs": cmd_jobs, "letters": cmd_letters, "report": cmd_report,
     "search": cmd_search, "status": cmd_status, "apply": cmd_apply,
     "convert-pdf": cmd_convert, "resources": lambda a: print(resources.render()),
     "check-sponsorship": cmd_check_sponsorship,
     "add-target": cmd_add_target, "all": cmd_all}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())

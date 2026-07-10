"""Markdown mektupları PDF'ye çevirir — basit, dependency-az çözüm."""
from fpdf import FPDF
from .config import LETTERS


def convert_all_letters():
    """Tüm .md mektupları .pdf'ye çevir (basit text → PDF)."""
    md_files = list(LETTERS.glob("*/*.md"))
    if not md_files:
        print("Mektup dosyası bulunamadı.")
        return

    converted = 0
    for md_file in md_files:
        pdf_file = md_file.with_suffix(".pdf")
        if pdf_file.exists():
            continue

        try:
            text = md_file.read_text(encoding="utf-8")
            # Başlık/link kısmını çıkar, sadece tam mektup kısmını al
            if "## 2) Tam kapak mektubu" in text:
                text = text.split("## 2) Tam kapak mektubu")[1]
            if "---" in text:
                text = text.split("---")[0]

            # Özel karakterleri standartlaştır
            text = text.strip().replace("—", "-").replace("–", "-").replace(""", '"').replace(""", '"')

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 8, text)
            pdf.output(str(pdf_file))
            converted += 1
            print(f"  ✓ {md_file.parent.name}/{md_file.stem}")
        except Exception as e:
            print(f"  ✗ {md_file.parent.name}/{md_file.stem} — {e}")

    print(f"\n✓ {converted}/{len(md_files)} mektup PDF'ye çevrildi")
    print(f"  Konum: output/letters/kateryna/*.pdf")
    print(f"          output/letters/ozer/*.pdf")

# Sponsor Şirket Arama Otomasyonu

Hollanda, İngiltere, İsviçre ve Lüksemburg'da **vize sponsorluğu yapan şirketleri**
bulur, açık **Data Science / Analyst pozisyonlarını** tarar, her ilan için
**kişiselleştirilmiş başvuru mektubu** üretir ve tüm başvurularını tek bir
**dashboard**'da takip eder. Hem Özer (Data Scientist / ML) hem Kateryna
(Data & Business Analyst) profili için çalışır.

## Hızlı başlangıç

```bash
pip3 install -r requirements.txt   # bir kere
python3 run.py all                 # tam pipeline (~5-10 dk)
open output/dashboard.html         # sonuçları gör
```

## Ne yapıyor?

| Adım | Komut | Açıklama |
|------|-------|----------|
| 1. Resmi listeler | `python3 run.py update` | **NL:** IND tanınmış sponsor kaydı (~12.900 şirket). **UK:** Home Office Skilled Worker sponsor listesi (~100.000+ şirket). Her ay güncellenir — arada bir tekrar çalıştır. |
| 2. Pozisyon tarama | `python3 run.py jobs` | ~85 öncelikli hedef şirketin başvuru sistemlerini (Greenhouse, Lever, Recruitee, Ashby, Workable API'leri) tarar; iki profilin anahtar kelimeleriyle eşleşen **canlı ilanları** bulur. |
| 3. Mektuplar | `python3 run.py letters` | Her yeni ilan için `output/letters/` altına şirkete/pozisyona/ülkeye özel **kısa outreach e-postası + tam kapak mektubu** üretir. |
| 4. Dashboard | `python3 run.py report` | `output/dashboard.html` — filtrelenebilir tablo + durum sayaçları. |

## Günlük kullanım akışı

1. `python3 run.py jobs && python3 run.py letters && python3 run.py report`
2. Dashboard'ı aç, `yeni` durumundaki ilanlara bak.
3. İlana başvur: ilan linkine git, `output/letters/` içindeki hazır mektubu
   yapıştır (göndermeden önce 1 dk okuyup gerekirse ufak dokunuş yap!).
4. Durumu işaretle: `python3 run.py status 12 basvuruldu`
   (durumlar: `yeni | basvuruldu | cevap_bekleniyor | mulakat | red | teklif`)

## Faydalı komutlar

```bash
# Bir şirket resmi sponsor mu? (NL + UK kayıtlarında arar)
python3 run.py search "booking"

# Sadece Hollanda'yı tara
python3 run.py jobs --country NL

# Kendi hedef şirketini ekle (LinkedIn'de gördüğün bir şirket vs.)
python3 run.py add-target "Şirket Adı" NL --careers https://sirket.com/careers
```

## Ayarlar — `config.yaml`

- **Anahtar kelimeler**: profil başına aranacak pozisyon isimleri. Yeni rol tipi
  eklemek istersen buraya ekle (ör. `product analyst`).
- **exclude_keywords**: elenecek kelimeler (intern, PhD...).
- **locations**: ülke başına şehir listesi (ilan lokasyonu eşleştirme).

## Önemli notlar (beklentiyi doğru kurmak için)

- **İsviçre ve Lüksemburg'da kamuya açık sponsor listesi YOK.** İsviçre'de
  AB-dışı işe alım kotalıdır ve izni işveren başlatır; Lüksemburg'da EU Blue
  Card rotası kullanılır. Bu yüzden bu iki ülkede sadece AB-dışı işe alım
  geçmişi bilinen büyük işverenler hedeflenir. **En gerçekçi şansın Hollanda**
  (HSM vizesi hızlı ve öngörülebilir) ve İngiltere'dir.
- **Otomatik form doldurma bilerek yok.** Yüzlerce kimliksiz otomatik başvuru
  spam filtrelerine takılır ve markanı yakar. Bu araç sana *hedef + canlı ilan +
  hazır mektup* verir; son gönderim 2 dakikalık insan dokunuşuyla olur — cevap
  oranını asıl artıran budur.
- **ATS'i bulunamayan şirketler** (`manuel liste`de yazanlar) Workday/SAP gibi
  kapalı sistem kullanır — bunlara kariyer sayfası linkinden elle başvur.
- Büyük şirketlerde ilanda "visa sponsorship" yazmasa bile NL listesindeyse
  sponsor olabilir — `search` komutuyla kontrol et.

## Dosya yapısı

```
config.yaml              # profiller, anahtar kelimeler, ülkeler
run.py                   # ana komut
sponsor_hunter/          # kod
data/                    # indirilen resmi listeler + ATS cache
output/tracker.csv       # başvuru takip tablosu (Excel'i de var)
output/letters/          # üretilen mektuplar (profil bazlı klasörler)
output/dashboard.html    # görsel takip paneli
```

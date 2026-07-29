"""output/dashboard.html — takip verisinden tek dosyalık, çevrimdışı dashboard üretir.

Tarayıcıda aç: open output/dashboard.html
"""
import datetime
import html
import json

from .config import OUTPUT
from . import tracker

DASHBOARD = OUTPUT / "dashboard.html"

STATUS_META = {
    "yeni":             ("◆", "yeni",             "#2a78d6", "#3987e5"),
    "basvuruldu":       ("➤", "başvuruldu",       "#2a78d6", "#3987e5"),
    "cevap_bekleniyor": ("…", "cevap bekleniyor", "#fab219", "#fab219"),
    "mulakat":          ("★", "mülakat",          "#0ca30c", "#0ca30c"),
    "teklif":           ("✔", "TEKLİF",           "#0ca30c", "#0ca30c"),
    "red":              ("✕", "red",              "#d03b3b", "#d03b3b"),
}

PAGE = """<!doctype html>
<html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sponsor Başvuru Takibi</title>
<style>
:root {{
  --surface: #fcfcfb; --card: #ffffff; --border: #e6e5e1;
  --ink-1: #0b0b0b; --ink-2: #52514e; --accent: #2a78d6;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --surface:#1a1a19; --card:#242422; --border:#3a3936;
          --ink-1:#ffffff; --ink-2:#c3c2b7; --accent:#3987e5; }}
}}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--surface); color:var(--ink-1);
       font:15px/1.5 -apple-system, "Segoe UI", Roboto, sans-serif; padding:24px; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
.sub {{ color:var(--ink-2); margin-bottom:20px; font-size:13px; }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
         gap:12px; margin-bottom:20px; }}
.tile {{ background:var(--card); border:1px solid var(--border); border-radius:10px;
        padding:14px 16px; }}
.tile .n {{ font-size:28px; font-weight:700; }}
.tile .l {{ color:var(--ink-2); font-size:12px; text-transform:uppercase;
           letter-spacing:.04em; }}
.filters {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px; }}
select, input[type=search] {{ background:var(--card); color:var(--ink-1);
  border:1px solid var(--border); border-radius:8px; padding:7px 10px; font-size:14px; }}
input[type=search] {{ flex:1; min-width:180px; }}
.tablewrap {{ overflow-x:auto; background:var(--card); border:1px solid var(--border);
             border-radius:10px; }}
table {{ border-collapse:collapse; width:100%; min-width:820px; }}
th, td {{ text-align:left; padding:9px 12px; border-bottom:1px solid var(--border);
         font-size:14px; }}
th {{ color:var(--ink-2); font-size:12px; text-transform:uppercase;
     letter-spacing:.04em; position:sticky; top:0; background:var(--card); }}
tr:last-child td {{ border-bottom:none; }}
a {{ color:var(--accent); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.badge {{ display:inline-flex; align-items:center; gap:6px; font-size:13px;
         color:var(--ink-1); white-space:nowrap; }}
.badge .dot {{ font-size:12px; }}
.muted {{ color:var(--ink-2); }}
.count {{ margin:10px 2px; color:var(--ink-2); font-size:13px; }}
</style></head><body>
<h1>Sponsor Şirket Başvuru Takibi</h1>
<div class="sub">Son güncelleme: {generated} · Toplam {total} ilan · Kaynaklar: IND (NL) + Home Office (UK) resmi sponsor listeleri</div>
<div class="tiles">{tiles}</div>
<div class="filters">
  <select id="f-profile"><option value="">Profil: tümü</option>{profile_opts}</select>
  <select id="f-country"><option value="">Ülke: tümü</option>{country_opts}</select>
  <select id="f-status"><option value="">Durum: tümü</option>{status_opts}</select>
  <select id="f-spon">
    <option value="">Sponsorluk: tümü</option>
    <option value="evet">✓ sponsorluk vaat ediyor</option>
    <option value="belirsiz">? belirsiz</option>
    <option value="hayır">✕ çalışma izni istiyor</option>
  </select>
  <input type="search" id="f-search" placeholder="Şirket veya pozisyon ara...">
</div>
<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Profil</th><th>Şirket</th><th>Ülke</th><th>Pozisyon</th>
<th>Lokasyon</th><th>Sponsorluk</th><th>Durum</th><th>Bulunma</th><th>Link</th></tr></thead>
<tbody id="rows"></tbody></table></div>
<div class="count" id="count"></div>
<script>
const DATA = {data_json};
const STATUS = {status_json};
const tbody = document.getElementById('rows');
const esc = s => (s??'').toString().replace(/[&<>"]/g,
  c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c]);
function badge(s) {{
  const m = STATUS[s] || ['○', s, 'var(--ink-2)'];
  return `<span class="badge"><span class="dot" style="color:${{m[2]}}">${{m[0]}}</span>${{esc(m[1])}}</span>`;
}}
const SPON = {{
  'evet':    ['✓', 'sponsorluk', '#0ca30c'],
  'hayır':   ['✕', 'izin istiyor', '#d03b3b'],
  'belirsiz':['?', 'belirsiz', 'var(--ink-2)'],
}};
function sponBadge(s) {{
  const m = SPON[s]; if (!m) return '<span class="muted">—</span>';
  return `<span class="badge"><span class="dot" style="color:${{m[2]}}">${{m[0]}}</span>${{esc(m[1])}}</span>`;
}}
const SPON_RANK = {{'evet':0, 'belirsiz':1, '':2, 'hayır':3}};
function render() {{
  const p = document.getElementById('f-profile').value;
  const c = document.getElementById('f-country').value;
  const s = document.getElementById('f-status').value;
  const sp = document.getElementById('f-spon').value;
  const q = document.getElementById('f-search').value.toLowerCase();
  const rows = DATA.filter(r =>
    (!p || r.profile===p) && (!c || r.country===c) && (!s || r.status===s) &&
    (!sp || (r.sponsorship||'')===sp) &&
    (!q || (r.company+' '+r.title).toLowerCase().includes(q)));
  // Sponsorluk vaat edenler en üstte
  rows.sort((a,b) => (SPON_RANK[a.sponsorship||'']??2) - (SPON_RANK[b.sponsorship||'']??2));
  tbody.innerHTML = rows.map(r => `<tr>
    <td class="muted">${{esc(r.id)}}</td><td>${{esc(r.profile)}}</td>
    <td><strong>${{esc(r.company)}}</strong></td><td>${{esc(r.country)}}</td>
    <td>${{esc(r.title)}}</td><td class="muted">${{esc(r.location)}}</td>
    <td>${{sponBadge(r.sponsorship||'')}}</td>
    <td>${{badge(r.status)}}</td><td class="muted">${{esc(r.found_date)}}</td>
    <td>${{r.url ? `<a href="${{esc(r.url)}}" target="_blank">ilan</a>` : ''}}
        ${{r.careers ? ` · <a href="${{esc(r.careers)}}" target="_blank">kariyer</a>` : ''}}</td>
  </tr>`).join('');
  document.getElementById('count').textContent = rows.length + ' ilan gösteriliyor';
}}
for (const id of ['f-profile','f-country','f-status','f-spon'])
  document.getElementById(id).addEventListener('change', render);
document.getElementById('f-search').addEventListener('input', render);
render();
</script></body></html>
"""


def build():
    df = tracker.load()
    records = df.to_dict("records")
    total = len(records)

    by_status = df["status"].value_counts().to_dict() if total else {}
    tiles = [f'<div class="tile"><div class="n">{total}</div><div class="l">Toplam ilan</div></div>']
    for key, (icon, label, light, _dark) in STATUS_META.items():
        n = by_status.get(key, 0)
        if n or key in ("yeni", "basvuruldu"):
            tiles.append(
                f'<div class="tile"><div class="n" style="color:{light}">{n}</div>'
                f'<div class="l">{icon} {html.escape(label)}</div></div>')
    for country in sorted(df["country"].unique()) if total else []:
        n = int((df["country"] == country).sum())
        tiles.append(f'<div class="tile"><div class="n">{n}</div>'
                     f'<div class="l">{html.escape(country)}</div></div>')

    def opts(col):
        vals = sorted(v for v in df[col].unique() if v) if total else []
        return "".join(f'<option value="{html.escape(v)}">{html.escape(v)}</option>' for v in vals)

    status_json = {k: [icon, label, light] for k, (icon, label, light, _d) in STATUS_META.items()}
    page = PAGE.format(
        generated=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        total=total, tiles="".join(tiles),
        profile_opts=opts("profile"), country_opts=opts("country"), status_opts=opts("status"),
        data_json=json.dumps(records, ensure_ascii=False),
        status_json=json.dumps(status_json, ensure_ascii=False),
    )
    DASHBOARD.write_text(page, encoding="utf-8")
    return DASHBOARD

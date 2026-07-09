"""Şirkete ve pozisyona göre kişiselleştirilmiş başvuru mektubu üretir.

Her eşleşen ilan için output/letters/{profil}/ altına bir Markdown dosyası:
  1) Kısa outreach e-postası (recruiter'a ilk temas — 150 kelime)
  2) Tam kapak mektubu (başvuru formuna yapıştırılacak)

İçerik Özer'in motivasyon mektubundan ve Kateryna'nın CV'sinden damıtılmıştır.
"""
import re

from .config import LETTERS

VISA_LINE = {
    "NL": "I am aware that {company} is an IND-recognised sponsor for highly skilled migrants, "
          "which makes the visa process fast and predictable — and my family and I have deliberately "
          "chosen the Netherlands as the country we want to build our future in.",
    "UK": "I understand that {company} holds a UK Skilled Worker sponsor licence, and I am fully "
          "prepared to relocate to the UK at short notice with my family.",
    "CH": "I am aware that hiring non-EU talent in Switzerland requires an employer-led permit "
          "application, and I am fully prepared to support that process with complete documentation "
          "and flexibility on timing.",
    "LU": "I am aware that {company} can hire non-EU talent in Luxembourg through the EU Blue Card "
          "route, and I am fully prepared to support that process and relocate at short notice.",
}

OZER_EMAIL = """\
Subject: Data Scientist / ML Engineer — Kaggle Master, ex-NATO, ready to relocate ({country_name})

Dear {company} Recruitment Team,

I am applying for the {title} position. Three facts about me:

1. **Kaggle Master** (top tier globally) with a first-place finish in an international ML
   competition, and a Postgraduate Diploma in AI (Distinction, UK).
2. **Production experience**: at IME LLC (US) I shipped end-to-end ML systems — forecasting
   (LSTM/GRU), computer vision, RAG/LLM agents — deployed on AWS with Docker and CI/CD.
3. **23 years of NATO/military operations experience** (recognised by the NATO Secretary
   General), which means I deliver under pressure and communicate clearly with stakeholders.

{visa_line}

My CV is attached; my Kaggle profile is kaggle.com/zeripek. I would welcome a short call.

Kind regards,
Özer İpek · ozeripek84@gmail.com · +90 505 443 35 74
"""

OZER_LETTER = """\
Dear Hiring Manager,

I am writing to apply for the **{title}** position at **{company}**. I bring a profile that
exists at the intersection of two worlds that rarely meet: elite international military and
NATO service, and hands-on, production-grade expertise in Machine Learning and AI.

**Technical depth, proven publicly.** I am a Kaggle Master — top tier of the global data
science community — with a first-place finish in an international ML competition. I hold a
Postgraduate Diploma in Artificial Intelligence (Richmond University / ATHE, UK) completed
with Distinction. As a Data Scientist at IME LLC, a US-based technology company, I built and
deployed end-to-end systems in production: demand and revenue forecasting with LSTM/GRU,
computer vision pipelines (YOLO, CNN transfer learning), RAG-based autonomous agents with
LangChain, and BI dashboards — shipped via AWS, Docker and CI/CD.

**Operational judgment most data scientists don't have.** I served 23 years as a
Non-Commissioned Officer in the Turkish Armed Forces, including five years at NATO's Rapid
Deployable Corps HQ and deployments to Iraq and Afghanistan. My service was recognised with
the NATO Non-Article 5 Medal, awarded by NATO Secretary General Jens Stoltenberg. When you
hire me, you hire someone who has delivered under conditions where failure was not an
option — and that discipline does not disappear when I open a Jupyter notebook.

{visa_line} My English is fluent (C1 — ÖSYM YDS: 96.25/100), honed over years of working
across language and cultural boundaries inside NATO.

I would be glad to discuss how my combination of ML engineering skill and operational
experience can contribute to {company}. Thank you for your time and consideration.

Yours sincerely,
**Özer İpek**
Data Scientist & AI Engineer · Former NATO NCO · Kaggle Master
ozeripek84@gmail.com · +90 505 443 35 74 · kaggle.com/zeripek
"""

KATERYNA_EMAIL = """\
Subject: {title} application — Finance + Data Analytics background, ready to relocate ({country_name})

Dear {company} Recruitment Team,

I am applying for the {title} position. In brief:

1. **Finance & risk foundation**: BSc Economics (Honours), two MSc degrees — Risk Analysis &
   Economic Security and International Relations, both with Honours.
2. **Corporate FP&A experience** as an Economist at a major Ukrainian energy company —
   budgeting, variance analysis, forecasting models, ERP data.
3. **Modern analytics stack**: Python (Pandas, Scikit-learn), SQL, Tableau, Power BI —
   applied in regression/classification projects and interactive dashboards (github.com/kate-solo).

{visa_line}

I am multilingual (Ukrainian/Russian native, English C1, Turkish B1) and comfortable in
international teams. My CV is attached — I would welcome a short call.

Kind regards,
Kateryna Ipek · kateryna.solovkina@gmail.com · +90 552 514 32 74
"""

KATERYNA_LETTER = """\
Dear Hiring Manager,

I am writing to apply for the **{title}** position at **{company}**. I combine a rigorous
finance and risk background with modern data analytics skills — a combination that lets me
not only build models and dashboards, but understand what the numbers mean for the business.

**Finance foundation.** I graduated with Honours at every stage of my education: BSc in
Economics & Management, MSc in Risk Analysis & Economic Security, and MSc in International
Relations. As an Economist in the Planning Department of PJSC Donbassenergo, I owned
financial planning and budgeting for production operations: monthly/quarterly/annual
reporting, expense and revenue forecasting models, and plan-vs-actual variance analysis on
large ERP datasets.

**Analytics stack.** I work in Python (Pandas, NumPy, Scikit-learn) and SQL, build
regression and classification models for business forecasting, and deliver interactive
dashboards in Tableau and Power BI. My portfolio of EDA and business-insight projects is
public on GitHub (github.com/kate-solo) and Kaggle (kaggle.com/katerynaipek).

{visa_line} I am a true multilingual — native Ukrainian and Russian, C1 English, B1 Turkish —
and years of living and studying internationally have made cross-cultural collaboration
second nature to me.

I would be glad to discuss how I can contribute to {company}'s analytics and reporting.
Thank you for your time and consideration.

Yours sincerely,
**Kateryna Ipek**
Data & Business Analyst · Risk & Performance Analytics
kateryna.solovkina@gmail.com · +90 552 514 32 74 · linkedin.com/in/kateryna-ipek-961a06254
"""

TEMPLATES = {
    "ozer": (OZER_EMAIL, OZER_LETTER),
    "kateryna": (KATERYNA_EMAIL, KATERYNA_LETTER),
}

COUNTRY_NAMES = {"NL": "Netherlands", "UK": "United Kingdom", "CH": "Switzerland", "LU": "Luxembourg"}


def _safe_filename(s):
    return re.sub(r"[^\w\-]+", "_", s).strip("_")[:80]


def generate(matches):
    written = []
    for m in matches:
        profile = m["profile"]
        if profile not in TEMPLATES:
            continue
        email_tpl, letter_tpl = TEMPLATES[profile]
        visa = VISA_LINE.get(m["country"], "").format(company=m["company"])
        fields = {
            "company": m["company"],
            "title": m["title"],
            "visa_line": visa,
            "country_name": COUNTRY_NAMES.get(m["country"], m["country"]),
        }
        body = (
            f"# {m['company']} — {m['title']}\n\n"
            f"- **Ülke:** {fields['country_name']}\n"
            f"- **Lokasyon:** {m.get('location') or '-'}\n"
            f"- **İlan linki:** {m['url']}\n\n"
            f"---\n\n## 1) Kısa outreach e-postası\n\n{email_tpl.format(**fields)}\n"
            f"---\n\n## 2) Tam kapak mektubu\n\n{letter_tpl.format(**fields)}"
        )
        outdir = LETTERS / profile
        outdir.mkdir(parents=True, exist_ok=True)
        path = outdir / f"{_safe_filename(m['company'])}__{_safe_filename(m['title'])}.md"
        path.write_text(body, encoding="utf-8")
        written.append(path)
    return written

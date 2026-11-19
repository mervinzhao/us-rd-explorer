"""Parse Table 1 (Domestic R&D and R&D Abroad, PhRMA member companies) from
pdftotext -layout output of each PhRMA edition. Run with python -I.

Usage: python -I phrma_parse.py <raw_dir> <out_long_csv>
Writes one row per (edition, year) with the values read from that edition.
"""
import csv
import re
import sys
from pathlib import Path

# file stem -> (edition label, publication year, source URL)
EDITIONS = {
    "p2002": ("Pharmaceutical Industry Profile 2002 (appendix, Table 1)", 2002,
              "https://keionline.org/sites/default/files/PhRMA_2002_p02_07_appendix.pdf"),
    "p2003": ("Pharmaceutical Industry Profile 2003 (appendix, Table 1)", 2003,
              "https://www.keionline.org/sites/default/files/PhrMA_2003_Appendix_Survey.pdf"),
    "p2004": ("Pharmaceutical Industry Profile 2004 (appendix, Table 1)", 2004,
              "https://www.keionline.org/sites/default/files/PhRMA_Industry_Profile_2004-03-31.pdf"),
    "p2005": ("Pharmaceutical Industry Profile 2005 (appendix, Table 1)", 2005,
              "https://www.keionline.org/sites/default/files/PHRMA_2005-03-17_1143.pdf"),
    "p2006": ("Pharmaceutical Industry Profile 2006 (appendix, Table 1)", 2006,
              "https://www.keionline.org/sites/default/files/PHRMA_Industry_Profile_2006.pdf"),
    "p2007": ("Pharmaceutical Industry Profile 2007 (appendix, Table 1)", 2007,
              "https://www.keionline.org/sites/default/files/PHRMA_Industry_Profile_2007.pdf"),
    "p2008": ("Pharmaceutical Industry Profile 2008 (appendix, Table 1)", 2008,
              "https://www.keionline.org/sites/default/files/PhRMA_industry_profile_2008.pdf"),
    "p2009": ("Pharmaceutical Industry Profile 2009 (appendix, Table 1)", 2009,
              "https://www.keionline.org/sites/default/files/PhRMA2009_ProfileFINAL.pdf"),
    "p2010": ("Pharmaceutical Industry Profile 2010 (appendix, Table 1)", 2010,
              "https://www.keionline.org/sites/default/files/PhRMA_Profile_2010_FINAL.pdf"),
    "p2011": ("Pharmaceutical Industry Profile 2011 (appendix, Table 1)", 2011,
              "https://www.keionline.org/sites/default/files/phrma_profile_2011_final.pdf"),
    "p2012": ("Pharmaceutical Industry Profile 2012 (appendix, Table 1)", 2012,
              "https://www.keionline.org/sites/default/files/phrma_industry_profile_2012.pdf"),
    "p2013": ("Biopharmaceutical Research Industry Profile 2013 (appendix, Table 1)", 2013,
              "https://www.phrma-jp.org/wordpress/wp-content/uploads/2016/09/profile_2013.pdf"),
    "p2014": ("Biopharmaceutical Research Industry Profile 2014 (appendix, Table 1)", 2014,
              "https://cdn.aglty.io/phrma/2014_PhRMA_PROFILE.pdf"),
    "s2021": ("PhRMA Annual Membership Survey 2021 (Table 1)", 2021,
              "https://www.phrma.org/-/media/Project/PhRMA/PhRMA-Org/PhRMA-Org/PDF/M-O/PhRMA_membership-survey_2021.pdf"),
    "s2022": ("PhRMA Annual Membership Survey 2022 (Table 1)", 2022,
              "https://cdn.aglty.io/phrma/global/blog/import/pdfs/PhRMA_membership-survey_2022_final.pdf"),
    "s2023": ("PhRMA Annual Membership Survey 2023 (Table 1)", 2023,
              "https://phrma.org/-/media/Project/PhRMA/PhRMA-Org/PhRMA-Refresh/Report-PDFs/A-C/PhRMA_membership-survey_single-page_70523_es_digital.pdf"),
    "s2024": ("PhRMA Annual Membership Survey 2024 (Table 1)", 2024,
              "https://phrma.org/-/media/Project/PhRMA/PhRMA-Org/PhRMA-Refresh/Report-PDFs/PhRMA_2024-Annual-Membership-Survey.pdf"),
    "s2025": ("PhRMA Annual Membership Survey 2025 (Table 1)", 2025,
              "https://cdn.aglty.io/phrma/Report%20-%20PhRMA%202025%20Annual%20Membership%20Survey%20-%20July%202025.pdf"),
}

TITLE = re.compile(r"(R&D AND R&D ABROAD|R&D and R&D A\s?broad|R&D and R&D Abroad).*(19\d\d)\s*[-–]\s*(20\d\d)", re.I)
ROW = re.compile(r"^\s*(\*{0,3})\s*((?:19|20)\d\d)(\*{0,3})\s+(.*)$")


def num(tok):
    return float(tok.replace("$", "").replace(",", ""))


def parse(path):
    lines = path.read_text(errors="replace").split("\n")
    start = None
    for i, ln in enumerate(lines):
        squashed = (ln + " " + (lines[i + 1] if i + 1 < len(lines) else "")).replace("A broad", "Abroad")
        if TITLE.search(squashed) and ". ." not in squashed and "...." not in squashed:
            start = i
            break
    if start is None:
        raise SystemExit(f"no table title in {path}")
    out = []
    for ln in lines[start + 2:start + 120]:
        if re.match(r"^\s*A\s?verage", ln):
            break
        m = ROW.match(ln)
        if not m:
            continue
        pre, year, post, rest = m.groups()
        rest = rest.replace("$ ", "$")
        toks = rest.split()
        if len(toks) < 6:
            raise SystemExit(f"short row in {path}: {ln!r}")
        dom, abroad, total = num(toks[0]), num(toks[2]), num(toks[4])
        out.append(dict(year=int(year), marker=(pre + post), domestic=dom,
                        abroad=abroad, total=total, raw=ln.strip()))
    return start, out


def main():
    raw = Path(sys.argv[1])
    dest = Path(sys.argv[2])
    rows = []
    for stem, (label, pub, url) in EDITIONS.items():
        start, recs = parse(raw / f"{stem}.txt")
        years = [r["year"] for r in recs]
        print(f"{stem}: title line {start + 1}, {len(recs)} rows, {min(years)}-{max(years)}")
        for r in recs:
            chk = round(r["domestic"] + r["abroad"] - r["total"], 1)
            if abs(chk) > 0.15:
                print(f"  sum check off by {chk}: {r['raw']}")
            rows.append(dict(edition_key=stem, edition=label, pub_year=pub, url=url,
                             year=r["year"], marker=r["marker"],
                             domestic=r["domestic"], abroad=r["abroad"], total=r["total"]))
    with dest.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()

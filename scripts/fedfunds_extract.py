"""Extract every published value of federal research obligations by field of S&E / field of R&D
from the downloaded Federal Funds survey tables into one long "candidates" file.

Every (year, character, field) cell can appear in several volumes; selection of the value to keep
happens in fedfunds_build.py. Run with:  python -I scripts/fedfunds_extract.py <rd-fields dir>
Downloaded files are only read (xls/xlsx/pdf parsing), never executed.
"""
import csv
import re
import sys
from pathlib import Path

import openpyxl
import pandas as pd
import pdfplumber

ROOT = Path(sys.argv[1]).resolve()
RAW = ROOT / "raw" / "fedfunds"
OUT = ROOT / "data" / "fedfunds_candidates.csv"

# Publication order (later = more recent). Dates are release dates of the volume.
PUBS = {  # source id: (publication order, volume, title)
    "nsf03325": (1, "vol 50 based", "Federal Funds for R&D: Detailed Historical Tables, FYs 1951-2002"),
    "nsf07323": (2, "vol 54", "Federal Funds for R&D: FYs 2004-06"),
    "nsf09300": (3, "vol 55", "Federal Funds for R&D: FYs 2005-07"),
    "nsf10303": (4, "vol 56", "Federal Funds for R&D: FYs 2006-08"),
    "nsf21329": (5, "vol 69", "Federal Funds for R&D: FYs 2019-20"),
    "nsf22323": (6, "vol 70", "Federal Funds for R&D: FYs 2020-21"),
    "nsf24309": (7, "vol 71", "Federal Funds for R&D: FYs 2021-22"),
    "nsf24321": (8, "vol 72", "Federal Funds for R&D: FYs 2022-23"),
    "nsf25328": (9, "vol 73", "Federal Funds for R&D: FYs 2023-24"),
    "nsf26316": (10, "vol 74", "Federal Funds for R&D: FYs 2024-25"),
}
CHAR_FROM_TITLE = {"research": "research_total", "basic research": "basic", "applied research": "applied"}

rows = []


def add(year, character, label, level, parent, broad, value_k, unit, source, status, flag=""):
    rows.append(dict(
        fiscal_year=int(year), character=character, label_native=label, field_level=level,
        parent_native=parent, broad_field_native=broad, value_usd_thousands=value_k,
        unit_published=unit, source=source.split("-")[0], source_table=source,
        pub_order=PUBS[source.split("-")[0]][0], status=status, flag=flag))


# ---------------------------------------------------------------- A. nsf03325 historical xls
for tab, character in (("hist25", "research_total"), ("hist35", "basic"), ("hist45", "applied")):
    df = pd.read_excel(RAW / "nsf03325" / f"{tab}.xls", header=None, dtype=object)
    title = " ".join(str(df.iloc[i, 0]) for i in range(2))
    assert "fiscal years 1970-2002" in title, title
    assert "thousands" in str(df.iloc[2, 0]).lower()
    years = {}
    for c in range(1, df.shape[1]):
        for r in (7, 8):
            v = str(df.iloc[r, c]).strip()
            if re.fullmatch(r"(19|20)\d\d", v):
                years[c] = int(v)
    assert min(years.values()) == 1970 and max(years.values()) == 2002, years
    stack = {}  # level -> label
    for r in range(11, 69):
        raw = df.iloc[r, 0]
        if not isinstance(raw, str) or not raw.strip():
            continue
        label = raw.rstrip()
        indent = len(label) - len(label.lstrip(" "))
        label = label.strip()
        level = {0: 0, 2: 1, 4: 2, 6: 3}[indent]
        stack[level] = label
        for k in list(stack):
            if k > level:
                del stack[k]
        parent = stack.get(level - 1, "")
        broad = stack.get(1, "") if level >= 1 else label
        for c, y in years.items():
            v = df.iloc[r, c]
            s = str(v).strip()
            if s in ("NA", "", "nan"):
                continue
            val = float(s.replace(",", ""))
            status = "actual" if y <= 2000 else "preliminary"
            flag = ""
            # FY2000 carries 0 for sub-detail lines that were no longer collected (clinical vs other
            # medical, history/linguistics/other social sciences); their parents are non-zero.
            if y == 2000 and level == 3 and val == 0 and label in (
                    "Clinical medical", "Other medical", "History", "Linguistics", "Other social sciences"):
                flag = "zero_placeholder_not_collected"
            add(y, character, label, level, parent, broad, val, "thousands", f"nsf03325-{tab}", status, flag)

# ---------------------------------------------------------------- B. PDF tables (vols 54-56)
# Tables 122-127: multi-year trend tables (millions, 1 decimal); tables 19/30/41: single-year
# detailed-field tables (thousands) for the volume's actual year and two preliminary years.
PDF_SPECS = {
    "nsf07323": ("nsf07323/nsf07323.pdf", 2004),
    "nsf09300": ("nsf09300/nsf09300.pdf", 2005),
    "nsf10303": ("nsf10303/nsf10303.pdf", 2006),
}
PDF_BROAD = {"Environmental sciences", "Life sciences", "Mathematics and computer sciences",
             "Physical sciences", "Psychology", "Social sciences", "Other sciences, nec", "Engineering"}
BIOAG = "Biological and agricultural sciences"
BIOAG_KIDS = {"Agricultural sciences", "Biological sciences (excluding environmental biology)",
              "Environmental biology"}
NUM = r"(?:-?[\d,]+\.\d|-?[\d,]+|NA|\(\*\)|\*|-)"

for pub, (path, actual_max) in PDF_SPECS.items():
    with pdfplumber.open(RAW / path) as pdf:
        pages = [(i, p.extract_text() or "") for i, p in enumerate(pdf.pages)]
    tables = {}
    for i, txt in pages:
        m = re.match(r"TABLE (12[2-7]|19|30|41)\. Federal obligations for (research|basic research|applied research), "
                     r"by detailed field of science and engineering: FY (\d{4})[–-](\d{2,4})", txt)
        if m:
            tables.setdefault(m.group(1), dict(char=CHAR_FROM_TITLE[m.group(2)], pages=[]))["pages"].append(txt)
    assert len(tables) == 9, (pub, tables.keys())
    for tno, t in tables.items():
        years = None
        stack = {}
        for txt in t["pages"]:
            if "(Dollars in millions)" in txt:
                mult, unit = 1000, "millions_1dp"
            else:
                assert "(Dollars in thousands)" in txt
                mult, unit = 1, "thousands"
            pending = ""
            for line in txt.split("\n"):
                line = line.strip()
                if line.startswith("Field "):
                    ys = [int(x) for x in line.split()[1:]]
                    assert years in (None, ys)
                    years = ys
                    continue
                if years is None or not line:
                    continue
                if re.match(r"^(NA =|nec =|NOTES?:|SOURCE:|\* =|TABLE|\(Dollars|Preliminary|\d+$)", line):
                    pending = ""
                    continue
                toks = line.split()
                n = len(years)
                vals = toks[-n:] if len(toks) > n else []
                if vals and all(re.fullmatch(NUM, v) for v in vals):
                    label = (pending + " " + " ".join(toks[:-n])).strip()
                    pending = ""
                else:
                    pending = (pending + " " + line).strip()
                    continue
                if label == "All fields":
                    level, parent, broad = 0, "", "All fields"
                    stack = {}
                elif label in PDF_BROAD:
                    level, parent, broad = 1, "All fields", label
                    stack = {1: label}
                elif label == BIOAG:
                    level, parent, broad = 2, stack[1], stack[1]
                    stack[2] = label
                elif label in BIOAG_KIDS and stack.get(2) == BIOAG:
                    level, parent, broad = 3, BIOAG, stack[1]
                else:
                    level, parent, broad = 2, stack[1], stack[1]
                    stack.pop(2, None)
                for y, v in zip(years, vals):
                    if v in ("NA", "-"):
                        continue
                    flag = ""
                    if v in ("*", "(*)"):
                        val, flag = None, "lt_50k_suppressed"
                    else:
                        val = float(v.replace(",", "")) * mult
                    status = "actual" if y <= actual_max else "preliminary"
                    add(y, t["char"], label, level, parent, broad, val, unit,
                        f"{pub}-T{tno}", status, flag)

# ---------------------------------------------------------------- C. xlsx trend tables (vols 69-74)
# trend tables (millions) plus the single-year detailed-field tables (thousands)
XLSX_SPECS = {
    "nsf21329": ("122", "123", "124", "125", "126", "127", "017", "029", "041"),
    "nsf22323": ("122", "123", "124", "125", "126", "127", "017", "029", "041"),
    "nsf24309": ("090", "091", "092", "093", "094", "095", "023", "028", "033"),
    "nsf24321": ("090", "091", "092", "093", "094", "095", "023", "028", "033"),
    "nsf25328": ("090", "091", "092", "093", "094", "095", "023", "028", "033"),
    "nsf26316": ("090", "091", "092", "093", "094", "095", "023", "028", "033"),
}
for pub, tabs in XLSX_SPECS.items():
    for tab in tabs:
        f = RAW / pub / f"{pub}-tab{tab}.xlsx"
        ws = openpyxl.load_workbook(f, data_only=True).active
        cells = [[c for c in r] for r in ws.iter_rows()]
        title = str(cells[1][0].value)
        m = re.match(r"Federal obligations for (research|basic research|applied research), by detailed field "
                     r"of (science and engineering|R&D): FYs (\d{4})[–-](\d{2})", title)
        assert m, (f, title)
        character = CHAR_FROM_TITLE[m.group(1)]
        unit_txt = str(cells[2][0].value).lower()
        assert "millions" in unit_txt or "thousands" in unit_txt, unit_txt
        mult = 1000 if "millions" in unit_txt else 1
        hdr = cells[3]
        assert str(hdr[0].value).strip() == "Field"
        years = {}
        for j, c in enumerate(hdr[1:], start=1):
            s = str(c.value).strip()
            y = int(float(re.match(r"(\d{4})", s).group(1)))
            years[j] = (y, "preliminary" if "prelim" in s.lower() else "actual")
        # decimals published? older volumes give 0.1M, newer integer millions
        sample = [c.value for r in cells[4:] for c in r[1:] if isinstance(c.value, float)]
        one_dp = any(abs(v - round(v)) > 1e-9 for v in sample)
        unit = ("millions" if mult == 1000 else "thousands") + ("_1dp" if one_dp else "_int")
        stack = {}
        for r in cells[4:]:
            lab = r[0].value
            if lab is None or not str(lab).strip():
                continue
            lab = str(lab).strip()
            level = int(r[0].alignment.indent or 0)
            # footnote marker on "Other social sciencesa"
            lab_clean = re.sub(r"(sciences)a$", r"\1", lab)
            stack[level] = lab_clean
            for k in list(stack):
                if k > level:
                    del stack[k]
            parent = stack.get(level - 1, "")
            broad = stack.get(1, "") if level >= 1 else lab_clean
            for j, (y, status) in years.items():
                v = r[j].value
                if v is None:
                    continue
                s = str(v).strip()
                if s in ("NA", "", "-"):
                    continue
                flag = ""
                if s == "*":
                    val, flag = None, "lt_500k_suppressed"
                else:
                    val = float(s.replace(",", "")) * mult
                add(y, character, lab_clean, level, parent, broad, val, unit, f"{pub}-T{int(tab)}", status, flag)

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote {len(rows)} candidate cells to {OUT}")
cd = pd.DataFrame(rows)
print(cd.groupby(["source", "status"]).fiscal_year.agg(["min", "max", "count"]))

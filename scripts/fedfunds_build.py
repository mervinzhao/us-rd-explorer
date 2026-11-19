"""Build the final long series of federal research obligations by field from the candidates file.

Selection rule per (fiscal year, character, field):
  * Only actual (non-preliminary) values are used.
  * The row set and labels come from the most recently published accessible volume that reports that
    year (the "latest" publication). Rows that only older volumes printed (presentational subtotals
    such as "Biological and agricultural sciences" for FY2000-06) are dropped.
  * The value is the latest-published one. If an older publication printed the same cell at finer
    precision and agrees with every later publication within rounding, the finer value is kept
    (it is the same number, unrounded). If an older value disagrees beyond rounding, that is a
    revision: the later value wins and the difference is written to the revisions log.

Run: python -I scripts/fedfunds_build.py <rd-fields dir>
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(sys.argv[1]).resolve()
DATA = ROOT / "data"
RAW = ROOT / "raw" / "fedfunds"

HALF = {"thousands": 0.5, "thousands_int": 0.5, "thousands_1dp": 0.05,
        "millions_1dp": 50.0, "millions_int": 500.0}
PREC = {"thousands": 1, "thousands_int": 1, "thousands_1dp": 0.1, "millions_1dp": 100, "millions_int": 1000}

# ------------------------------------------------------------------ field keys
# Keys only unify cosmetic relabelling within one taxonomy (e.g. "Life sciences, n.e.c." /
# "Life sciences, nec" / "Other life sciences"). They do NOT bridge the FY2021 field-of-R&D break:
# for FY2021+ the key is built from the new label.
OLD = {
    "total, all fields": "all_fields", "all fields": "all_fields",
    "life sciences, total": "life_sciences", "life sciences": "life_sciences",
    "biol & agricultural, total": "bio_and_agri_sciences",
    "biological and agricultural sciences": "bio_and_agri_sciences",
    "biol (excl environmental)": "biological_sciences_excl_env_bio",
    "biological sciences (excluding environmental biology)": "biological_sciences_excl_env_bio",
    "environmental biology": "environmental_biology",
    "agricultural": "agricultural_sciences", "agricultural sciences": "agricultural_sciences",
    "medical sciences, total": "medical_sciences", "medical sciences": "medical_sciences",
    "clinical medical": "clinical_medical_sciences", "other medical": "other_medical_sciences",
    "life sciences, n.e.c.": "other_life_sciences", "life sciences, nec": "other_life_sciences",
    "other life sciences": "other_life_sciences",
    "psychology, total": "psychology", "psychology": "psychology",
    "biological aspects": "psychology_biological_aspects", "social aspects": "psychology_social_aspects",
    "psychological sciences, n.e.c.": "other_psychological_sciences",
    "psychological sciences, nec": "other_psychological_sciences",
    "other psychological sciences": "other_psychological_sciences",
    "physical sciences, total": "physical_sciences", "physical sciences": "physical_sciences",
    "astronomy": "astronomy", "chemistry": "chemistry", "physics": "physics",
    "physical sciences, n.e.c.": "other_physical_sciences", "physical sciences, nec": "other_physical_sciences",
    "other physical sciences": "other_physical_sciences",
    "environmental sciences, total": "environmental_sciences", "environmental sciences": "environmental_sciences",
    "atmospheric sciences": "atmospheric_sciences", "geological sciences": "geological_sciences",
    "oceanography": "oceanography",
    "environmental sciences, n.e.c.": "other_environmental_sciences",
    "environmental sciences, nec": "other_environmental_sciences",
    "other environmental sciences": "other_environmental_sciences",
    "math & computer sciences, total": "math_and_computer_sciences",
    "mathematics and computer sciences": "math_and_computer_sciences",
    "computer sciences and mathematics": "math_and_computer_sciences",
    "mathematics": "mathematics", "computer sciences": "computer_sciences",
    "math & computer sciences, n.e.c.": "other_math_and_computer_sciences",
    "mathematics and computer sciences, nec": "other_math_and_computer_sciences",
    "other computer sciences and mathematics": "other_math_and_computer_sciences",
    "engineering, total": "engineering", "engineering": "engineering",
    "aeronautical": "aeronautical_engineering", "aeronautical engineering": "aeronautical_engineering",
    "astronautical": "astronautical_engineering", "astronautical engineering": "astronautical_engineering",
    "chemical": "chemical_engineering", "chemical engineering": "chemical_engineering",
    "civil": "civil_engineering", "civil engineering": "civil_engineering",
    "electrical": "electrical_engineering", "electrical engineering": "electrical_engineering",
    "mechanical": "mechanical_engineering", "mechanical engineering": "mechanical_engineering",
    "metallurgy & materials": "metallurgy_and_materials_engineering",
    "metallurgy and materials engineering": "metallurgy_and_materials_engineering",
    "engineering, n.e.c.": "other_engineering", "engineering, nec": "other_engineering",
    "other engineering": "other_engineering",
    "social sciences, total": "social_sciences", "social sciences": "social_sciences",
    "anthropology": "anthropology", "economics": "economics", "political science": "political_science",
    "sociology": "sociology",
    "social sciences, n.e.c.": "other_social_sciences", "social sciences, nec": "other_social_sciences",
    "other social sciences": "other_social_sciences",
    "history": "history", "linguistics": "linguistics",
    "other sciences, n.e.c.": "other_sciences_nec", "other sciences, nec": "other_sciences_nec",
    "other sciences nec": "other_sciences_nec",
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def field_key(label, year, level, parent):
    lab = label.strip()
    m = re.match(r"^(.*?)\s*\(formerly (.*)\)$", lab)
    if year >= 2021:
        new = (m.group(1) if m else lab).lower()
        new = {"material science": "materials science", "humanities": "humanities, including history"}.get(new, new)
        if new in ("all fields",):
            return "all_fields"
        return "rd_" + slug(new)
    if m:
        lab = m.group(2)
    low = lab.lower()
    # 1970-75 sub-detail of "Social sciences, n.e.c." is a different concept from the later
    # "Other social sciences" (it excludes history and linguistics)
    if low == "other social sciences" and level == 3:
        return "other_social_sciences_excl_history_linguistics"
    return OLD[low]


def taxonomy(year):
    if year <= 1975:
        return "fose_1970_75"
    if year <= 1977:
        return "fose_1976_77"
    if year <= 2020:
        return "fose_1978_2020"
    return "ford_2021"


c = pd.read_csv(DATA / "fedfunds_candidates.csv", keep_default_na=False, na_values=[""])
c = c[c.flag.fillna("") != "zero_placeholder_not_collected"]
c = c[c.status == "actual"].copy()
c["key"] = [field_key(l, y, lv, p) for l, y, lv, p in zip(c.label_native, c.fiscal_year, c.field_level,
                                                          c.parent_native.fillna(""))]
c["broad_key"] = [field_key(b, y, 1, "") for b, y in zip(c.broad_field_native, c.fiscal_year)]
c["parent_key"] = [field_key(p, y, max(lv - 1, 0), "") if isinstance(p, str) and p else ""
                   for p, y, lv in zip(c.parent_native, c.fiscal_year, c.field_level)]
c["half"] = c.unit_published.map(HALF)
c["prec"] = c.unit_published.map(PREC)

out, revs = [], []
for (y, ch), g in c.groupby(["fiscal_year", "character"]):
    latest_pub = g.pub_order.max()
    keys = g[g.pub_order == latest_pub].key.unique()
    for k in keys:
        cand = g[g.key == k].sort_values(["pub_order", "prec"], ascending=[True, False])
        lat = cand[cand.pub_order == latest_pub].sort_values("prec").iloc[0]  # finest within latest volume
        num = cand[cand.value_usd_thousands.notna()]
        note = []
        if pd.isna(lat.value_usd_thousands):
            # "*" = greater than 0 but less than half the table's rounding unit; an older, finer
            # publication of the same cell that lies in that range is consistent with it
            cap = lat.half
            ok = [r for r in num.itertuples() if 0 < r.value_usd_thousands < cap + r.half]
            if ok:
                chosen = sorted(ok, key=lambda r: (r.prec, -r.pub_order))[0]
                note.append(f"finer-precision value; latest publication {lat.source_table} prints * (>0 and < ${cap:,.1f} thousand)")
            else:
                chosen = lat
                note.append(f"published as * (>0 but < ${cap:,.1f} thousand); value left blank")
        else:
            # revisions: any value that disagrees with a later one beyond rounding
            rows = list(num.itertuples())
            for i, a in enumerate(rows):
                for b in rows[i + 1:]:
                    if b.pub_order > a.pub_order and abs(a.value_usd_thousands - b.value_usd_thousands) > a.half + b.half + 1e-6:
                        revs.append(dict(fiscal_year=y, character=ch, field_key=k, label_native=b.label_native,
                                         older_source=a.source_table, older_value=a.value_usd_thousands,
                                         newer_source=b.source_table, newer_value=b.value_usd_thousands,
                                         diff_usd_thousands=b.value_usd_thousands - a.value_usd_thousands))
            # finest candidate consistent with every later-published candidate
            best = lat
            for a in sorted(rows, key=lambda r: (r.prec, -r.pub_order)):
                later = [b for b in rows if b.pub_order > a.pub_order or (b.pub_order == a.pub_order and b is not a)]
                if all(abs(a.value_usd_thousands - b.value_usd_thousands) <= a.half + b.half + 1e-6 for b in later
                       if b.pub_order >= a.pub_order):
                    best = a
                    break
            chosen = best
            if chosen.source_table != lat.source_table:
                note.append(f"finer-precision value; latest publication {lat.source_table} agrees within rounding")
            older_rev = [r for r in revs if r["fiscal_year"] == y and r["character"] == ch and r["field_key"] == k]
            if older_rev:
                note.append("revised vs " + ",".join(sorted({r['older_source'] for r in older_rev})))
        if chosen.source_table != lat.source_table:
            note.append(f"label as printed in {lat.source_table}")
        lvl = int(lat.field_level)
        out.append(dict(
            fiscal_year=y, character=ch,
            broad_field_native=lat.broad_field_native,
            detailed_field_native=lat.label_native,
            taxonomy_version=taxonomy(y),
            value_usd_thousands_nominal=(None if pd.isna(chosen.value_usd_thousands)
                                         else round(float(chosen.value_usd_thousands), 1)),
            source_table=chosen.source_table, status="actual",
            field_level=lvl, parent_field_native=lat.parent_native if isinstance(lat.parent_native, str) else "",
            field_key=k, broad_field_key=lat.broad_key, parent_field_key=lat.parent_key,
            precision_usd_thousands=chosen.prec, note="; ".join(note)))

df = pd.DataFrame(out).sort_values(["character", "fiscal_year", "field_level", "broad_field_key", "field_key"])
df.loc[df.field_level == 0, "broad_field_key"] = "all_fields"
df.to_csv(DATA / "fedfunds_research_by_field.csv", index=False)
rv = pd.DataFrame(revs).drop_duplicates()
rv["pct"] = (rv.diff_usd_thousands / rv.older_value.where(rv.older_value != 0) * 100).round(2)
rv.to_csv(DATA / "fedfunds_revisions_log.csv", index=False)
print("rows", len(df), "revisions", len(rv))

# ------------------------------------------------------------------ checks
chk = []
tot = df[df.field_level == 0].pivot(index="fiscal_year", columns="character", values="value_usd_thousands_nominal")
prec0 = df[df.field_level == 0].pivot(index="fiscal_year", columns="character", values="precision_usd_thousands")
t1 = pd.read_excel(RAW / "nsf26316" / "nsf26316-tab001.xlsx", header=None)
t1 = t1.iloc[4:, [0, 3, 4, 5]]
t1.columns = ["fy", "research_total_t1", "basic_t1", "applied_t1"]
t1 = t1[t1.fy.astype(str).str.fullmatch(r"\d{4}")]
t1["fy"] = t1.fy.astype(int)
t1 = t1.set_index("fy").apply(pd.to_numeric, errors="coerce")
m = tot.join(t1, how="left")
m["basic_diff"] = m.basic - m.basic_t1
m["applied_diff"] = m.applied - m.applied_t1
m["research_diff"] = m.research_total - m.research_total_t1
m["b_plus_a_minus_total"] = m.basic + m.applied - m.research_total
m.to_csv(DATA / "fedfunds_check_totals_vs_table1.csv")
print(m[["basic_diff", "applied_diff", "research_diff", "b_plus_a_minus_total"]].abs().describe())

# additivity of children to parents in the final file
bad = []
for (y, ch), g in df.groupby(["fiscal_year", "character"]):
    for par, kids in g[g.field_level > 0].groupby("parent_field_key"):
        p = g[g.field_key == par]
        if len(p) != 1 or kids.value_usd_thousands_nominal.isna().any():
            continue
        tol = p.precision_usd_thousands.iloc[0] / 2 + kids.precision_usd_thousands.sum() / 2 + 1
        d = kids.value_usd_thousands_nominal.sum() - p.value_usd_thousands_nominal.iloc[0]
        if abs(d) > tol:
            bad.append((y, ch, par, round(d)))
pd.DataFrame(bad, columns=["fiscal_year", "character", "parent", "children_minus_parent"]).to_csv(
    DATA / "fedfunds_check_additivity.csv", index=False)
print("additivity failures", len(bad))
for b in bad[:40]:
    print(b)

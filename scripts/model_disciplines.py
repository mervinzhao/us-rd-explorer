"""Split National Patterns research cells (basic, applied x source of funds, all performers, 1970-2024)
by discipline. Output: data/discipline_cube.csv.

Federal: field-of-science shares of federal research obligations (Federal Funds survey), by character.
Higher ed, state & local, nonprofit: field shares of the university R&D each funds (HERD); FY2010-24 by
source, FY1973-2009 the nonfederal field mix, FY1970-72 held at FY1973.
Business: no discipline data in any survey; carried as 'unclassified'.
"""
import numpy as np
import pandas as pd
from plotlib import DATA
from crosswalk import group as field_group

YEARS = list(range(1970, 2025))
CH = ["basic", "applied"]
DISC = ["life", "physical", "computing", "engineering", "social", "earth", "math", "other", "unclassified"]
G2D = {"Medical & health": "life", "Biological & ag": "life", "Physical sciences": "physical",
       "Engineering": "engineering", "Earth, atmos & ocean": "earth", "Computing": "computing",
       "Math & statistics": "math", "Social & behavioral": "social", "Other": "other"}

# federal field shares
ff = pd.read_csv(DATA / "harmonized_fedfunds_by_group.csv")
ff["disc"] = ff.group.map(G2D)
fed = {}
for ch in CH:
    w = ff[ff.character == ch].pivot_table(index="fiscal_year", columns="disc", values="usd_billions_nominal", aggfunc="sum")
    w = w.reindex(index=YEARS, columns=DISC).fillna(0)
    fed[ch] = w.div(w.sum(axis=1), axis=0)

# HERD field shares by source
h = pd.read_csv(DATA / "herd_by_field_source.csv")
h = h[h.finest_level & (h.fiscal_year >= 1973)].copy()
h["disc"] = h.detailed_field_native.map(lambda s: G2D[field_group(s)])
SRCMAP = {"Federal": "fed", "Federal government": "fed", "Total": "tot", "Institution funds": "higher_education",
          "State and local government": "nonfederal_government", "Nonprofit organizations": "nonprofit"}
h["src"] = h.source_of_funds_native.map(SRCMAP)
pv = h.dropna(subset=["src"]).pivot_table(index=["src", "fiscal_year"], columns="disc",
                                          values="value_usd_thousands_nominal", aggfunc="sum").fillna(0)
nonfed = (pv.loc["tot"] - pv.loc["fed"]).clip(lower=0)
herd = {}
for src in ["higher_education", "nonfederal_government", "nonprofit"]:
    df = pd.DataFrame(0.0, index=YEARS, columns=DISC)
    for y in YEARS:
        row = pv.loc[(src, y)] if y >= 2010 else nonfed.loc[max(y, 1973)]
        row = row.reindex(DISC).fillna(0)
        df.loc[y] = row / row.sum()
    herd[src] = df

np_ = pd.read_csv(DATA / "natpat_character_source_performer.csv")
cells = (np_[(np_.performer == "all_performers") & (np_.source_of_funds != "all_sources") & np_.character.isin(CH)]
         .pivot_table(index=["source_of_funds", "character"], columns="year", values="value_usd_millions_nominal", aggfunc="sum"))
rows = []
for (src, ch), r in cells.iterrows():
    for y in YEARS:
        tot = r.get(y, np.nan)
        tot = 0.0 if pd.isna(tot) else float(tot)
        if src == "federal":
            sh = fed[ch].loc[y]
        elif src == "business":
            sh = pd.Series(0.0, index=DISC)
            sh["unclassified"] = 1.0
        else:
            sh = herd[src].loc[y]
        for d in DISC:
            rows.append(dict(year=y, character=ch, source=src, discipline=d, value=tot * float(sh[d])))
cube = pd.DataFrame(rows)
cube.to_csv(DATA / "discipline_cube.csv", index=False)
chk = cube.groupby(["year", "character", "source"]).value.sum()
tot = cells.stack().rename("t").reset_index().rename(columns={"source_of_funds": "source", "level_2": "year"})
print("cells:", len(chk))
nb = cube[cube.source != "business"]
t = nb[nb.year.isin([1970, 2024])].pivot_table(index="discipline", columns=["character", "year"], values="value", aggfunc="sum")
print((t / 1000).round(1).to_string())

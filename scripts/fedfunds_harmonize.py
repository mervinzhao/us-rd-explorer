"""Map Federal Funds research obligations onto the harmonized field groups.

Life sciences and math/CS use their level-2 children, everything else its level-1 broad field.
FY1970-75: math and CS are only published combined; split using the FY1976 basic/applied ratio
(flagged as imputed in the output).
"""
import pandas as pd
from plotlib import DATA

d = pd.read_csv(DATA / "fedfunds_research_by_field.csv")


def grp(r):
    b = r.broad_field_native.lower().replace("&", "and")
    f, lvl = r.detailed_field_native.lower(), r.field_level
    if lvl == 0:
        return "TOTAL"
    if b.startswith("life"):
        if lvl != 2:
            return None
        if f.startswith(("medical", "health")):
            return "Medical & health"
        return "Biological & ag"
    if "math" in b and "comput" in b:
        if r.taxonomy_version == "fose_1970_75":
            return "MATHCS" if lvl == 1 else None
        if lvl != 2:
            return None
        if f.startswith("computer"):
            return "Computing"
        if f.startswith("mathematics") and "computer" not in f:
            return "Math & statistics"
        return "MATHCS_NEC"
    if lvl != 1:
        return None
    if b.startswith("computer"):
        return "Computing"
    if b.startswith("mathematics"):
        return "Math & statistics"
    if b.startswith("physical"):
        return "Physical sciences"
    if b.startswith("engineering"):
        return "Engineering"
    if b.startswith(("environmental", "geosciences")):
        return "Earth, atmos & ocean"
    if b.startswith(("psychology", "social")):
        return "Social & behavioral"
    if b.startswith("other"):
        return "Other"
    raise ValueError(r)


d["grp"] = d.apply(grp, axis=1)
d = d[d.grp.notna()]
d["val"] = d.value_usd_thousands_nominal / 1e6
w = d.pivot_table(index=["character", "fiscal_year"], columns="grp", values="val", aggfunc="sum")

# Impute FY1970-75 math vs CS split from FY1976 shares, by character
for ch in ["basic", "applied", "research_total"]:
    r76 = w.loc[(ch, 1976)]
    cs_share = r76["Computing"] / (r76["Computing"] + r76["Math & statistics"])
    for y in range(1970, 1976):
        mc = w.loc[(ch, y), "MATHCS"]
        w.loc[(ch, y), "Computing"] = mc * cs_share
        w.loc[(ch, y), "Math & statistics"] = mc * (1 - cs_share)
w = w.drop(columns="MATHCS")

# Math/CS n.e.c. (1976-2020): allocate pro rata between computing and math
nec = w["MATHCS_NEC"].fillna(0)
base = w["Computing"] + w["Math & statistics"]
w["Computing"] += nec * w["Computing"] / base
w["Math & statistics"] += nec * w["Math & statistics"] / base
w = w.drop(columns="MATHCS_NEC")

parts = w.drop(columns="TOTAL").sum(axis=1)
gap = (parts - w["TOTAL"]).abs().max()
print("max |sum of groups - total| ($B):", round(gap, 4))

out = w.drop(columns="TOTAL").reset_index().melt(id_vars=["character", "fiscal_year"], var_name="group",
                                                 value_name="usd_billions_nominal")
out["imputed"] = (out.fiscal_year < 1976) & out.group.isin(["Computing", "Math & statistics"])
out.to_csv(DATA / "harmonized_fedfunds_by_group.csv", index=False)

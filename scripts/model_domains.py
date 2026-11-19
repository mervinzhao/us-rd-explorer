"""Split every National Patterns cell (character of work x source of funds, all performers, 1953-2024)
into application domains. Output: data/domain_shares.csv and data/domain_cube.csv.

Lens: what the R&D is for.
  Federal: agency mission (Federal Funds obligations by agency and character), with federal
           computer-science research (field data) pulled out into Software & internet.
  Business: industry of the performing company (BRDIS/BERD 2008-2024). Before 2008 only the
           health part is estimated (PhRMA series); the rest of business is "Not split".
  Higher ed, state & local, nonprofit: field of the university R&D each funds (HERD).
"""
import re
import warnings
import numpy as np
import pandas as pd
import xlrd
import openpyxl
from plotlib import DATA, ROOT
from crosswalk import group as field_group

warnings.filterwarnings("ignore")
YEARS = list(range(1953, 2025))
CH = ["basic", "applied", "development"]
DOM = ["health", "software", "hardware", "defense", "energy", "industrial", "agenv", "general", "unsplit"]
FF = ROOT / "raw" / "fedfunds"


def num(x):
    return float(x) if isinstance(x, (int, float)) else 0.0


# ======================= FEDERAL =======================
# --- 2005-2024: current tables with sub-agency detail
TABS = {"basic": ["078", "079"], "applied": ["080", "081"], "development": ["082", "083"]}
TOP_MAP = {
    "Department of Agriculture": "agenv", "Department of Defense": "defense", "Department of Education": "general",
    "Department of Energy": "energy", "Department of Health and Human Services": "health",
    "Department of Homeland Security": "defense", "Department of Housing and Urban Development": "general",
    "Department of the Interior": "agenv", "Department of Justice": "general", "Department of Labor": "general",
    "Department of State": "general", "Department of Transportation": "industrial", "Department of the Treasury": "general",
    "Department of Veterans Affairs": "health", "Department of Commerce": "general",
    "Environmental Protection Agency": "agenv", "National Aeronautics and Space Administration": "defense",
    "National Science Foundation": "general", "Nuclear Regulatory Commission": "energy",
    "Tennessee Valley Authority": "energy", "Smithsonian Institution": "general",
}
SUB_MAP = {  # (parent, sub) -> domain, carved out of the parent's domain
    ("Department of Energy", "Office of Science"): "general",
    ("Department of Energy", "National Nuclear Security Administration"): "defense",
    ("Department of Commerce", "National Institute of Standards and Technology"): "industrial",
    ("Department of Commerce", "National Oceanic and Atmospheric Administration"): "agenv",
    ("Department of Defense", "Defense Health Agency"): "health",
}
cur = {ch: {} for ch in CH}  # ch -> year -> {domain: $M}
sub_shares = {ch: {} for ch in CH}  # parent -> year -> {domain: share of parent}
for ch, tabs in TABS.items():
    for t in tabs:
        rows = list(openpyxl.load_workbook(FF / "nsf26316" / f"nsf26316-tab{t}.xlsx", read_only=True).active.iter_rows(values_only=True))
        hdr = next(r for r in rows if r[0] == "Agency")
        yrs = [int(str(x)[:4]) for x in hdr[1:] if x]
        parent, other_block = None, False
        for r in rows[rows.index(hdr) + 1:]:
            name = str(r[0]).strip() if r[0] else ""
            if not name:
                continue
            vals = [num(v) for v in r[1:1 + len(yrs)]]
            if name == "Other agencies":
                other_block = True
                continue
            if name in ("All agencies",):
                for y, v in zip(yrs, vals):
                    if y <= 2024:
                        cur[ch].setdefault(y, {})["_total"] = v
                continue
            top = name.startswith("Department of") or other_block
            if top:
                parent = name
                d = TOP_MAP.get(name, "general")
                for y, v in zip(yrs, vals):
                    if y <= 2024:
                        cur[ch].setdefault(y, {})
                        cur[ch][y][d] = cur[ch][y].get(d, 0) + v
            elif (parent, name) in SUB_MAP:
                d, pd_ = SUB_MAP[(parent, name)], TOP_MAP[parent]
                for y, v in zip(yrs, vals):
                    if y <= 2024:
                        cur[ch][y][d] = cur[ch][y].get(d, 0) + v
                        cur[ch][y][pd_] = cur[ch][y].get(pd_, 0) - v
                        sub_shares[ch].setdefault(parent, {}).setdefault(y, {})[d] = v
for ch in CH:  # sub-agency split of DOE and Commerce, 2005-07 mean, for back-casting
    for parent in ["Department of Energy", "Department of Commerce"]:
        pass

# parent totals 2005-07 to compute sub-shares
def parent_split(ch, parent, years=(2005, 2006, 2007)):
    rows = []
    for t in TABS[ch]:
        rr = list(openpyxl.load_workbook(FF / "nsf26316" / f"nsf26316-tab{t}.xlsx", read_only=True).active.iter_rows(values_only=True))
        hdr = next(r for r in rr if r[0] == "Agency")
        yrs = [int(str(x)[:4]) for x in hdr[1:] if x]
        for r in rr:
            if r[0] and str(r[0]).strip() == parent:
                rows += [(y, num(v)) for y, v in zip(yrs, r[1:1 + len(yrs)]) if y in years]
    tot = sum(v for _, v in rows)
    out = {}
    for y in years:
        for d, v in sub_shares[ch].get(parent, {}).get(y, {}).items():
            out[d] = out.get(d, 0) + v
    out = {d: v / tot for d, v in out.items()} if tot else {}
    out[TOP_MAP[parent]] = 1 - sum(out.values())
    return out


DOE_SPLIT = {ch: parent_split(ch, "Department of Energy") for ch in CH}
COM_SPLIT = {ch: parent_split(ch, "Department of Commerce") for ch in CH}
print("DOE split 2005-07:", {ch: {k: round(v, 2) for k, v in DOE_SPLIT[ch].items()} for ch in CH})

# --- 1951-2002: historical table A, major agencies by character
s = xlrd.open_workbook(FF / "nsf03325" / "hista.xls").sheet_by_index(0)
HMAP = {"Department of Agriculture": "agenv", "Department of Commerce": "COM", "Department of Defense": "defense",
        "Department of Energy": "DOE", "Department of Health, Education, & Welfare": "health",
        "Department of Health & Human Services": "health", "Department of the Interior": "agenv",
        "Department of Transportation": "industrial", "Department of Veterans Affairs": "health",
        "Atomic Energy Commission": "DOE", "Energy Research & Development Administration": "DOE",
        "National Aeronautics & Space Administration": "defense", "National Science Foundation": "general",
        "Other agencies": "general"}
hist = {ch: {} for ch in CH}
hist_rd = {}
yr = None
for r in range(s.nrows):
    a = str(s.cell_value(r, 0)).strip()
    m = re.search(r"Fiscal year (\d{4})", a)
    if m:
        yr = int(m.group(1))
        continue
    if not (yr and a):
        continue
    key = re.sub(r"\s*\d+$", "", a)  # strip footnote digits
    vals = [s.cell_value(r, c) for c in range(1, 7)]
    rd, basic, applied, dev = (vals[1], vals[2], vals[3], vals[4])
    tgt = "_total" if key.startswith("Total") else HMAP.get(key)
    if tgt is None:
        continue
    for ch, v in zip(CH, (basic, applied, dev)):
        if isinstance(v, float):
            hist[ch].setdefault(yr, {})
            hist[ch][yr][tgt] = hist[ch][yr].get(tgt, 0) + v
    if isinstance(rd, float):
        hist_rd.setdefault(yr, {})
        hist_rd[yr][tgt] = hist_rd[yr].get(tgt, 0) + rd


def resolve(d, ch):
    out = {}
    for k, v in d.items():
        if k == "_total":
            continue
        if k == "DOE":
            for dd, sh in DOE_SPLIT[ch].items():
                out[dd] = out.get(dd, 0) + v * sh
        elif k == "COM":
            for dd, sh in COM_SPLIT[ch].items():
                out[dd] = out.get(dd, 0) + v * sh
        else:
            out[k] = out.get(k, 0) + v
    return out


fed = {ch: pd.DataFrame(0.0, index=YEARS, columns=DOM) for ch in CH}
fed_flag = {}
for ch in CH:
    for y in YEARS:
        if y >= 2005:
            d = {k: v for k, v in cur[ch][y].items() if k != "_total"}
            tot, f = cur[ch][y]["_total"], "reported"
        elif y <= 2002 and y in hist[ch] and hist[ch][y].get("_total"):
            d, tot, f = resolve(hist[ch][y], ch), hist[ch][y]["_total"], "reported"
        elif y <= 2002:
            d, tot, f = resolve(hist_rd[y], ch), hist_rd[y]["_total"], "modeled"
        else:
            continue
        for k, v in d.items():
            fed[ch].loc[y, k] = v / tot
        fed_flag[(ch, y)] = f
    for y in (2003, 2004):
        fed[ch].loc[y] = (fed[ch].loc[2002] + fed[ch].loc[2005]) / 2
        fed_flag[(ch, y)] = "modeled"
    fed[ch] = fed[ch].clip(lower=0)
    fed[ch] = fed[ch].div(fed[ch].sum(axis=1), axis=0)

# pull federal computer-science research out into software
ff = pd.read_csv(DATA / "harmonized_fedfunds_by_group.csv")
cs = ff.pivot_table(index="fiscal_year", columns=["character", "group"], values="usd_billions_nominal")
for ch in ["basic", "applied"]:
    share = (cs[(ch, "Computing")] / cs[ch].sum(axis=1)).reindex(YEARS)
    share = share.bfill()  # FY1953-69: hold the FY1970 share
    fed[ch] = fed[ch].mul(1 - share, axis=0)
    fed[ch]["software"] += share
print("federal 2024 basic:", fed["basic"].loc[2024].round(3).to_dict())
print("federal 1965 dev:", fed["development"].loc[1965].round(3).to_dict())

# ======================= BUSINESS =======================
RAW = pd.read_csv(DATA / "berd_by_industry.csv")
RAW = RAW[(RAW.is_primary == 1) & (RAW.year >= 2008)]
ALL, MFG, NONMFG = "21–23, 31–33, 42–81", "31–33", "21–23, 42–81"
# named components: code -> domain. Manufacturing residual -> industrial, nonmanufacturing residual -> general.
COMP = {
    "3254": "health", "3391": "health", "541714": "health", "334510, 334517": "health", "621–23": "health",
    "51": "software", "5415": "software",
    "334": "hardware", "333242": "hardware",
    "3364": "defense", "334511": "defense", "336992": "defense",
    "22": "energy", "324": "energy", "3336": "energy", "21": "energy",
    "311": "agenv", "312": "agenv", "3253": "agenv", "33311": "agenv",
}
# children carved out of a parent that is also listed: 334 contains 334510/17 and 334511
CARVE = {"334510, 334517": "334", "334511": "334"}
MFG_CODES = {"3254", "3391", "334", "333242", "3364", "336992", "324", "3336", "311", "312", "3253", "33311"}
NEED = [ALL, MFG, NONMFG] + list(COMP)


def berd_table(measure, years):
    return (RAW[(RAW.measure == measure) & RAW.industry_code_native.isin(NEED)]
            .pivot_table(index="year", columns="industry_code_native", values="value_usd_millions_nominal",
                         aggfunc="first").reindex(columns=NEED, index=years))


def domains_from(x):
    g = pd.DataFrame(0.0, index=x.index, columns=DOM)
    for code, d in COMP.items():
        g[d] += x[code]
        if code in CARVE:
            g[COMP[CARVE[code]]] -= x[code]
    mfg_named = sum(x[c] for c in MFG_CODES) - 0  # carve-outs are inside 334 (mfg) so mfg total unchanged
    non_named = sum(x[c] for c in COMP if c not in MFG_CODES and c not in CARVE)
    g["industrial"] += x[MFG] - mfg_named
    g["general"] += x[NONMFG] - non_named
    return g


tot_all = berd_table("total", range(2008, 2025)).interpolate(limit_direction="both")
# National Patterns' business source is company money, so split company-funded R&D (federally funded
# business R&D, mostly aerospace and defense, belongs to the federal source). Company funding by industry is
# published from 2015; 2008-14 use each industry's 2015-17 company share of its total.
comp = berd_table("company_funded", range(2008, 2025))
cratio = (comp.loc[2015:2017] / tot_all.loc[2015:2017]).mean().clip(upper=1).fillna(1.0)
tot_t = comp.fillna(tot_all * cratio)
dom_tot = domains_from(tot_t)
print("max |domains - all| ($M):", (dom_tot.sum(axis=1) - tot_t[ALL]).abs().max().round(1))
mix = {}
for ch in CH:
    x = berd_table("company_funded_" + ch, range(2015, 2025))
    ratio = (x / tot_t.loc[2015:2024]).mean()
    x = x.fillna(tot_t.loc[2015:2024] * ratio)
    mix[ch] = domains_from(x)
early = {ch: (mix[ch].loc[2015:2017].sum() / sum(mix[c].loc[2015:2017].sum() for c in CH)) for ch in CH}
bus = {ch: pd.DataFrame(np.nan, index=YEARS, columns=DOM) for ch in CH}
for ch in CH:
    for y in range(2008, 2025):
        v = mix[ch].loc[y] if y >= 2015 else dom_tot.loc[y] * early[ch]
        v = v.clip(lower=0)
        bus[ch].loc[y] = v / v.sum()

# before 2008: SIC-basis industry series 1957-96 (company funds), interpolated 1997-2007, held 1953-56
from business_sic_domains import business_pre2008
pooled2008 = dom_tot.loc[2008].clip(lower=0)
pre, bus_pre_flag = business_pre2008(pooled2008 / pooled2008.sum())
# 1997-2007: health follows the PhRMA-based series instead of a straight line; other domains rescale
ex = pd.read_csv(DATA / "exbio_model.csv")
exb = ex[ex.source == "business"].groupby("year")[["bio", "total"]].sum()
ph = exb.bio / exb.total
r96 = pre.loc[1996, "health"] / ph[1996]  # bridge the SIC-basis level in 1996 to the BERD level in 2008
for y in range(1997, 2008):
    w = (y - 1996) / 12
    ph[y] = ph[y] * (r96 + (1 - r96) * w)
    others = pre.loc[y].drop("health")
    pre.loc[y, "health"] = ph[y]
    pre.loc[y, others.index] = others / others.sum() * (1 - ph[y])
for ch in CH:
    for y in YEARS:
        if y < 2008:
            v = pre.loc[y].reindex(DOM).fillna(0) * early[ch].reindex(DOM).fillna(0)
            bus[ch].loc[y] = v / v.sum()
print("business 2024 dev:", bus["development"].loc[2024].round(3).to_dict())

# ======================= HERD-BASED SOURCES =======================
def herd_domain(label):
    s_ = label.lower()
    g = field_group(label)
    if g in ("Medical & health",) or "bioengineering" in s_:
        return "health"
    if g == "Biological & ag":
        return "agenv" if re.search(r"agricultur|natural resources", s_) else "health"
    if g == "Computing":
        return "software"
    if g == "Engineering":
        if "electrical" in s_:
            return "hardware"
        if re.search(r"aero|astro", s_):
            return "defense"
        return "industrial"
    if g == "Physical sciences":
        return "industrial" if "materials" in s_ else "general"
    if g == "Earth, atmos & ocean":
        return "agenv"
    return "general"


h = pd.read_csv(DATA / "herd_by_field_source.csv")
h = h[h.finest_level & (h.fiscal_year >= 1973)].copy()
h["dom"] = h.detailed_field_native.map(herd_domain)
SRCMAP = {"Federal": "fed", "Federal government": "fed", "Total": "tot", "Institution funds": "higher_education",
          "State and local government": "nonfederal_government", "Nonprofit organizations": "nonprofit"}
h["src"] = h.source_of_funds_native.map(SRCMAP)
h = h.dropna(subset=["src"])
pv = h.pivot_table(index=["src", "fiscal_year"], columns="dom", values="value_usd_thousands_nominal", aggfunc="sum").fillna(0)
nonfed = (pv.loc["tot"] - pv.loc["fed"]).clip(lower=0)
# 1973-79: engineering subfields not collected; split "Engineering, all" with the FY1980 engineering mix
eng80 = h[(h.fiscal_year == 1980) & (h.src == "tot") & h.detailed_field_native.str.startswith("Engineering")]
eng80 = eng80.groupby("dom").value_usd_thousands_nominal.sum()
eng80 = eng80 / eng80.sum()
for y in range(1973, 1980):
    ind = nonfed.loc[y, "industrial"]
    eng_all = h[(h.fiscal_year == y) & h.detailed_field_native.str.startswith("Engineering")]
    e = (eng_all[eng_all.src == "tot"].value_usd_thousands_nominal.sum()
         - eng_all[eng_all.src == "fed"].value_usd_thousands_nominal.sum())
    nonfed.loc[y, "industrial"] = ind - e
    for d, sh in eng80.items():
        nonfed.loc[y, d] = nonfed.loc[y].get(d, 0) + e * sh
herd = {}
for src in ["higher_education", "nonfederal_government", "nonprofit"]:
    df = pd.DataFrame(0.0, index=YEARS, columns=DOM)
    for y in YEARS:
        row = pv.loc[(src, y)] if y >= 2010 else nonfed.loc[max(y, 1973)]
        row = row.reindex(DOM).fillna(0)
        df.loc[y] = row / row.sum()
    herd[src] = df
print("higher ed 2024:", herd["higher_education"].loc[2024].round(3).to_dict())

# ======================= ASSEMBLE =======================
np_ = pd.read_csv(DATA / "natpat_character_source_performer.csv")
cells = (np_[(np_.performer == "all_performers") & (np_.source_of_funds != "all_sources") & (np_.character != "total")]
         .pivot_table(index=["source_of_funds", "character"], columns="year", values="value_usd_millions_nominal", aggfunc="sum"))
SH = {"federal": fed, "business": bus}
SH.update({s_: {ch: herd[s_] for ch in CH} for s_ in herd})
rows = []
for (src, ch), r in cells.iterrows():
    for y in YEARS:
        tot = r.get(y, np.nan)
        tot = 0.0 if pd.isna(tot) else tot
        shv = SH[src][ch].loc[y]
        if src == "federal":
            flag = "modeled" if fed_flag.get((ch, y)) == "modeled" or y < 1970 and ch != "development" else "reported"
        elif src == "business":
            flag = bus_pre_flag[y] if y < 2008 else ("modeled" if y < 2015 else "reported")
        else:
            flag = "reported" if y >= 2010 else "modeled"
        for d in DOM:
            rows.append(dict(year=y, character=ch, source=src, domain=d, share=float(shv[d]), value=tot * float(shv[d]), flag=flag))
cube = pd.DataFrame(rows)
cube.to_csv(DATA / "domain_cube.csv", index=False)
chk = cube.groupby(["year", "character", "source"])[["share"]].sum()
print("share sums min/max:", chk.share.min().round(4), chk.share.max().round(4))
t = cube[cube.year == 2024].pivot_table(index="domain", columns="character", values="value", aggfunc="sum").reindex(DOM)
print((t / 1000).round(1).to_string())

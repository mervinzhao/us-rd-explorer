"""Hypothetical: the original National Patterns slide (character of work x source of funds) with
life-sciences R&D removed.

National Patterns has no field split, so for each source of funds and character of work we estimate
the life-sciences share s(source, character, year) from the surveys that do carry field or industry,
and remove s x the National Patterns cell. Output: data/exbio_model.csv and data/exbio_shares.csv.

Federal (NatPat source = federal, all performers)
  basic, applied 1970-2024: life sciences / all fields, Federal Funds research obligations.
  basic, applied 1953-69:   (HEW/HHS + USDA) share of federal obligations x k, where k is the
                            1970-74 mean ratio of the life share to that agency share (modeled).
  development 1953-2024:    (HEW/HHS + USDA [+ Defense Health Agency from FY2020]) share of
                            federal development obligations; FY2003-04 interpolated.
Business (NatPat source = business)
  2008-2024: bio industries (NAICS 3254 + 3391 + 541714) / all industries, BRDIS/BERD;
             character split from BERD 2015-24, 2015-17 mean fractions before 2015.
  before 2008: PhRMA member domestic R&D x k (k = 2008-12 mean BERD bio / PhRMA) over NatPat
             business-performed R&D (modeled); constant share before the PhRMA series starts.
Higher education, state & local, nonprofit (these fund mostly university and nonprofit performers)
  2010-2024: life sciences share of HERD R&D funded by institution funds / state & local / nonprofits.
  1973-2009: life share of HERD nonfederally funded R&D x the 2010-12 ratio of the source-specific
             share to the nonfederal share (modeled); 1953-72 held at 1973.
  Same share applied to basic, applied and development (HERD has no field x character).
"""
import re
import numpy as np
import pandas as pd
import xlrd
import openpyxl
from plotlib import DATA, ROOT, deflator

YEARS = range(1953, 2025)
FF = ROOT / "raw" / "fedfunds"
flags = {}  # (source, character) -> {year: "reported" | "modeled"}

# ---------------- National Patterns cells ----------------
np_ = pd.read_csv(DATA / "natpat_character_source_performer.csv")
cells = (np_[(np_.performer == "all_performers") & (np_.source_of_funds != "all_sources")
             & (np_.character != "total")]
         .pivot_table(index=["source_of_funds", "character"], columns="year",
                      values="value_usd_millions_nominal", aggfunc="sum"))
bus_perf = (np_[(np_.performer == "business") & (np_.source_of_funds == "all_sources")]
            .pivot_table(index="character", columns="year", values="value_usd_millions_nominal"))

# ---------------- Federal ----------------
ff = pd.read_csv(DATA / "harmonized_fedfunds_by_group.csv")
ff["life"] = ff.group.isin(["Medical & health", "Biological & ag"])
fed_life = (ff.groupby(["character", "fiscal_year"])
            .apply(lambda g: g.loc[g.life, "usd_billions_nominal"].sum() / g.usd_billions_nominal.sum(),
                   include_groups=False).unstack(0))

# hist table A: obligations by agency and character, FY1951-2002
s = xlrd.open_workbook(FF / "nsf03325" / "hista.xls").sheet_by_index(0)
rows, yr = [], None
for r in range(s.nrows):
    a = str(s.cell_value(r, 0)).strip()
    m = re.search(r"Fiscal year (\d{4})", a)
    if m:
        yr = int(m.group(1))
        continue
    if yr and a:
        v = [s.cell_value(r, c) for c in range(1, 7)]
        v = [float(x) if isinstance(x, float) else np.nan for x in v]
        rows.append(dict(year=yr, agency=a, research=v[1] - v[4] if not np.isnan(v[4]) else np.nan,
                         basic=v[2], applied=v[3], development=v[4]))
ha = pd.DataFrame(rows)
ha["bioagency"] = ha.agency.str.contains("Health|Agriculture")
ha["total"] = ha.agency.str.startswith("Total")


def agency_share(col):
    g = ha.groupby(["year"])
    num = ha[ha.bioagency].groupby("year")[col].sum(min_count=1)
    den = ha[ha.total].set_index("year")[col]
    return num / den


fed = pd.DataFrame(index=YEARS, columns=["basic", "applied", "development"], dtype=float)
for ch in ["basic", "applied"]:
    proxy = agency_share(ch)
    proxy_r = (ha[ha.bioagency].groupby("year")[["basic", "applied"]].sum().sum(axis=1)
               / ha[ha.total].set_index("year")[["basic", "applied"]].sum(axis=1))
    proxy = proxy.fillna(proxy_r)  # FY1951-55: basic/applied not split, use research total
    # FY1951-55 research = total R&D - development is NA too; fall back on R&D total share
    proxy_rd = (ha[ha.bioagency].groupby("year")["research"].sum()
                / ha[ha.total].set_index("year")["research"])
    proxy = proxy.fillna(proxy_rd)
    k = (fed_life.loc[1970:1974, ch] / proxy.loc[1970:1974]).mean()
    for y in YEARS:
        if y >= 1970:
            fed.loc[y, ch] = fed_life.loc[y, ch]
            flags.setdefault(("federal", ch), {})[y] = "reported"
        else:
            fed.loc[y, ch] = k * proxy.get(y, np.nan)
            flags.setdefault(("federal", ch), {})[y] = "modeled"
    print(f"federal {ch}: k={k:.2f}, 1953 share={fed.loc[1953, ch]:.2f}, 1969={fed.loc[1969, ch]:.2f}, "
          f"1970={fed.loc[1970, ch]:.2f}")

dev_old = agency_share("development")
dev_new = {}
for t in ["082", "083"]:
    ws = openpyxl.load_workbook(FF / "nsf26316" / f"nsf26316-tab{t}.xlsx", read_only=True).active
    rr = list(ws.iter_rows(values_only=True))
    hdr = next(r for r in rr if r[0] == "Agency")
    yrs = [int(str(h)[:4]) for h in hdr[1:] if h]
    tab = {r[0]: r[1:1 + len(yrs)] for r in rr if r[0]}
    num = lambda name: np.array([x if isinstance(x, (int, float)) else 0 for x in tab.get(name, [0] * len(yrs))], float)
    tot = num("All agencies")
    bio = num("Department of Health and Human Services") + num("Department of Agriculture") + num("Defense Health Agency")
    dev_new.update({y: b / t for y, b, t in zip(yrs, bio, tot) if y <= 2024})
dev = pd.concat([dev_old.dropna(), pd.Series(dev_new)]).sort_index()
dev = dev[~dev.index.duplicated(keep="last")].reindex(YEARS).interpolate().bfill()
fed["development"] = dev
for y in YEARS:
    flags.setdefault(("federal", "development"), {})[y] = "modeled" if y in (2003, 2004) else "reported"

# ---------------- HERD-based sources ----------------
h = pd.read_csv(DATA / "herd_by_field_source.csv")
h = h[h.finest_level & (h.fiscal_year >= 1973)].copy()
from crosswalk import group
h["life"] = h.detailed_field_native.map(group).isin(["Medical & health", "Biological & ag"])
SRCMAP = {"Federal": "Federal", "Federal government": "Federal", "Total": "Total",
          "Institution funds": "higher_education", "State and local government": "nonfederal_government",
          "Nonprofit organizations": "nonprofit"}
h["src"] = h.source_of_funds_native.map(SRCMAP)
lshare = (h.dropna(subset=["src"]).groupby(["src", "fiscal_year"])
          .apply(lambda g: g.loc[g.life, "value_usd_thousands_nominal"].sum() / g.value_usd_thousands_nominal.sum(),
                 include_groups=False).unstack(0))
nonfed_tot = h[h.src == "Total"].groupby("fiscal_year").value_usd_thousands_nominal.sum() - \
    h[h.src == "Federal"].groupby("fiscal_year").value_usd_thousands_nominal.sum()
nonfed_life = h[(h.src == "Total") & h.life].groupby("fiscal_year").value_usd_thousands_nominal.sum() - \
    h[(h.src == "Federal") & h.life].groupby("fiscal_year").value_usd_thousands_nominal.sum()
nonfed_share = nonfed_life / nonfed_tot

herd = {}
for src in ["higher_education", "nonfederal_government", "nonprofit"]:
    r = (lshare.loc[2010:2012, src] / nonfed_share.loc[2010:2012]).mean()
    ser = pd.Series(index=YEARS, dtype=float)
    for y in YEARS:
        if y >= 2010:
            ser[y], f = lshare.loc[y, src], "reported"
        elif y >= 1973:
            ser[y], f = min(nonfed_share[y] * r, 0.98), "modeled"
        else:
            ser[y], f = min(nonfed_share[1973] * r, 0.98), "modeled"
        for ch in ["basic", "applied", "development"]:
            flags.setdefault((src, ch), {})[y] = f
    herd[src] = ser
    print(f"{src}: calib r={r:.2f}, 1973={ser[1973]:.2f}, 2009={ser[2009]:.2f}, 2010={ser[2010]:.2f}, 2024={ser[2024]:.2f}")

# ---------------- Business ----------------
RAW = pd.read_csv(DATA / "berd_by_industry.csv")
RAW = RAW[(RAW.is_primary == 1) & (RAW.year >= 2008)]
NEED = ["21–23, 31–33, 42–81", "3254", "3391", "541714"]


def berd(measure, years):
    x = (RAW[(RAW.measure == measure) & RAW.industry_code_native.isin(NEED)]
         .pivot_table(index="year", columns="industry_code_native", values="value_usd_millions_nominal",
                      aggfunc="first").reindex(columns=NEED, index=years))
    return x


tot = berd("total", range(2008, 2025)).interpolate(limit_direction="both")
bio_tot = tot["3254"] + tot["3391"] + tot["541714"]
frac = {}
for ch in ["basic", "applied", "development"]:
    x = berd(ch, range(2015, 2025))
    ratio = (x / tot.loc[2015:2024]).mean()
    x = x.fillna(tot.loc[2015:2024] * ratio)
    frac[ch] = (x["3254"] + x["3391"] + x["541714"]) / bio_tot.loc[2015:2024]
frac = pd.DataFrame(frac)
frac = frac.div(frac.sum(axis=1), axis=0)
early = frac.loc[2015:2017].mean()
print("bio character fractions 2015-17:", early.round(3).to_dict(), " 2024:", frac.loc[2024].round(3).to_dict())

bio_series = bio_tot.copy().astype(float)
bio_flag = {y: "reported" for y in bio_tot.index}
try:
    ph = pd.read_csv(DATA / "phrma_domestic_rd.csv").dropna(subset=["domestic_rd_usd_millions"])
    ph = ph.drop_duplicates("year", keep="last").set_index("year").domestic_rd_usd_millions
    k = (bio_tot.loc[2008:2012] / ph.reindex(range(2008, 2013))).mean()
    print(f"business: PhRMA years {ph.index.min()}-{ph.index.max()}, k={k:.2f}")
    for y in range(int(ph.index.min()), 2008):
        if y in ph.index:
            bio_series[y], bio_flag[y] = ph[y] * k, "modeled"
    bio_series = bio_series.sort_index()
except FileNotFoundError:
    print("business: no PhRMA series yet; pre-2008 held at 2008 share")

bus = pd.DataFrame(index=YEARS, columns=["basic", "applied", "development"], dtype=float)
# 2015-24: bio share of each character directly. Before 2015 the bio character mix is unknown, so hold
# the 2015-17 character shares and scale them by the movement in bio's share of all business R&D.
overall = bio_series / bus_perf.loc["total"].reindex(bio_series.index)
for y in bio_series.index:
    for ch in bus.columns:
        if y >= 2015:
            bus.loc[y, ch] = bio_series[y] * frac.loc[y, ch] / bus_perf.loc[ch, y]
for ch in bus.columns:
    base = bus.loc[2015:2017, ch].mean() / overall.loc[2015:2017].mean()
    for y in bio_series.index:
        if y < 2015:
            bus.loc[y, ch] = base * overall[y]
            pass  # 2008-14: bio total reported, character mix held at 2015-17
first = bus.dropna().index.min()
for y in YEARS:
    for ch in bus.columns:
        if y < first:
            bus.loc[y, ch] = bus.loc[first, ch]
        flags.setdefault(("business", ch), {})[y] = bio_flag.get(y, "modeled") if y >= first else "held"
bus = bus.clip(upper=0.95)

# ---------------- Assemble ----------------
SHARES = {"federal": fed, "business": bus}
for src in herd:
    SHARES[src] = pd.DataFrame({ch: herd[src] for ch in ["basic", "applied", "development"]})
defl = deflator()
out = []
for (src, ch), row in cells.iterrows():
    for y in YEARS:
        v = row.get(y, np.nan)
        sh = SHARES[src].loc[y, ch]
        out.append(dict(year=y, character=ch, source=src, total=v, life_share=sh, bio=v * sh, nonbio=v * (1 - sh),
                        deflator=defl.get(y), flag=flags[(src, ch)][y]))
out = pd.DataFrame(out)
out.to_csv(DATA / "exbio_model.csv", index=False)

summ = out.groupby(["character", "year"])[["total", "bio"]].sum()
summ["bio_share"] = summ.bio / summ.total
print((summ.bio_share.unstack(0).loc[[1955, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2024]] * 100).round(1).to_string())
for src in SHARES:
    print(src, (SHARES[src].loc[[1955, 1965, 1975, 1990, 2005, 2015, 2024]] * 100).round(0).to_dict("list"))

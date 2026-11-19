"""Business (company and other nonfederal) R&D by application domain, 1953-2007.

Sources, company funds by industry:
  SIC basis 1956-98: NSF 'Research and Development in Industry' tables transcribed from scanned volumes
    (data/sird_scan_by_industry.csv), with NSF IRIS historical tables (data/sird_hist_by_industry.csv,
    from a public mirror of the archived IRIS files) filling cells the scans lack, notably 1997-98.
  NAICS basis 2004-07: IRIS SIRD tables by NAICS industry.
Segments:
  1956-98 'reported', 2004-07 'reported', 1999-2003 'interpolated' (shares, linear between 1998 and 2004),
  1953-55 'held' at 1956. The caller adjusts health in interpolated years to follow the PhRMA series.
Within reported SIC years:
  - company funds per line; missing -> line total x its company/total ratio interpolated over years;
    still missing -> the line's share of all-industry company funds interpolated over years.
  - top-level lines are scaled to sum to the all-industry company total.
  - splits inside a line use the sub-lines where published, else interpolated sub-line ratios.
"""
import numpy as np
import pandas as pd
from plotlib import DATA

DOMS = ["health", "software", "hardware", "defense", "energy", "industrial", "agenv", "general"]
SIC_YEARS = list(range(1956, 1999))

IRIS_CODE_KEY = {
    "13,29": "petro", "20,21": "food", "22,23": "textiles", "24,25": "lumber", "26": "paper", "28": "chem",
    "283": "drugs", "30": "rubber", "32": "stone", "33": "primet", "34": "fabmet", "35": "mach", "357": "office",
    "36": "elec", "361-64,369": "othelec", "37": "transp", "371": "mv", "372,376": "aircraft",
    "373-75,379": "othtrans", "38": "instr", "381-82": "sciinstr", "384-87": "optinstr", "737": "compserv",
    "48": "commun", "80": "health", "49": "elecgas",
}


def iris_key(code, label):
    if isinstance(code, str) and code.strip() in IRIS_CODE_KEY:
        return IRIS_CODE_KEY[code.strip()]
    lab = str(label).strip().lower()
    if lab == "all industries":
        return "total"
    if lab.startswith("nonmanufacturing"):
        return "nonmfg"
    if lab.startswith("other manufacturing"):
        return "othmfg"
    return None


def load():
    d = pd.read_csv(DATA / "sird_scan_by_industry.csv")
    d = d[d.preferred == 1].copy()
    d["v"] = pd.to_numeric(d.value_usd_millions_nominal, errors="coerce")
    p = d.pivot_table(index="year", columns=["measure", "industry_key"], values="v", aggfunc="first")
    ir = pd.read_csv(DATA / "sird_hist_by_industry.csv")
    ir = ir[(ir.is_primary == 1) & (ir.classification == "SIC") & ir.measure.isin(["total", "company_nonfederal", "federal"])].copy()
    ir["key"] = [iris_key(c, l) for c, l in zip(ir.sic_code_native, ir.industry_label_native)]
    ir["v"] = pd.to_numeric(ir.value_usd_millions_nominal, errors="coerce")
    ir = ir.dropna(subset=["key"])
    q = ir.pivot_table(index="year", columns=["measure", "key"], values="v", aggfunc="first")
    p = p.reindex(index=sorted(set(p.index) | set(q.index)))
    for col in q.columns:
        if col not in p.columns:
            p[col] = np.nan
        p[col] = p[col].fillna(q[col].reindex(p.index))
    return p


def company_series(p, key, years):
    comp = p.get(("company_nonfederal", key), pd.Series(dtype=float)).reindex(years)
    tot = p.get(("total", key), pd.Series(dtype=float)).reindex(years)
    ratio = (comp / tot).interpolate(limit_direction="both")
    return comp.fillna(tot * ratio)


def sic_shares():
    p = load()
    years = SIC_YEARS
    T = p[("company_nonfederal", "total")].reindex(years)
    T = T.fillna(p[("total", "total")].reindex(years) * (p[("company_nonfederal", "total")] / p[("total", "total")]).reindex(years).interpolate(limit_direction="both"))
    C = {k: company_series(p, k, years) for k in
         ["food", "textiles", "lumber", "paper", "chem", "drugs", "petro", "rubber", "stone", "primet", "fabmet", "mach",
          "office", "elec", "othelec", "transp", "aircraft", "mv", "othtrans", "mvtrans", "instr", "sciinstr", "optinstr",
          "othmfg", "nonmfg", "compserv", "commun", "health", "elecgas"]}

    def share_fill(s):
        sh = (s / T).interpolate(limit_direction="both")
        return s.fillna(sh * T)

    transp = C["transp"].fillna(C["aircraft"] + C["mvtrans"].fillna(C["mv"] + C["othtrans"]))
    top = {k: C[k] for k in ["food", "textiles", "lumber", "paper", "chem", "petro", "rubber", "stone", "primet", "fabmet",
                             "mach", "elec", "instr", "othmfg", "nonmfg"]}
    top["transp"] = transp
    S = pd.DataFrame({k: share_fill(v) for k, v in top.items()})
    S = S.mul(T / S.sum(axis=1), axis=0)

    def ratio(num, den):
        return (num / den).clip(0, 1).interpolate(limit_direction="both")

    r_drugs, r_office = ratio(C["drugs"], C["chem"]), ratio(C["office"], C["mach"])
    r_othelec, r_air = ratio(C["othelec"], C["elec"]), ratio(C["aircraft"], transp)
    r_sci, r_opt = ratio(C["sciinstr"], C["instr"]), ratio(C["optinstr"], C["instr"])
    nmd = pd.DataFrame({k: C[k] for k in ["compserv", "commun", "health", "elecgas", "nonmfg"]})
    nm_sw = ratio(nmd.compserv + nmd.commun, nmd.nonmfg)   # 1995-98 detail, held back before 1995
    nm_he, nm_en = ratio(nmd.health, nmd.nonmfg), ratio(nmd.elecgas, nmd.nonmfg)

    out = pd.DataFrame(0.0, index=years, columns=DOMS)
    out["health"] += S.chem * r_drugs + S.instr * r_opt * 0.5 + S.nonmfg * nm_he
    out["industrial"] += S.chem * (1 - r_drugs) + S.instr * r_opt * 0.5
    out["hardware"] += S.mach * r_office + S.elec * (1 - r_othelec) + S.instr * r_sci * 0.5
    out["industrial"] += S.mach * (1 - r_office) + S.elec * r_othelec
    out["defense"] += S.transp * r_air + S.instr * r_sci * 0.5
    out["industrial"] += S.transp * (1 - r_air) + S.instr * (1 - r_sci - r_opt).clip(lower=0)
    out["energy"] += S.petro + S.nonmfg * nm_en
    out["agenv"] += S.food
    out["industrial"] += S.textiles + S.lumber + S.paper + S.rubber + S.stone + S.primet + S.fabmet + S.othmfg
    out["software"] += S.nonmfg * nm_sw
    out["general"] += S.nonmfg * (1 - nm_sw - nm_he - nm_en).clip(lower=0)
    return out.div(out.sum(axis=1), axis=0)


def naics_shares(split3345):
    """IRIS SIRD NAICS 2004-07, company funds. split3345: dict domain -> share of NAICS 3345 (from BERD)."""
    ir = pd.read_csv(DATA / "sird_hist_by_industry.csv")
    ir = ir[(ir.is_primary == 1) & (ir.classification == "NAICS") & (ir.measure.isin(["company_nonfederal", "total"]))].copy()
    ir["v"] = pd.to_numeric(ir.value_usd_millions_nominal, errors="coerce")
    ir["code"] = ir.sic_code_native.astype(str).str.replace(" ", "")
    years = [2004, 2005, 2006, 2007]
    p = ir.pivot_table(index="year", columns=["measure", "code"], values="v", aggfunc="first").reindex(years)

    def comp(code):
        c = p.get(("company_nonfederal", code), pd.Series(np.nan, index=years))
        t = p.get(("total", code), pd.Series(np.nan, index=years))
        r = (c / t).interpolate(limit_direction="both")
        return c.fillna(t * r).interpolate(limit_direction="both").fillna(0)

    ALL, MFG, NON = "21-23,31-33,42,44-81", "31-33", "21-23,42,44-81"
    named_mfg = {"3254": "health", "3391": "health", "334": None, "3364": "defense", "324": "energy",
                 "311": "agenv", "312": "agenv"}
    named_non = {"51": "software", "5415": "software", "621-23": "health", "22": "energy", "21": "energy"}
    out = pd.DataFrame(0.0, index=years, columns=DOMS)
    tot = comp(ALL)
    mfg_named = 0
    for code, d in named_mfg.items():
        v = comp(code)
        mfg_named = mfg_named + v
        if code == "334":
            v3345 = comp("3345")
            out["hardware"] += v - v3345
            for dd, sh in split3345.items():
                out[dd] += v3345 * sh
        else:
            out[d] += v
    out["industrial"] += (comp(MFG) - mfg_named).clip(lower=0)
    non_named = 0
    for code, d in named_non.items():
        v = comp(code)
        non_named = non_named + v
        out[d] += v
    out["general"] += (comp(NON) - non_named).clip(lower=0)
    out = out.clip(lower=0)
    print("NAICS 2004-07 company: sum of domains vs total", (out.sum(axis=1) / tot).round(3).to_dict())
    return out.div(out.sum(axis=1), axis=0)


def business_pre2008(split3345):
    sic, nai = sic_shares(), naics_shares(split3345)
    out = pd.DataFrame(index=range(1953, 2008), columns=DOMS, dtype=float)
    flag = {}
    for y in out.index:
        if y in sic.index:
            out.loc[y], flag[y] = sic.loc[y], "reported"
        elif y in nai.index:
            out.loc[y], flag[y] = nai.loc[y], "reported"
        elif y < 1956:
            out.loc[y], flag[y] = sic.loc[1956], "held"
        else:
            w = (y - 1998) / (2004 - 1998)
            out.loc[y] = (1 - w) * sic.loc[1998] + w * nai.loc[2004]
            flag[y] = "interpolated"
    return out, flag


if __name__ == "__main__":
    s = sic_shares()
    print((s.loc[[1956, 1960, 1970, 1980, 1990, 1996, 1997, 1998]] * 100).round(1).to_string())

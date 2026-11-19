"""Business (company and other nonfederal) R&D by application domain, 1953-2007, from the SIC-basis SIRD
industry series transcribed from NSF 'Research and Development in Industry' volumes (1956-96).

Returns a DataFrame year x domain of shares (sum 1) and a flag per year:
  1957-96 'reported' (industry data, with some lines filled as described below)
  1997-2007 'interpolated' (linear in shares between 1996 and the 2008 BERD split)
  1953-56 'held' (1957 shares)
Within 1957-96:
  - company funds per line; missing -> line total x its company/total ratio interpolated over years;
    still missing -> the line's share of all-industry company funds interpolated over years.
  - top-level lines are scaled to sum to the all-industry company total.
  - splits inside a line use the sub-lines where published, else interpolated sub-line ratios.
"""
import numpy as np
import pandas as pd
from plotlib import DATA

DOMS = ["health", "software", "hardware", "defense", "energy", "industrial", "agenv", "general"]


def load():
    d = pd.read_csv(DATA / "sird_scan_by_industry.csv")
    d = d[d.preferred == 1].copy()
    d["v"] = pd.to_numeric(d.value_usd_millions_nominal, errors="coerce")
    p = d.pivot_table(index="year", columns=["measure", "industry_key"], values="v", aggfunc="first")
    return p


def company_series(p, key, years):
    comp = p.get(("company_nonfederal", key), pd.Series(dtype=float)).reindex(years)
    tot = p.get(("total", key), pd.Series(dtype=float)).reindex(years)
    ratio = (comp / tot).interpolate(limit_direction="both")
    est = comp.isna()
    comp = comp.fillna(tot * ratio)
    return comp, est


def sic_shares():
    p = load()
    years = list(range(1957, 1997))
    T = p[("company_nonfederal", "total")].reindex(years)
    T = T.fillna(p[("total", "total")].reindex(years) * (p[("company_nonfederal", "total")] / p[("total", "total")]).reindex(years).interpolate(limit_direction="both"))
    C = {}
    for k in ["food", "textiles", "lumber", "paper", "chem", "drugs", "petro", "rubber", "stone", "primet", "fabmet", "mach",
              "office", "elec", "othelec", "transp", "aircraft", "mv", "othtrans", "mvtrans", "instr", "sciinstr", "optinstr",
              "othmfg", "nonmfg", "compserv", "commun", "health", "elecgas", "medoffices"]:
        C[k] = company_series(p, k, years)[0]

    def share_fill(s):  # fill remaining gaps via the line's share of the all-industry total
        sh = (s / T).interpolate(limit_direction="both")
        return s.fillna(sh * T)

    # transport: before 1972 only aircraft + (motor vehicles and other transport combined)
    transp = C["transp"].copy()
    alt = C["aircraft"] + C["mvtrans"].fillna(C["mv"] + C["othtrans"])
    transp = transp.fillna(alt)
    top = {
        "food": C["food"], "textiles": C["textiles"], "lumber": C["lumber"], "paper": C["paper"], "chem": C["chem"],
        "petro": C["petro"], "rubber": C["rubber"], "stone": C["stone"], "primet": C["primet"], "fabmet": C["fabmet"],
        "mach": C["mach"], "elec": C["elec"], "transp": transp, "instr": C["instr"], "othmfg": C["othmfg"], "nonmfg": C["nonmfg"],
    }
    top = {k: share_fill(v) for k, v in top.items()}
    S = pd.DataFrame(top)
    S = S.mul(T / S.sum(axis=1), axis=0)  # scale to all-industry company total

    def ratio(num, den):
        return (num / den).clip(0, 1).interpolate(limit_direction="both")

    r_drugs = ratio(C["drugs"], C["chem"])
    r_office = ratio(C["office"], C["mach"])          # from 1972; held at 1972-74 before
    r_othelec = ratio(C["othelec"], C["elec"])
    r_air = ratio(C["aircraft"], transp)
    r_sci = ratio(C["sciinstr"], C["instr"])
    r_opt = ratio(C["optinstr"], C["instr"])
    # nonmanufacturing composition from 1995-96 detail, held back
    nm = pd.DataFrame({k: C[k] for k in ["compserv", "commun", "health", "elecgas", "nonmfg"]}).loc[1995:1996].mean()
    nm_sw, nm_he, nm_en = (nm.compserv + nm.commun) / nm.nonmfg, nm.health / nm.nonmfg, nm.elecgas / nm.nonmfg

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
    out["general"] += S.nonmfg * (1 - nm_sw - nm_he - nm_en)
    out = out.div(out.sum(axis=1), axis=0)
    return out


def business_pre2008(share2008):
    """share2008: Series of domain shares (all characters pooled) for 2008 from BERD."""
    sic = sic_shares()
    out = pd.DataFrame(index=range(1953, 2008), columns=DOMS, dtype=float)
    flag = {}
    for y in out.index:
        if 1957 <= y <= 1996:
            out.loc[y], flag[y] = sic.loc[y], "reported"
        elif y < 1957:
            out.loc[y], flag[y] = sic.loc[1957], "held"
        else:
            w = (y - 1996) / (2008 - 1996)
            out.loc[y] = (1 - w) * sic.loc[1996] + w * share2008.reindex(DOMS).fillna(0)
            flag[y] = "interpolated"
    return out, flag


if __name__ == "__main__":
    s = sic_shares()
    print((s.loc[[1957, 1960, 1965, 1970, 1975, 1980, 1985, 1990, 1995, 1996]] * 100).round(1).to_string())

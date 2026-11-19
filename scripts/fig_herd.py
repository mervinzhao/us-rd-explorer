"""University R&D (HERD) by harmonized field group and funder."""
import pandas as pd
import matplotlib.pyplot as plt
from plotlib import DATA, SLOTS, GRAY, INK, INK2, GRID, stack, legend, save, deflator, to_real
from crosswalk import GROUPS, group

COLORS = SLOTS + [GRAY]
NOTE = ("Source: NCSES HERD and predecessor survey microdata, FY1973-2024. Dashed lines: FY2010 survey redesign "
        "(non-S&E fields in scope, clinical trials counted, campus-level reporting) and FY2016 field taxonomy revision. "
        "Constant 2017 $ (GDP deflator).")

d = pd.read_csv(DATA / "herd_by_field_source.csv")
d = d[d.finest_level & (d.fiscal_year >= 1973)].copy()
SRC = {"Federal": "Federal", "Federal government": "Federal", "Total": "Total",
       "State and local government": "State & local", "Business": "Business", "Industry": "Business",
       "Institution funds": "Institution", "Nonprofit organizations": "Nonprofit",
       "All other sources": "All other"}
d["src"] = d.source_of_funds_native.map(SRC)
d["grp"] = d.detailed_field_native.map(group)
d["val"] = d.value_usd_thousands_nominal / 1e6  # $B
defl = deflator()


def wide(src):
    w = d[d.src == src].pivot_table(index="fiscal_year", columns="grp", values="val", aggfunc="sum")
    return to_real(w.reindex(columns=GROUPS), defl)


tot, fed = wide("Total"), wide("Federal")
nonfed = tot - fed
BRK = [2009.5, 2015.5]

# Fig 2: total / federal / nonfederal university R&D by field group
fig, axes = plt.subplots(3, 2, figsize=(13, 9.5))
for i, (w, t) in enumerate([(tot, "All university R&D"), (fed, "Federally funded"), (nonfed, "Nonfederally funded")]):
    stack(axes[i, 0], w, COLORS, breaks=BRK)
    stack(axes[i, 1], w, COLORS, share=True, breaks=BRK)
    axes[i, 0].set_ylabel("$B, constant 2017")
    axes[i, 1].set_ylabel("Share")
    axes[i, 0].text(0.02, 0.92, t, transform=axes[i, 0].transAxes, fontsize=13, color=INK, va="top")
legend(fig, GROUPS, COLORS, ncol=5, y=1.04)
fig.text(0.01, -0.02, NOTE, fontsize=8, color=INK2, wrap=True)
fig.tight_layout()
save(fig, "02_herd_by_field")

# Fig 3: federal share of each field's university R&D, 1973-2024 (one line per group, small multiples)
share = (fed / tot)
fig, axes = plt.subplots(3, 3, figsize=(12, 8), sharex=True, sharey=True)
for ax, g, c in zip(axes.flat, GROUPS, COLORS):
    for other in GROUPS:
        ax.plot(share.index, share[other], color=GRID, linewidth=1)
    ax.plot(share.index, share[g], color=c, linewidth=2)
    ax.set_title(g, fontsize=11, color=INK, loc="left")
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    for b in BRK:
        ax.axvline(b, color=INK2, linewidth=0.7, linestyle=(0, (2, 2)))
fig.suptitle("Federal share of university R&D, by field", x=0.01, ha="left", fontsize=13, color=INK)
fig.text(0.01, -0.01, NOTE, fontsize=8, color=INK2, wrap=True)
fig.tight_layout()
save(fig, "03_herd_federal_share_by_field")

# Fig 4: funder mix within each field, FY2010-2024
SRC_ORDER = ["Federal", "Business", "Institution", "State & local", "Nonprofit", "All other"]
SRC_COL = ["#2a78d6", "#e34948", "#eda100", "#a8a7a2", "#008300", "#d6d5d0"]
m = d[(d.fiscal_year >= 2010) & d.src.isin(SRC_ORDER)]
fig, axes = plt.subplots(3, 3, figsize=(12, 8), sharex=True, sharey=True)
for ax, g in zip(axes.flat, GROUPS):
    w = m[m.grp == g].pivot_table(index="fiscal_year", columns="src", values="val", aggfunc="sum").reindex(columns=SRC_ORDER)
    stack(ax, w, SRC_COL, share=True, breaks=[2015.5])
    ax.set_title(g, fontsize=11, color=INK, loc="left")
legend(fig, SRC_ORDER, SRC_COL, y=1.03)
fig.text(0.01, -0.01, "Source: NCSES HERD microdata FY2010-2024 (field x source not collected before FY2010). "
         "Dashed line: FY2016 field taxonomy revision.", fontsize=8, color=INK2)
fig.tight_layout()
save(fig, "04_herd_funder_mix_by_field")

# Data out
tot.assign(series="total").reset_index().melt(id_vars=["fiscal_year", "series"]).to_csv(
    DATA / "harmonized_herd_by_group_real2017.csv", index=False)
print((tot.div(tot.sum(axis=1), axis=0).loc[[1975, 1990, 2005, 2015, 2024]] * 100).round(1).to_string())
print((share.loc[[1975, 1990, 2005, 2015, 2024]] * 100).round(0).to_string())

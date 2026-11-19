"""Business R&D performed in the US by industry group, 2008-2024 (BRDIS/BERD)."""
import pandas as pd
import matplotlib.pyplot as plt
from plotlib import DATA, SLOTS, GRAY, INK, INK2, stack, legend, save, deflator, to_real

ALL, MFG, NONMFG = "21–23, 31–33, 42–81", "31–33", "21–23, 42–81"
G_BIO, G_ICT, G_SW, G_PHYS, G_OTH = ("Bio (pharma, med devices, biotech)", "ICT hardware (semis, comms, other 334)",
                                    "Software & internet (information, computer services)", "Other physical industry",
                                    "Other services")
GROUPS = [G_BIO, G_PHYS, G_SW, G_ICT, G_OTH]  # stack order, matches the headline figure
COLORS = [SLOTS[0], SLOTS[1], SLOTS[2], SLOTS[6], GRAY]
NEED = [ALL, MFG, NONMFG, "3254", "3391", "541714", "334", "3345", "51", "5415"]

raw = pd.read_csv(DATA / "berd_by_industry.csv")
raw = raw[(raw.is_primary == 1) & (raw.year >= 2008)]


def table(measure, years):
    return (raw[(raw.measure == measure) & raw.industry_code_native.isin(NEED)]
            .pivot_table(index="year", columns="industry_code_native", values="value_usd_millions_nominal",
                         aggfunc="first").reindex(columns=NEED, index=years))


def groups(measure, years=range(2008, 2025)):
    x = table(measure, years)
    filled = x.isna()
    if measure == "total":
        x = x.interpolate(limit_direction="both")  # suppressed cells: linear fill, flagged below
    else:
        # missing component: its total R&D x its mean measure/total ratio over published years
        t = table("total", years).interpolate(limit_direction="both")
        ratio = (x / t).mean()
        x = x.fillna(t * ratio)
    g = pd.DataFrame(index=x.index)
    g[G_BIO] = x["3254"] + x["3391"] + x["541714"]
    g[G_PHYS] = x[MFG] - x["3254"] - x["3391"] - (x["334"] - x["3345"])
    g[G_SW] = x["51"] + x["5415"]
    g[G_ICT] = x["334"] - x["3345"]
    g[G_OTH] = x[NONMFG] - x["51"] - x["5415"] - x["541714"]
    return g / 1000, filled, x[ALL] / 1000


tot, filled, alltot = groups("total")
print("filled cells (total):", {c: list(filled.index[filled[c]]) for c in NEED if filled[c].any()})
print("max |groups - all industries| $B:", (tot.sum(axis=1) - alltot).abs().max().round(3))
defl = deflator()
real = to_real(tot, defl)

fig, axes = plt.subplots(1, 2, figsize=(13, 3.6))
stack(axes[0], real, COLORS, breaks=[2022.5])
stack(axes[1], real, COLORS, share=True, breaks=[2022.5])
axes[0].set_ylabel("$B, constant 2017")
axes[1].set_ylabel("Share")
axes[0].text(0.02, 0.92, "Business R&D performed in the US", transform=axes[0].transAxes, fontsize=13, color=INK, va="top")
for ax in axes:
    ax.set_xticks(range(2008, 2025, 2))
legend(fig, GROUPS, COLORS, ncol=3, y=1.13)
fig.text(0.01, -0.1, "Source: NCSES BRDIS 2008-16 and BERD 2017-24 (NSF 27-300), domestic performance, all funders. "
         "Firms classified by dominant R&D business code; NAICS vintage changes 2009, 2014, 2020. Suppressed cells "
         "linearly filled (pharma 2016, med devices 2008-09 and 2016, biotech services 2008, 2020; instruments 2018). "
         "Dashed: 2023 reporting break (some firms dropped non-R&D spending). Bio includes NAICS 3254, 3391, 541714; "
         "ICT hardware is 334 minus 3345 instruments; software & internet is 51 plus 5415.",
         fontsize=8, color=INK2, wrap=True)
fig.tight_layout()
save(fig, "08_business_rd_by_industry")

real.reset_index().melt(id_vars="year", var_name="group", value_name="usd_billions_2017").to_csv(
    DATA / "harmonized_berd_by_group_real2017.csv", index=False)
print((tot.div(tot.sum(axis=1), axis=0) * 100).round(1).loc[[2008, 2012, 2016, 2020, 2024]].to_string())
print(real.round(0).loc[[2008, 2016, 2024]].to_string())

# Development only, 2015-2024 (industry detail by character of work is thin before 2015)
try:
    dev, dfill, _ = groups("development", range(2015, 2025))
    print("development filled:", {c: list(dfill.index[dfill[c]]) for c in NEED if dfill[c].any()})
    print((dev.div(dev.sum(axis=1), axis=0) * 100).round(1).to_string())
    rdev = to_real(dev, defl)
    fig, axes = plt.subplots(1, 2, figsize=(13, 3.6))
    stack(axes[0], rdev, COLORS, breaks=[2022.5])
    stack(axes[1], rdev, COLORS, share=True, breaks=[2022.5])
    axes[0].set_ylabel("$B, constant 2017")
    axes[1].set_ylabel("Share")
    axes[0].text(0.02, 0.92, "Business development", transform=axes[0].transAxes, fontsize=13, color=INK, va="top")
    legend(fig, GROUPS, COLORS, ncol=3, y=1.13)
    fig.text(0.01, -0.1, "Source: NCSES BERD 2015-24, development performed by business, all funders. Unpublished "
             "development cells (med devices 2015-18, biotech services 2015-19) estimated as that industry's total R&D "
             "times its mean development share in published years.", fontsize=8, color=INK2, wrap=True)
    fig.tight_layout()
    save(fig, "09_business_development_by_industry")
except Exception as e:
    print("dev failed", e)

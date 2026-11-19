"""Federal research obligations by harmonized field group, FY1970-2024."""
import pandas as pd
import matplotlib.pyplot as plt
from plotlib import DATA, SLOTS, GRAY, INK, INK2, GRID, stack, legend, save, deflator, to_real
from crosswalk import GROUPS, LENS, LENS_ORDER

COLORS = SLOTS + [GRAY]
BRK = [2003.5, 2020.5]
NOTE = ("Source: NCSES Survey of Federal Funds for R&D, obligations for research, FY1970-2024 (historical tables "
        "nsf03325; volumes 54-56, 69-74). Dashed lines: FY2004 NIH switch to estimated field codes (moves ~$3B/yr "
        "from biological to medical) and FY2021 field-of-R&D taxonomy (NASA reclassified). Math/computing split "
        "imputed for FY1970-75. Constant 2017 $ (GDP deflator).")

d = pd.read_csv(DATA / "harmonized_fedfunds_by_group.csv")
defl = deflator()


def wide(ch):
    w = d[d.character == ch].pivot(index="fiscal_year", columns="group", values="usd_billions_nominal")
    return to_real(w.reindex(columns=GROUPS), defl)


basic, applied, total = wide("basic"), wide("applied"), wide("research_total")

fig, axes = plt.subplots(2, 2, figsize=(13, 6.6))
for i, (w, t) in enumerate([(basic, "Federal basic research"), (applied, "Federal applied research")]):
    stack(axes[i, 0], w, COLORS, breaks=BRK)
    stack(axes[i, 1], w, COLORS, share=True, breaks=BRK)
    axes[i, 0].set_ylabel("$B, constant 2017")
    axes[i, 1].set_ylabel("Share")
    axes[i, 0].text(0.02, 0.92, t, transform=axes[i, 0].transAxes, fontsize=13, color=INK, va="top")
legend(fig, GROUPS, COLORS, ncol=5, y=1.07)
fig.text(0.01, -0.04, NOTE, fontsize=8, color=INK2, wrap=True)
fig.tight_layout()
save(fig, "05_fed_research_by_field")

# Small multiples: real federal research (basic + applied) by group
fig, axes = plt.subplots(3, 3, figsize=(12, 8), sharex=True)
for ax, g, c in zip(axes.flat, GROUPS, COLORS):
    ax.fill_between(basic.index, 0, basic[g], color=c, alpha=0.95, linewidth=0)
    ax.fill_between(total.index, basic[g], total[g], color=c, alpha=0.35, linewidth=0)
    ax.set_title(g, fontsize=11, color=INK, loc="left")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_xlim(1970, 2024)
    ax.set_ylim(0, None)
    for b in BRK:
        ax.axvline(b, color=INK2, linewidth=0.7, linestyle=(0, (2, 2)))
fig.suptitle("Federal research obligations by field, $B constant 2017 (dark: basic, light: applied). "
             "Each panel has its own scale.", x=0.01, ha="left", fontsize=12, color=INK)
fig.text(0.01, -0.03, NOTE, fontsize=8, color=INK2, wrap=True)
fig.tight_layout()
save(fig, "06_fed_research_by_field_multiples")

# Lens: atoms / bits / bio / people
LCOL = [SLOTS[0], SLOTS[1], SLOTS[2], SLOTS[3], GRAY]
fig, axes = plt.subplots(2, 2, figsize=(13, 6.6))
for i, (w, t) in enumerate([(basic, "Federal basic research"), (applied, "Federal applied research")]):
    lw = w.T.groupby(LENS).sum().T.reindex(columns=LENS_ORDER)
    stack(axes[i, 0], lw, LCOL, breaks=[2020.5])
    stack(axes[i, 1], lw, LCOL, share=True, breaks=[2020.5])
    axes[i, 0].set_ylabel("$B, constant 2017")
    axes[i, 1].set_ylabel("Share")
    axes[i, 0].text(0.02, 0.92, t, transform=axes[i, 0].transAxes, fontsize=13, color=INK, va="top")
legend(fig, ["Bio (life sciences)", "Atoms (physical, engineering, earth)", "Bits (computing, math)",
             "People (social, behavioral)", "Other"], LCOL, y=1.04)
fig.text(0.01, -0.03, NOTE, fontsize=8, color=INK2, wrap=True)
fig.tight_layout()
save(fig, "07_fed_research_lens")

for nm, w in [("basic", basic), ("applied", applied), ("total", total)]:
    lw = w.T.groupby(LENS).sum().T.reindex(columns=LENS_ORDER)
    print(nm, "share %\n", (lw.div(lw.sum(axis=1), axis=0) * 100).round(1).loc[[1970, 1980, 1990, 2000, 2010, 2024]].to_string())
print("real $B total research by group\n", total.round(1).loc[[1970, 1980, 1990, 2000, 2004, 2010, 2020, 2024]].to_string())

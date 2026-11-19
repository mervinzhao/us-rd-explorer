"""Headline remake of the original 3x2 slide with field / industry splits instead of funders."""
import pandas as pd
import matplotlib.pyplot as plt
from plotlib import DATA, SLOTS, GRAY, INK, INK2, stack, save, deflator, to_real
from crosswalk import GROUPS, LENS, LENS_ORDER
import matplotlib

defl = deflator()
f = pd.read_csv(DATA / "harmonized_fedfunds_by_group.csv")
b = pd.read_csv(DATA / "harmonized_berd_by_group_real2017.csv")

LCOL = [SLOTS[0], SLOTS[1], SLOTS[2], SLOTS[3], GRAY]  # Bio, Atoms, Bits, People, Other


def lens(ch):
    w = f[f.character == ch].pivot(index="fiscal_year", columns="group", values="usd_billions_nominal")
    w = to_real(w.reindex(columns=GROUPS), defl)
    return w.T.groupby(LENS).sum().T.reindex(columns=LENS_ORDER)


BORDER = ["Bio (pharma, med devices, biotech)", "Other physical industry",
          "Software & internet (information, computer services)", "ICT hardware (semis, comms, other 334)",
          "Other services"]
BLAB = ["Bio", "Other physical industry", "Software & internet", "ICT hardware", "Other services"]
BCOL = [SLOTS[0], SLOTS[1], SLOTS[2], SLOTS[6], GRAY]
bw = b.pivot(index="year", columns="group", values="usd_billions_2017").reindex(columns=BORDER)

fig, axes = plt.subplots(3, 2, figsize=(13, 10))
rows = [(lens("basic"), LCOL, "Federal basic research, by field", [2020.5]),
        (lens("applied"), LCOL, "Federal applied research, by field", [2020.5]),
        (bw, BCOL, "Business R&D, by industry", [2022.5])]
for i, (w, cols, title, brk) in enumerate(rows):
    stack(axes[i, 0], w, cols, breaks=brk)
    stack(axes[i, 1], w, cols, share=True, breaks=brk)
    axes[i, 0].set_ylabel("$B, constant 2017")
    axes[i, 1].set_ylabel("Share")
    axes[i, 0].set_title(title, loc="left", fontsize=13, color=INK)
    labs = ["Bio", "Atoms", "Bits", "People", "Other"] if i < 2 else BLAB
    if i != 1:
        h = [matplotlib.patches.Patch(facecolor=c, label=l) for l, c in zip(labs, cols)]
        axes[i, 1].legend(handles=h[::-1], loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=9.5)
for ax in axes[:2].flat:
    ax.set_xlim(1970, 2024)
fig.text(0.01, -0.035,
         "Bio = life sciences; Atoms = physical sciences, engineering, earth/atmos/ocean; Bits = computer and information "
         "sciences, math and statistics; People = psychology, social sciences.\n"
         "Federal: NCSES Federal Funds survey, research obligations FY1970-2024 (math/CS split imputed FY1970-75; dashed: FY2021 "
         "taxonomy change). Business: NCSES BRDIS/BERD 2008-24, domestic performance, all funders\n"
         "(Bio = NAICS 3254+3391+541714; ICT hardware = 334 minus 3345; software & internet = 51+5415; dashed: 2023 "
         "reporting break). Business R&D has no field-of-science split, only industry. Constant 2017 $ (GDP deflator).",
         fontsize=8, color=INK2)
fig.tight_layout()
save(fig, "00_headline_fields_and_industries")

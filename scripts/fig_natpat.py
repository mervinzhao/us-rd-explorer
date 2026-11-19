"""Refresh of the original slide: US R&D by character of work x source of funds, 1953-2024."""
import pandas as pd
import matplotlib.pyplot as plt
from plotlib import DATA, stack, legend, save, INK, INK2

d = pd.read_csv(DATA / "natpat_character_source_performer.csv")
d = d[(d.performer == "all_performers") & (d.source_of_funds != "all_sources")]

SRC = ["federal", "business", "higher_education", "nonprofit", "nonfederal_government"]
LAB = ["Federal", "Business", "Higher ed", "Nonprofit", "State & local gov"]
# Keep the original slide's funder colors (blue/red/yellow/green), stepped to the reference palette.
COL = ["#2a78d6", "#e34948", "#eda100", "#008300", "#a8a7a2"]
ROWS = [("basic", "Basic research"), ("applied", "Applied research"), ("development", "Development")]

fig, axes = plt.subplots(3, 2, figsize=(13, 9.5), gridspec_kw={"width_ratios": [1, 1]})
for i, (ch, title) in enumerate(ROWS):
    w = (d[d.character == ch].pivot_table(index="year", columns="source_of_funds",
                                         values="value_usd_millions_constant2017", aggfunc="sum")
         .reindex(columns=SRC) / 1000)
    stack(axes[i, 0], w, COL, breaks=[2022.5], shade=(2022.5, 2024))
    stack(axes[i, 1], w, COL, share=True, breaks=[2022.5], shade=(2022.5, 2024))
    axes[i, 0].set_ylabel("$B, constant 2017")
    axes[i, 1].set_ylabel("Share")
    axes[i, 0].text(0.02, 0.92, title, transform=axes[i, 0].transAxes, fontsize=13, color=INK, va="top")
legend(fig, LAB, COL, y=1.02)
fig.text(0.01, -0.01, "Source: NCSES National Patterns of R&D Resources 2023-24 (NSF 26-313), all performers. "
         "Shaded: 2023 preliminary, 2024 estimate; dashed line marks the 2023 business-survey break. "
         "'Business' includes foreign business funding.", fontsize=8, color=INK2)
fig.tight_layout()
save(fig, "01_natpat_character_by_funder")

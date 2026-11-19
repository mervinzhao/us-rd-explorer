"""Shared plotting helpers: stacked-area grids, absolute (constant 2017 $) and share."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA, FIGS = ROOT / "data", ROOT / "figs"

# Reference categorical palette (dataviz skill), slots 1-8, in fixed order.
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
GRAY = "#a8a7a2"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def deflator():
    d = pd.read_csv(DATA / "natpat_deflator.csv")
    return d.set_index("year")["deflator"]  # 2017 = 1.0


def to_real(wide, defl):
    """wide: index=year, nominal values. Returns constant-2017 values."""
    return wide.div(defl.reindex(wide.index), axis=0)


def stack(ax, wide, colors, share=False, breaks=(), shade=None):
    w = wide.fillna(0)
    if share:
        w = w.div(w.sum(axis=1), axis=0)
    ax.stackplot(w.index, w.T.values, colors=colors, alpha=0.9, linewidth=0.6, edgecolor="white")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_xlim(w.index.min(), w.index.max())
    if share:
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    for b in breaks:
        ax.axvline(b, color=INK2, linewidth=0.8, linestyle=(0, (2, 2)))
    if shade is not None:
        ax.axvspan(shade[0], shade[1], color="#000000", alpha=0.06, linewidth=0)


def legend(fig, labels, colors, ncol=None, y=0.995):
    handles = [matplotlib.patches.Patch(facecolor=c, label=l) for l, c in zip(labels, colors)]
    fig.legend(handles=handles, loc="upper center", ncol=ncol or len(labels), frameon=False,
               bbox_to_anchor=(0.5, y), fontsize=9.5)


def save(fig, name):
    FIGS.mkdir(exist_ok=True)
    fig.savefig(FIGS / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

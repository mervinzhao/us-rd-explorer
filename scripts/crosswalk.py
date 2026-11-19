"""Harmonized field groups across NCSES taxonomies (HERD 1973-2024, Federal Funds 1970s-2024).

Groups (stack order = categorical slot order):
  1 Medical & health          medical sciences, health sciences, clinical
  2 Biological & ag           biological/biomedical sciences, agriculture, natural resources, other life
  3 Physical sciences         physics, chemistry, astronomy, materials science, other physical
  4 Engineering               all engineering subfields
  5 Earth, atmos & ocean      environmental sciences / geosciences
  6 Computing                 computer (and information) sciences
  7 Math & statistics
  8 Social & behavioral       psychology, social sciences
  9 Other                     other sciences n.e.c., non-S&E (HERD from FY2003)

Four-way lens: atoms = 3+4+5, bits = 6+7, bio = 1+2, people = 8 (+9 shown separately).
"""
import re

GROUPS = ["Medical & health", "Biological & ag", "Physical sciences", "Engineering",
          "Earth, atmos & ocean", "Computing", "Math & statistics", "Social & behavioral", "Other"]
LENS = {"Medical & health": "Bio", "Biological & ag": "Bio", "Physical sciences": "Atoms",
        "Engineering": "Atoms", "Earth, atmos & ocean": "Atoms", "Computing": "Bits",
        "Math & statistics": "Bits", "Social & behavioral": "People", "Other": "Other"}
LENS_ORDER = ["Bio", "Atoms", "Bits", "People", "Other"]


def group(label: str) -> str:
    s = label.lower()
    if s.startswith("life sciences"):
        if re.search(r"medical sciences|health sciences|clinical", s) and "biomedical sciences" not in s:
            return "Medical & health"
        return "Biological & ag"
    if s.startswith("physical sciences"):
        return "Physical sciences"
    if s.startswith("engineering"):
        return "Engineering"
    if s.startswith(("environmental sciences", "geosciences")):
        return "Earth, atmos & ocean"
    if s.startswith("computer"):
        return "Computing"
    if s.startswith(("mathematic",)):
        return "Math & statistics"
    if s.startswith(("psychology", "social sciences")):
        return "Social & behavioral"
    if s.startswith(("other sciences", "non-s&e")):
        return "Other"
    raise ValueError(f"unmapped field: {label}")

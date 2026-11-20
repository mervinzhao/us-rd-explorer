"""Inject the domain cube into the explorer template."""
import json
import pandas as pd
from plotlib import DATA, ROOT

c = pd.read_csv(DATA / "domain_cube.csv")
years = sorted(c.year.unique())
defl = pd.read_csv(DATA / "natpat_deflator.csv").set_index("year").deflator
DOMAINS = [
    ("health", "Health & life sciences", "var(--d1)",
     "Federal: HHS (NIH, BARDA, CDC), VA, Defense Health Agency. Business: pharmaceuticals and biologics (NAICS 3254), biotech R&D firms (541714), medical devices (3391, 334510/17), health care. Universities: medical, health and biological sciences, bioengineering."),
    ("industrial", "Industrial & transportation", "var(--d2)",
     "Federal: DOT, NIST. Business: chemicals other than pharma, machinery, motor vehicles, metals and the rest of manufacturing. Universities: chemical, civil, mechanical, materials and industrial engineering, materials science."),
    ("software", "Software & internet", "var(--d3)",
     "Federal: research in computer and information sciences, whichever agency funds it. Business: the information sector (software publishers, internet, data processing and hosting, telecom) and computer systems design (5415). Universities: computer and information sciences."),
    ("energy", "Energy", "var(--d4)",
     "Federal: DOE energy offices (efficiency and renewables, fossil, nuclear, electricity, ARPA-E), NRC, TVA. Business: utilities, oil and gas extraction, petroleum refining, turbines."),
    ("defense", "Defense & space", "var(--d5)",
     "Federal: DOD (excluding the Defense Health Agency), NASA, DOE's NNSA, DHS. Business: aerospace (3364), guidance and navigation instruments, military vehicles. Universities: aerospace engineering."),
    ("agenv", "Agriculture & environment", "var(--d6)",
     "Federal: USDA, Interior, EPA, NOAA. Business: food and beverage, agricultural chemicals and machinery. Universities: agricultural and natural resource sciences, geosciences, atmospheric and ocean sciences."),
    ("hardware", "Electronics & computing hardware", "var(--d7)",
     "Business: semiconductors, computers, communications equipment and other electronics (NAICS 334, excluding electromedical and navigation), semiconductor machinery. Universities: electrical engineering. No federal agency has this mission."),
    ("general", "General science & other", "var(--d8)",
     "Federal: NSF (other than computer science), DOE Office of Science, Smithsonian, and smaller agencies. Business: R&D services firms outside biotech, finance and other services. Universities: physics, chemistry, astronomy, mathematics, social sciences, psychology and non-science fields."),
]
DOM_ORDER = ["agenv", "health", "software", "hardware", "energy", "defense", "industrial", "general"]
DOM_SHORT = {"agenv": "Ag & environment", "health": "Health", "software": "Software", "hardware": "Hardware",
             "energy": "Energy", "defense": "Defense & space", "industrial": "Industrial", "general": "General & other"}
DOMAINS = sorted([(k, l, f"var(--dom-{k})", d) for k, l, _, d in DOMAINS], key=lambda t: DOM_ORDER.index(t[0]))
FUND = ["federal", "business", "higher_education", "nonprofit", "nonfederal_government"]
out = {"years": [int(y) for y in years], "deflator": [round(float(defl[y]), 5) for y in years],
       "domains": [dict(key=k, label=l, color=col, desc=d, short=DOM_SHORT[k]) for k, l, col, d in DOMAINS],
       "business_est": [[1953, 1955], [1999, 2003]], "cube": {}}
gdp = pd.read_csv(DATA / "natpat_deflator.csv").set_index("year").gdp_usd_billions_nominal
out["gdp"] = [round(float(gdp[y]), 1) for y in years]
for ch in ["basic", "applied", "development"]:
    out["cube"][ch] = {}
    for f in FUND:
        out["cube"][ch][f] = {}
        for k, *_ in DOMAINS:
            x = c[(c.character == ch) & (c.source == f) & (c.domain == k)].set_index("year").reindex(years).value
            out["cube"][ch][f][k] = [round(float(v), 1) if v and abs(v) >= 0.05 else 0 for v in x.fillna(0)]
out["notes"] = {
    "basic": "Mostly health and general science, with software a small slice.",
    "applied": "",
    "development": "Development is mostly business product engineering: software, electronics, health and defense.",
}
# business development panel (from the earlier build)
b = pd.read_csv(DATA / "berd_by_industry.csv")
b = b[(b.is_primary == 1) & (b.measure == "development")]
LY = int(b.year.max())
v = b[b.year == LY].drop_duplicates("industry_code_native").set_index("industry_code_native").value_usd_millions_nominal
ITEMS = [
    ("Web search, social media and other internet (other 51)", "other 51", "sw"),
    ("Software publishers (5112)", "5112", "sw"),
    ("Data processing and cloud hosting (518)", "518", "sw"),
    ("Computer systems design (5415)", "5415", "sw"),
    ("Semiconductors and components (3344)", "3344", "ict"),
    ("Computers and other electronics (other 334)", "other 334", "ict"),
    ("Communications equipment (3342)", "3342", "ict"),
    ("Pharmaceuticals and biologics (3254)", "3254", "bio"),
    ("Medical equipment (3391)", "3391", "bio"),
    ("Biotech R&D firms (541714)", "541714", "bio"),
    ("Aerospace (3364)", "3364", "def"),
    ("Motor vehicles and parts (3361-63)", "3361–63", "phys"),
    ("Machinery (333)", "333", "phys"),
    ("Finance and insurance (52)", "52", "oth"),
]
tot = float(v["21–23, 31–33, 42–81"])
items = [{"label": l, "value": round(float(v[cd]) / 1000, 1), "group": g} for l, cd, g in ITEMS]
items.append({"label": "All other industries", "value": round(tot / 1000 - sum(i["value"] for i in items), 1), "group": "rest"})
out["busdev"] = {"year": LY, "total": round(tot / 1000, 1), "items": items}

# discipline tab
dc = pd.read_csv(DATA / "discipline_cube.csv")
dyears = sorted(dc.year.unique())
DISC = [
    ("life", "Life sciences", "var(--d1)", "Medical, health, biological and agricultural sciences, environmental biology."),
    ("physical", "Physical sciences", "var(--d2)", "Physics, chemistry, astronomy, materials science."),
    ("computing", "Computer sciences", "var(--d3)", "Computer and information sciences."),
    ("engineering", "Engineering", "var(--d4)", "All engineering fields: aerospace, chemical, civil, electrical, mechanical, materials, industrial, bioengineering."),
    ("social", "Psychology & social sciences", "var(--d5)", "Psychology, economics, political science, sociology, anthropology."),
    ("earth", "Earth, atmosphere & ocean", "var(--d6)", "Geological, atmospheric and ocean sciences."),
    ("math", "Mathematics & statistics", "var(--d7)", "Mathematics and statistics."),
    ("other", "Other fields", "var(--d8)", "Sciences not elsewhere classified, and (universities from FY2003) business, education, humanities, law and other non-science fields."),
    ("unclassified", "Business (no discipline data)", "var(--hatch-fg)", "Business-funded research. No survey classifies company research by discipline."),
]
DISC_ORDER = ["life", "physical", "engineering", "earth", "math", "computing", "social", "other", "unclassified"]
DISC_SHORT = {"life": "Life sciences", "physical": "Physical", "engineering": "Engineering", "earth": "Earth sciences",
              "math": "Math", "computing": "Computing", "social": "Social sciences", "other": "Other", "unclassified": "Business"}
DISC = sorted([(k, l, col if k == "unclassified" else f"var(--disc-{k})", d) for k, l, col, d in DISC], key=lambda t: DISC_ORDER.index(t[0]))
out["disc"] = {"years": [int(y) for y in dyears], "gdp": [round(float(gdp[y]), 1) for y in dyears],
               "deflator": [round(float(defl[y]), 5) for y in dyears],
               "groups": [dict(key=k, label=l, color=col, desc=d, short=DISC_SHORT[k]) for k, l, col, d in DISC], "cube": {}}
for ch in ["basic", "applied"]:
    out["disc"]["cube"][ch] = {}
    for f in FUND:
        out["disc"]["cube"][ch][f] = {}
        for k, *_ in DISC:
            x = dc[(dc.character == ch) & (dc.source == f) & (dc.discipline == k)].set_index("year").reindex(dyears).value
            out["disc"]["cube"][ch][f][k] = [round(float(v), 1) if v and abs(v) >= 0.05 else 0 for v in x.fillna(0)]

tpl = (ROOT / "dashboard" / "explorer_head.html").read_text() + (ROOT / "dashboard" / "explorer_script.html").read_text()
html = tpl.replace("/*__DATA__*/null", json.dumps(out, separators=(",", ":")))
# claude.ai artifact version (the artifact host supplies the document skeleton)
(ROOT / "dashboard" / "us-rd-explorer.html").write_text(html)
# standalone page for GitHub Pages
head, body = html.split('<div id="root"></div>', 1)
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="robots" content="noindex">\n'
        '<meta name="description" content="US R&amp;D 1953-2024 by type of work, funder, application domain and discipline.">\n'
        + head + '<style>html,body{margin:0}</style>\n</head>\n<body>\n<div id="root"></div>' + body + '\n</body>\n</html>\n')
(ROOT / "index.html").write_text(page)
print("bytes", len(html))

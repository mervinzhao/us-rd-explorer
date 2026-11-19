# US R&D Explorer

An interactive page of US R&D from 1953 to 2024, split three ways (by type of work, by who pays for it, and by what it is for or which discipline it sits in). The page is `index.html`, a single self-contained file (React from cdnjs, the data inlined), so it runs as-is on GitHub Pages.

The totals are NCSES National Patterns of R&D Resources. National Patterns splits US R&D by character of work (basic research, applied research, development), source of funds and performer, but not by field or industry. Every other split here is an estimate: for each funder and type of work I estimate the share going to each domain or discipline from the surveys that do classify spending, and apply that share to the National Patterns total. Read the results as scale, not as exact accounting.

This is a personal analysis of public data.

## The two views

By application groups R&D by what it is for, in eight domains (health and life sciences, software and internet, electronics and computing hardware, defense and space, energy, industrial and transportation, agriculture and environment, general science and other).
- Federal money goes by the mission of the agency that obligates it (NIH is health, DOD is defense, DOE's energy offices are energy, NSF and DOE's Office of Science are general science), except that federal research in computer and information sciences is moved into software wherever it is funded.
- Business money (company funds only, since federally funded business R&D already sits with the federal source) goes by the industry of the company doing the work.
- University, state and nonprofit money goes by the field of the university research it pays for.

By discipline covers research only (basic and applied), from 1970, grouped by field of science. No survey classifies development or company-funded research by discipline, so business shows up only as an unclassified band.

## Sources

| Data | Years | Source |
|---|---|---|
| R&D by character, funder and performer | 1953-2024 | NCSES National Patterns 2023-24 (NSF 26-313) |
| Federal research obligations by field | FY1970-2024 | NCSES Federal Funds survey (historical tables NSF 03-325, volumes 54-56 and 69-74) |
| Federal obligations by agency and character | FY1951-2002, FY2005-2024 | Federal Funds historical table A and volume 74 trend tables |
| University R&D by field and funder | FY1972-2024 | HERD and its predecessor survey, institution microdata |
| Business R&D by industry (NAICS) | 1999-2004, 2008-2024 | NCSES SIRD, BRDIS and BERD data tables |
| Business R&D by industry (SIC) | 1956-1996 | NSF *Research and Development in Industry* volumes, transcribed by hand from scans on archive.org |
| Pharmaceutical R&D | 1970-2024 | PhRMA member companies' domestic R&D (Industry Profile and Membership Survey) |

Constant dollars use the GDP deflator that National Patterns publishes (2017 = 1).

## Where the estimates are weakest

- Business before 2008. 1957-96 comes from the SIC industry tables, whose lines are coarser than today's (instruments, for example, are split by assumption between defense, hardware, health and industrial). 1997-2007 is a straight line between the 1996 and 2008 splits, except health, which follows the PhRMA series. 1953-56 holds the 1957 split. The page marks these years with a hatched strip.
- The type-of-work mix inside each business domain is reported only from 2015 and is held at its 2015-17 level before that.
- Federal agency missions hide content (DARPA's computing work counts as defense), and the federal field data have their own breaks (NIH moved to estimated field codes in FY2004, and the field taxonomy changed in FY2021).
- University, state and nonprofit funders get one split for basic, applied and development alike, since HERD does not cross field with type of work.
- 2023 is preliminary and 2024 an estimate in National Patterns, and business R&D from 2023 follows a reporting change.

Each survey's quirks, breaks and checks are in `data/*_NOTES.md`.

## Layout

- `index.html`: the page.
- `data/`: the survey extracts (`natpat_*`, `fedfunds_*`, `herd_*`, `berd_*`, `sird_scan_*`, `phrma_*`), the hand transcriptions of the scanned SIC tables (`data/sird_transcriptions/`), and the model outputs the page is built from (`domain_cube.csv`, `discipline_cube.csv`).
- `scripts/`: extraction, modeling and build scripts. `model_domains.py` and `model_disciplines.py` produce the two cubes and `build_explorer.py` writes `index.html` from `dashboard/explorer_head.html` and `dashboard/explorer_script.html`.
- `figs/`: static versions of the main charts.

To rebuild the page from the data in this repo:

```bash
cd scripts && python3 model_disciplines.py && python3 build_explorer.py
```

`model_domains.py` also reads the raw Federal Funds Excel tables, which are not committed (they are public at the URLs in `data/fedfunds_NOTES.md`).

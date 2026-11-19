# Federal research obligations by field of science and engineering, FY1970-2024

Source survey: NSF/NCSES Survey of Federal Funds for Research and Development ("Federal Funds survey").
Built 2026-11-18. Scripts: `scripts/fedfunds_extract.py` (parse every published table into
`data/fedfunds_candidates.csv`), `scripts/fedfunds_build.py` (select values, checks),
`scripts/fedfunds_agency.py` (agency file). Raw downloads are in `raw/fedfunds/`.

## Outputs

| File | What |
|---|---|
| `fedfunds_research_by_field.csv` | Main series. 6,927 rows. FY1970-2024, characters `basic`, `applied`, `research_total`, every field level published. |
| `fedfunds_research_by_field_agency.csv` | Agency x broad field, FY2019-2024 only (see "Agency file"). |
| `fedfunds_revisions_log.csv` | Every cell where an older publication differs from a newer one by more than rounding. |
| `fedfunds_check_totals_vs_table1.csv` | All-fields totals per year vs Table 1 (character of work trend), plus basic+applied vs total. |
| `fedfunds_check_additivity.csv` | Children that do not sum to their parent beyond rounding (1 row, explained below). |
| `fedfunds_candidates.csv` | Intermediate: every value parsed from every table, including preliminary years and superseded values. |

### Columns of the main file

Requested columns: `fiscal_year`, `character` (basic | applied | research_total), `broad_field_native`,
`detailed_field_native`, `taxonomy_version`, `value_usd_thousands_nominal`, `source_table`, `status`
(all rows are `actual`; preliminary years were excluded).

Extra columns:
- `field_level`: 0 = all fields, 1 = broad field total, 2 = detailed field, 3 = sub-detail (only FY1970-99: the three parts of "Biological and agricultural" in FY1978-99, clinical vs other medical in FY1970-77, history/linguistics/other in FY1970-75). Do not sum across levels.
- `parent_field_native`, `field_key`, `broad_field_key`, `parent_field_key`: `field_key` is a stable id that only absorbs cosmetic relabelling inside one taxonomy (for example "Life sciences, n.e.c." = "Life sciences, nec" = "Other life sciences", or "Health sciences (formerly medical sciences)" printed for FY2016-20 = `medical_sciences`). It does not bridge the FY2021 break: every FY2021+ key starts with `rd_`.
- `precision_usd_thousands`: rounding unit of the published value kept (1 = thousands, 0.1, 100 = $0.1M, 1000 = $1M).
- `note`: why a value or label came from where it did, revision flags, `*` cells.

Units: nominal dollars in thousands. Source tables are in thousands (historical tables, single-year tables) or millions (trend tables, 1 decimal up to vol 70, integers from vol 71); millions were multiplied by 1,000.

### How values were chosen

1. Only actual years are used. Each volume reports one actual year plus preliminary/projected years; FY2025 (vol 74) is preliminary and is excluded, as are FY2001-02 in the 1951-2002 historical tables.
2. Row set and labels for a year come from the most recent accessible volume that reports it ("latest publication"). Subtotals that only older volumes printed (e.g. "Biological and agricultural sciences" for FY2000-06) are dropped.
3. Value: the latest-published value. If an older table printed the same cell at finer precision and it agrees with every later publication within rounding, the finer number is kept (it is the same number, unrounded). `note` says so. If an older value differs beyond rounding, the later value wins and the pair goes to the revisions log.
4. `*` cells (">0 but < $500,000" in million tables, "< $500" in thousand tables): filled from an older finer table when one exists and is consistent; otherwise the value is blank (4 rows, all Humanities: FY2021 basic and applied, FY2022 applied, FY2024 applied).

## Sources and exact URLs by year range

| FY range in final file | Source id | Tables used | URL |
|---|---|---|---|
| 1970-1999 (values) | nsf03325, Detailed Historical Tables FYs 1951-2002 (vol 50 based), xls, $ thousands | hist25 (research), hist35 (basic), hist45 (applied) | https://webarchive.library.unt.edu/web/20121010114603id_/http://www.nsf.gov/statistics/nsf03325/tables/hist25.xls (hist35.xls, hist45.xls same path). Index: https://webarchive.library.unt.edu/web/20121010114603/http://www.nsf.gov/statistics/nsf03325 |
| 1985 (labels; values cross-checked) | nsf07323, Federal Funds FYs 2004-06 (vol 54), PDF | T122-T127 (FY1985-2006 trend, $M 1dp); T19/T30/T41 (FY2004, $K) | https://webarchive.library.unt.edu/web/20090514074659id_/http://www.nsf.gov/statistics/nsf07323/pdf/nsf07323.pdf |
| 1986; FY2005 values | nsf09300, Federal Funds FYs 2005-07 (vol 55), PDF | T122-T127; T19/T30/T41 (FY2005, $K) | https://webarchive.library.unt.edu/web/20090514075941id_/http://www.nsf.gov/statistics/nsf09300/pdf/nsf09300.pdf |
| 1987-1999 (labels; values cross-checked); FY2006 values | nsf10303, Federal Funds FYs 2006-08 (vol 56), PDF | T122-T127 (FY1987-2008); T19/T30/T41 (FY2006, $K) | https://webarchive.library.unt.edu/web/20130303045249id_/http://www.nsf.gov/statistics/nsf10303/pdf/nsf10303.pdf |
| 2000 | nsf21329, FYs 2019-20 (vol 69), xlsx | T122-T127 (FY2000-20, $M 1dp); T17/T29/T41 (FY2019, $K) | https://ncses.nsf.gov/pubs/nsf21329/assets/data-tables/nsf21329-data-tables-tables.zip |
| 2001-2018 (mostly), 2020 | nsf22323, FYs 2020-21 (vol 70), xlsx | T122-T127 (FY2001-21); T17/T29/T41 (FY2020, $K) | https://ncses.nsf.gov/pubs/nsf22323/assets/data-tables/nsf22323-data-tables-tables-excels.zip |
| 2002 (latest), 2021 | nsf24309, FYs 2021-22 (vol 71), xlsx | T90-T95; T23/T28/T33 (FY2021, $K) | https://ncses.nsf.gov/pubs/nsf24309/assets/data-tables/nsf24309-data-tables-tables-excels.zip |
| 2003 (latest), 2022 | nsf24321, FYs 2022-23 (vol 72), xlsx | T90-T95; T23/T28/T33 (FY2022) | https://ncses.nsf.gov/pubs/nsf24321/assets/data-tables/nsf24321-data-tables-tables-excels.zip |
| 2004 (latest), 2023 | nsf25328, FYs 2023-24 (vol 73), xlsx | T90-T95; T23/T28/T33 (FY2023) | https://ncses.nsf.gov/pubs/nsf25328/assets/data-tables/nsf25328-data-tables-tables-excels.zip |
| 2005-2024 (latest), 2024 values | nsf26316, FYs 2024-25 (vol 74, released 2026-05-04), xlsx | T90-T95 (FY2005-15 and FY2016-25, $M integer); T23/T28/T33 (FY2024, $K); T1 for checks; technical table A-3 crosswalk | https://ncses.nsf.gov/pubs/nsf26316/assets/data-tables/nsf26316-data-tables-tables-excels.zip ; https://ncses.nsf.gov/pubs/nsf26316/assets/technical-tables/nsf26316-technical-tables-tables-excels.zip ; survey page https://ncses.nsf.gov/surveys/federal-funds-research-development |

"Latest" for a given FY means the newest volume whose trend window includes it (windows roll by one year per volume: vol 74 covers FY2005-25, vol 73 FY2004-24, ..., vol 69 FY2000-20, vol 56 FY1987-2008, vol 55 FY1986-2007, vol 54 FY1985-2006). Where the `source_table` is older than the latest, the latest agreed within rounding (see `note`).

Also downloaded but not used for values: nsf06313 (vol 53, FYs 2003-05) `tables.pdf`, superseded; nsf03325 hist6/hista/hist16/26/36 (by character and by agency, no field).

### What was looked for and not usable

- Volumes 57-68 (published 2009-2020, trend windows starting FY1988-1999) are not reachable: NCSES moved them to "archived" goodbye pages, the UNT web archive did not capture their tables, and web.archive.org was not reachable when this was built. So for FY1987-1999 the latest accessible publication is vol 56 (2010) and for FY1985-86 vols 54-55. Comparisons below suggest the risk is small: across vol 50 -> 54 -> 55 -> 56 -> 69 no FY1970-99 cell changed beyond rounding.
- "Federal Obligations for Research by Agency and Detailed Field of S&E" historical series (nsf98326 FY1970-98, nsf01333 FY1970-2001, nsf04313 FY1970-2002, nsf04335 FY1970-2003): only the landing pages are archived; the xls/pdf tables are not. This is why the agency file does not go back further.
- NCSES Table Builder (ncsesdata.nsf.gov/builder, Federal Funds app "ffs") is a Qlik JavaScript app with no plain export URL; not used. Its configured key tables are single-year (FY2024).
- DataLumos/ICPSR: no copy of this survey found (only the FFRDC survey).

## Taxonomy versions and breaks

| `taxonomy_version` | Years | Field detail available |
|---|---|---|
| `fose_1970_75` | FY1970-75 | 7 broad fields + other sciences n.e.c. Math & computer sciences reported only as a total. Biological & agricultural reported only as a total. Medical sciences split into clinical / other medical. Social sciences n.e.c. split into history / linguistics / other. |
| `fose_1976_77` | FY1976-77 | Mathematics, computer sciences and math & CS n.e.c. split out. History/linguistics split no longer collected. Clinical/other medical still split. |
| `fose_1978_2020` | FY1978-2020 | Biological (excl. environmental), environmental biology and agricultural sciences split out (FY1978-99 under the subtotal "Biological and agricultural sciences", printed until FY2006 in vols 54-56 but dropped from vol 69+ tables, so FY2000-20 rows have them directly under Life sciences). Clinical vs other medical no longer collected (FY2000 shows 0 placeholders in the historical table; those 15 cells were removed). Labels change cosmetically between sources ("n.e.c." / "nec" / "Other ..."; vol 71+ trend tables print FY2013-20 rows with new names such as "Health sciences (formerly medical sciences)"); `field_key` is constant through these. |
| `ford_2021` | FY2021-24 | Field of R&D taxonomy introduced in vol 71 (FYs 2021-22). 9 broad areas, 41 fields. See crosswalk. Not comparable with FY2020 and earlier. |

### Crosswalk, vol 70 (field of S&E) -> vol 71 (field of R&D), from technical table A-3

| Vol 70 and earlier (`fose_*`) | Change | Vol 71+ (`ford_2021`) |
|---|---|---|
| Computer sciences and mathematics (broad): Computer sciences | separated, now a broad area | Computer and information sciences (no detail) |
| Mathematics; Other computer sciences and mathematics | separated, now a broad area | Mathematics and statistics (no detail) |
| Environmental sciences / Atmospheric sciences / Geological sciences / Oceanography / Other environmental sciences | renamed | Geosciences, atmospheric sciences, and ocean sciences / Atmospheric science and meteorology / Geological and earth sciences / Ocean sciences and marine sciences / Other geosciences, atmospheric sciences, and ocean sciences |
| Biological sciences (excl. environmental biology) + Environmental biology | combined | Biological and biomedical sciences |
| Medical sciences | renamed | Health sciences |
| (none) | new | Natural resources and conservation (life sciences) |
| Agricultural sciences; Other life sciences | unchanged | same |
| Astronomy | renamed | Astronomy and astrophysics |
| (none) | new | Materials science (physical sciences; printed "Material science" in vols 71-72) |
| Chemistry; Physics; Other physical sciences | unchanged | same |
| Psychology: biological aspects, social aspects, other | unchanged | same |
| Political science; Sociology | renamed | Political science and government; Sociology, demography, and population studies |
| Other social sciences | narrowed | Other social sciences, excluding education research and law (moved to Other fields) |
| Anthropology; Economics | unchanged | same |
| Aeronautical engineering + Astronautical engineering | combined | Aerospace, aeronautical, and astronautical engineering |
| (none) | new | Bioengineering and biomedical engineering; Industrial and manufacturing engineering |
| Electrical engineering; Metallurgy and materials engineering | renamed | Electrical, electronics, and communications engineering; Metallurgical and materials engineering |
| Chemical, civil, mechanical, other engineering | unchanged | same |
| Other sciences nec | replaced | Other fields: business management, communication, education research, humanities incl. history, law, social work, visual and performing arts, all other fields |

Vol 71 also started collecting field of R&D for experimental development (not used here; this file is research only).

### Comparability breaks inside a taxonomy (from survey technical notes and table notes)

- FY1992: ADAMHA folded into NIH; psychology research appears underreported in FY1992.
- FY1996: NSF changed its field coding; some engineering fields (e.g. mechanical) shift.
- FY2000: NIH reclassified its development as research; NASA moved the Space Station from R&D to R&D plant. Visible as level shifts in life sciences and psychology (basic psychology 347 -> 818 -> 293 $M in FY1999-2001).
- FY2004: NIH financial records stopped carrying field of S&E; NIH estimates fields from scientific class codes. Biological vs medical sciences are not comparable across FY2003/2004 (basic biology 10,472 -> 7,223 $M while basic medical 2,919 -> 5,477 $M).
- FY2004-06: NASA full-cost budgeting. FY2012-13: NASA reporting revamp; ISS research counted as research from FY2012. NASA has no field codes and allocates research to fields by estimate.
- FY2016: definitions aligned with OMB A-11 (development narrowed to "experimental development"); mainly affects development, but some reclassification at the research margin is possible.
- FY2009-10: ARRA funding. FY2020-22: COVID supplemental appropriations.

## Revisions found (overlapping volumes disagree beyond rounding)

Full list in `fedfunds_revisions_log.csv` (each older/newer pair). Summary, first-published vs value kept:
- FY1970-99: none. vol 50 historical tables, vols 54-56 and vol 69 agree within rounding for every cell.
- FY2000: 11 small differences between the 2003 historical tables and every later volume (largest: psychology biological aspects, research, 7.8 -> 8.2 $M; social aspects 56.4 -> 56.0 $M; applied all-fields total 18,900.7 -> 18,900.8 $M). Later value kept. This leaves a 0.09 $M additivity gap in FY2000 research (the one row in the additivity check).
- FY2021: large field reallocation after NASA revised its FY2021 field data in vol 72 (plus DOT and USAID undercount corrections). Research: All other fields 10,748 -> 5,595 $M; physical sciences 8,044 -> 10,048; geosciences 3,569 -> 5,042; astronomy 308 -> 964; aerospace engineering 1,717 -> 2,604; all-fields total 86,244 -> 85,915. Vol 72+ values kept.
- FY2022: 10 small revisions (social sciences/sociology about +1 $M).
- FY2023: basic "Other engineering" revised down 354 $M in vol 74 (all-fields basic 47,335 -> 46,981 $M).
- FY2024: only one actual publication so far (vol 74).

## Known gaps and limits

- No finer field detail exists before FY1976 for math/CS and before FY1978 for the biology split; FY1970-75/77 sub-detail that was later dropped (clinical medicine, history, linguistics) is kept as level 3.
- Precision: FY1970-2000 (except 11 revised FY2000 cells), FY2004-06 and FY2024 are in thousands. FY2001-03 and FY2007-18 are at $0.1M (vols 69-70 are the latest publications to print one decimal; the vol 71+ trend tables print integer millions and agree with them). FY2019-20 at $0.1 thousand. FY2021-23 cells at $1M where the cell was revised after its own volume, otherwise thousands from that year's volume.
- 4 cells are blank (`*`, no finer value available): Humanities FY2021 basic/applied, FY2022 applied (under $500 thousand), FY2024 applied (under $500).
- FY2025 is preliminary only (vol 74) and is not included. FY2024 is actual.
- Latest accessible publication for FY1985-99 is 2008-2010 (vols 54-56), not the 2011-2020 volumes (see above).
- `research_total` = basic + applied up to rounding in every year (max gap $1M in integer-million years).

## Sanity check against an independent published total

Comparison: all-fields total in this file vs Table 1 of vol 74 ("Federal obligations for research and development, by type of R&D, and for R&D plant: FYs 1951-2025", $ thousands; https://ncses.nsf.gov/pubs/nsf26316/assets/data-tables/tables/nsf26316-tab001.xlsx). Table 1 is a separate trend table (character of work, no field split), so it tests both the field-table parsing and the value selection. It comes from the same survey; no fully independent source of these totals exists (S&E Indicators and National Patterns republish this survey).

| FY | Basic, this file ($K) | Basic, Table 1 ($K) | Diff | Applied, this file ($K) | Applied, Table 1 ($K) | Diff |
|---|---|---|---|---|---|---|
| 1970 | 1,925,908 | 1,925,908 | 0 | 2,974,890 | 2,974,890 | 0 |
| 1980 | 4,674,156 | 4,674,156 | 0 | 6,923,222 | 6,923,222 | 0 |
| 1990 | 11,285,593 | 11,285,593 | 0 | 10,336,771 | 10,336,771 | 0 |
| 2000 | 19,569,849 | 19,569,849 | 0 | 18,900,800 | 18,900,781 | 19 |
| 2010 | 31,795,300 | 31,795,342 | -42 | 31,932,600 | 31,932,631 | -31 |
| 2024 | 47,493,585 | 47,493,585 | 0 | 52,062,246 | 52,062,246 | 0 |

All 55 years: maximum absolute difference 319 (basic), 320 (applied), 481 (research total), all within the rounding of the field tables used ($0.1M or $1M). Every year is in `fedfunds_check_totals_vs_table1.csv`. Table 1 has thousand-dollar totals for every year if more precision on the all-fields line is needed.

Other checks run: children sum to parents within rounding in every source table and in the final file (except the FY2000 case above); PDF-extracted values were spot-checked against the PDF text (e.g. FY1987 basic engineering n.e.c. 107.8 $M vs 107,757 $K in the historical xls; FY2004 basic medical sciences 5,477,224 $K).

## Agency file (`fedfunds_research_by_field_agency.csv`)

FY2019-2024 only, research / basic / applied, every agency row printed (department, sub-agency, `agency_level` from the table indentation, `department_or_independent`), by broad field plus "Total, all fields", $ thousands. Sources: the single-year "by agency and field" tables of vols 69-74 (nsf21329 T18/T30/T42, nsf22323 T18/T30/T42, nsf24309/24321/25328/26316 T24/T29/T34). FY2019-20 use the old broad fields (`fose_1978_2020`), FY2021+ the field-of-R&D areas.
- These are the as-first-published splits; NCSES does not republish agency x field for earlier years. For FY2021 (NASA, DOT, USAID revisions), FY2022 and FY2023 the agency file totals therefore differ from the revised main file (all-fields research: FY2021 +329 $M, FY2022 -25 $M, FY2023 +352 $M). NASA FY2021 rows carry a note.
- Earlier agency x field history (FY1970-2003) exists only in the unarchived nsf04313/nsf04335 tables; PDF agency tables for FY2004-06 in vols 54-56 were not parsed.

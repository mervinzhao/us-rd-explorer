# National Patterns of R&D Resources: source notes

Downloaded 2026-11-18. Release used throughout: National Patterns of R&D Resources: 2023–24 Data Update, NSF 26-313, released 27 February 2026 (disclosure review NCSES-DRN25-070). No 2024–25 edition exists yet (`/data-collections/national-patterns/2024-2025` returns 404).

## URLs

- Landing page (the generic link redirects here): https://ncses.nsf.gov/data-collections/national-patterns/2023-2024
  - The URL in the request, https://ncses.nsf.gov/surveys/national-patterns-rd-resources, returns 404.
- Excel tables, zipped: https://ncses.nsf.gov/pubs/nsf26313/assets/data-tables/nsf26313-data-tables-tables-excels.zip
- Single tables: https://ncses.nsf.gov/pubs/nsf26313/assets/data-tables/tables/nsf26313-tab00N.xlsx (N = 1 to 9)
- Full data-tables PDF, with footnotes and technical notes (the xlsx files have no footnotes): https://ncses.nsf.gov/pubs/nsf26313/assets/nsf26313.pdf
- InfoBrief: NSF 26-314, https://ncses.nsf.gov/pubs/nsf26314 ("U.S. R&D Totaled $937 Billion in 2023; Estimate for 2024 Indicates Further Increase to $993 Billion")
- Previous edition, used only for the revision check: 2022–23, NSF 25-326, released 27 February 2025, https://ncses.nsf.gov/data-collections/national-patterns/2022-2023

Citation: National Center for Science and Engineering Statistics (NCSES). 2026. *National Patterns of R&D Resources: 2023–24 Data Update.* NSF 26-313. Alexandria, VA: U.S. National Science Foundation.

Local copies are in `raw/natpat/nsf26313/`: the zip, `xlsx/`, the PDF and `nsf26313.txt` (pdftotext). The previous edition's tables 6 to 9 are in `raw/natpat/prev_2022-2023/`.

## Tables used

| Table | Title | Used for |
|---|---|---|
| nsf26313-tab001 | U.S. GDP, R&D, and ratio of R&D to GDP (and components): 1953–2024 | `natpat_deflator.csv` |
| nsf26313-tab002 to tab005 | U.S. total / basic / applied / experimental development expenditures, by performer and source of funds: 1953–2024 | Performer totals (`all_sources` × performer), the `all_federal_performers` group, the business-performer detail file, and a cross-check |
| nsf26313-tab006 to tab009 | The same four, by source of funds and performer: 1953–2024 | Every source × performer cell, source totals, and the grand total |

All values are in millions of dollars and calendar years. Each table has a current-dollar block and a constant-2017-dollar block.

## Output files

- `natpat_character_source_performer.csv`: 8,928 rows, 1953–2024, columns `year, character, source_of_funds, performer, value_usd_millions_nominal, status, value_usd_millions_constant2017, not_available, table_id`.
  - `character`: basic | applied | development | total.
  - `source_of_funds`: all_sources, federal, nonfederal_government, business, higher_education, nonprofit.
  - `performer`: all_performers, all_federal_performers (federal intramural plus FFRDCs, table 2–5 total), federal_intramural, ffrdc, nonfederal_government, business, higher_education, nonprofit.
  - `status`: actual for 1953–2022, preliminary for 2023 ("some data for 2023 are preliminary and may be revised later") and estimated for 2024 ("include estimates and are likely to be revised later"). NCSES treats 2024 as an estimate, not a preliminary actual, so it gets a third value.
  - `not_available = NA` where the table prints NA. The value is blank there; it is not zero.
  - `table_id` is the table the value was taken from. Cells from tables 6–9 matched tables 2–5 everywhere they overlap (0 mismatches in 8,064 comparisons).
  - The constant-dollar column comes straight from the tables. NCSES computes it from unrounded data, so it can differ by about $1M from nominal ÷ deflator.
- `natpat_business_performer_funding_detail.csv`: tables 2–5 split business-performed R&D into own domestic, other domestic business, foreign business and other. Tables 6–9 fold the first three into the `business` source, so this is kept in a separate file to avoid double counting. Before 2008 only federal and own (all nonfederal) are shown, and the other three are NA.
- `natpat_deflator.csv`: the GDP implicit price deflator (2017 = 1.00000) used by National Patterns, plus nominal and real GDP and total R&D in billions, from table 1.
- `natpat_checks.txt`: the full output of the sum and cross-table checks.
- `natpat_revisions_vs_2022-23.txt`: every change in source totals between the 2022–23 and 2023–24 editions.
- Scripts: `scripts/natpat_build.py` (builds all of the above, `python -I scripts/natpat_build.py raw/natpat/nsf26313/xlsx data`) and `scripts/natpat_revisions.py`.

Headline check against the release: 2023 total is $937.2B (basic $138.1B, applied $174.1B, development $625.0B), and 2024 is $993.4B. Both match the landing page and NSF 26-314.

## Sanity check: do sources sum to totals?

- Sources to the grand total: the five source totals sum to the all-sources, all-performers total within ±$3M (rounding) in every year and every character, in current and constant dollars. This is the identity the basic/applied/development-by-funder chart depends on, and it holds.
- Basic + applied + development sum to total within ±$5M for every source.
- The source × performer matrix is not complete from 2016 on. In every year from 2016 to 2024, about $0.7–1.1B of total R&D sits in source totals and performer totals but in no source × performer cell. Most of it is nonfederal-government and higher-education money that funds nonprofit performers ($0.6–1.1B a year of the nonprofit performer total). Smaller amounts reach business performers ($60–150M, the table 2 "Other" column, part of which tables 6–9 count as a nonprofit source) and state intramural performers ($30–45M). Before 2016 the matrix closes within ±$2M. The source and performer totals are complete. Only the cells are partial, so anything built by summing cells instead of using the published totals will come out low.
- 2024 has a further $623M (total R&D; basic $123M, applied $255M, development $244M): federal intramural R&D funded by nonfederal sources (table 2 footnote g). It is included in `all_federal_performers` and in the nonfederal source totals, but it has no cell.
- No all-sources total is published for `federal_intramural`. Before 2024 it is all federally funded, so use the `federal` × `federal_intramural` row.

## Revisions versus the previous edition (2022–23, NSF 25-326)

- 1953–2022: only rounding-level changes, except for $50–150M a year moved from the nonprofit source to the higher-education source in 2016–2022, and higher-education development revised in 2016.
- Business R&D for 2022 and earlier was not revised. The release says explicitly that "no revisions will be made to the R&D expenditure estimates published for the 2022 or earlier BERD Surveys". What changed is the treatment of 2023: business-funded R&D in 2023 went from $709.2B to $703.9B. Within it, business-funded basic research fell $1.1B, applied research rose $4.2B and development fell $8.4B. Federal 2023 rose $1.0B, and nonprofit 2023 rose $1.1B.

## Breaks and comparability notes (from the table footnotes and technical notes)

Business performer and business source:
- 2023 and later: during the 2023 BERD survey some respondents dropped spending that does not meet the BERD definition of R&D. NCSES calls the result a "meaningful decrease" for 2023 against the old reporting practice, and says 2023–24 are not comparable with 2022 and earlier, which will not be revised. This is a downward level break between 2022 and 2023, concentrated in business-funded R&D.
- 2008: the business survey switched from SIRD (1953–2007) to BRDIS. NCSES says the switch "does not appear to have introduced further discontinuities" in the type-of-R&D estimates. Social science R&D was first included in 2008 ($0.8B). Before 2008 business R&D splits only into federal and nonfederal, so in the source × performer tables nonfederal_government → business and nonprofit → business are NA for 1953–2007, and all nonfederal funding of business performers is counted as business-funded.
- 2016: microbusinesses with 1–4 employees were added (BRDI-M, +$4.8B). From 2017, ABS covers firms with 1–9 employees ($5.7B in 2017) and BRDS/BERD covers firms with 10 or more.
- 1998: the type-of-R&D estimates for business were revised and are not comparable with 1997 and earlier. The share of business-funded R&D that is basic research drops from 7.6% (1997) to 4.5% (1998). This is a method step, not a real change, and it is the largest break in the basic-research-by-funder series.
- From 2008, companies report the type of R&D only for company-funded and federally funded work. Type splits for other sources are estimated.
- The business source includes foreign business funding: parent or unaffiliated firms abroad, $25.8B in 2023, and U.S. firms' foreign subsidiaries, $34.1B (table 2 footnote d). The detail is in the business-performer detail file.

Type of R&D by source, in general:
- Federal type splits come from survey responses. Nonfederal type splits by source are modeled from nonfederal totals and the total nonfederally funded R&D by type. NCSES: "comparisons of R&D type by funding source are not supported by statistical testing."

Federal intramural:
- 2016 and later exclude preproduction development (for example DoD Operational Systems Development), $5–7B a year in 2016–18. Federally funded intramural development is $20.3B in 2014, $19.0B in 2015 and $15.8B in 2016.
- 2024: the data source changed from the Federal Funds survey to the new Federal Facilities R&D Survey. Before 2024, intramural also included the cost of administering extramural R&D. The 2024 type mix moves sharply: federally funded intramural basic $7.4B → $5.9B, applied $11.6B → $8.9B, development $25.9B → $33.7B, against a total of $44.9B → $48.5B. Treat the 2023 to 2024 change in federal intramural, and in federally funded development generally, as a break.
- Fiscal-year data are converted to calendar years: from 1977, 75% of the same fiscal year plus 25% of the next; before 1977, 50/50. Higher education and state data use 50/50.

FFRDCs:
- Before 2001 all FFRDC R&D is counted as federally funded, so FFRDC cells under nonfederal government, business and nonprofit are NA for 1953–2000. From 2001 nonfederal funding is shown ($447M of $29.9B in 2023).
- 1953–54 FFRDC totals cover only university-administered FFRDCs. Industry-administered FFRDCs sit in business and nonprofit-administered ones in nonprofit. For type of R&D, 1953–63 cover university-administered only, and 1964–80 exclude nonprofit-administered FFRDCs, which sit in nonprofit.

Nonfederal government (state intramural):
- Available from 2006 only (NA for 1953–2005). Type of R&D is reported only from 2016 and estimated for 2006–15. The source category "nonfederal government" means state and local government. It is about $6.7B in 2023 and mostly funds higher education.

Higher education:
- Before 2003, S&E fields only. Non-S&E R&D was 3.4% in FY2003 and 6.4% in FY2023.
- 1998 and later are netted for pass-through funds to other institutions, which avoids double counting ($9.5B of pass-through in FY2023).
- The type-of-R&D estimation was revised in 1998 and again in 2010. The basic share of higher-education-performed R&D goes 75.2% (2009), 70.6% (2010), 66.7% (2011).
- The higher-education performer's "nonprofit" funding includes unclassified other sources ($3.0B of $9.2B in FY2023).

Nonprofit performer:
- Source surveys: NPRA 2016, and the NPRA modules of ABS for 2020–23. 2017–19 are interpolated.
- For 1998–2015, the federally funded part comes from Federal Funds. Business-funded and self-funded parts are estimated from the parameters of the 1996–97 nonprofit survey, as are type-of-R&D splits other than the federal one.
- Years before 1973 come from earlier National Patterns reports (surveys in 1957 and 1960).
- The nonprofit source series is therefore mostly modeled before 2016, and the 1997/98 and 2015/16 seams are method changes.

Footnote letters in the tables: 2023 carries a/g/h and 2024 carries b/h/i, depending on the table. The CSV turns them into `status`.

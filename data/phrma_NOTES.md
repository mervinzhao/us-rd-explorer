# PhRMA member-company domestic R&D: notes

Files
- `phrma_domestic_rd.csv`: one row per year, 1970-2024, nominal $ millions. Value from the most recent edition that prints the year. `note` lists other editions' differing values and estimate flags.
- `phrma_domestic_rd_by_edition.csv`: every value read, one row per (year, edition), with domestic, abroad, total and the edition's "Estimated" flag.
- `work/phrma_parsed_long.csv`: raw parser output.
- Scripts: `../scripts/phrma_parse.py` (reads Table 1 from `pdftotext -layout` text), `../scripts/phrma_build.py` (picks values, writes notes). Raw PDFs and text are in `../raw/phrma/`.

Source table: "Domestic R&D and R&D Abroad, PhRMA Member Companies" (Table 1 of the profile appendix, later of the stand-alone Annual Membership Survey). PhRMA reached it directly. The NSF fallback was not needed.

## Editions used (18)

| Edition | Years in Table 1 | Copy used |
|---|---|---|
| Pharmaceutical Industry Profile 2002, appendix | 1970-2001 (2001 est.) | keionline.org |
| Profile 2003, appendix | 1970-2002 (2002 est.) | keionline.org |
| Profile 2004 to 2010, appendix | 1970 to the year before publication (last year est.) | keionline.org |
| Profile 2011, 2012 | 1975 on | keionline.org |
| Biopharmaceutical Research Industry Profile 2013 | 1975-2012 | phrma-jp.org |
| Biopharmaceutical Research Industry Profile 2014 | 1980-2013 | cdn.aglty.io (PhRMA CDN) |
| PhRMA Annual Membership Survey 2021 to 2025 | rolling 39-year window, e.g. 1987-2024 in 2025 | phrma.org / cdn.aglty.io |

Not retrieved: the 2015 profile, the 2016-2020 stand-alone surveys, the 2016 profile (it only points to the survey), and editions before 2002. web.archive.org was not reachable when this was built, and the phrma.org URLs for those years are dead. So the first-published estimates for 2014-2019 are missing. Those years' values come from the 2021+ surveys, which agree with each other. A CRS report (RL30913) quotes the 2000 profile as estimating $22.4 billion "in the United States" for 2000. The final value is 21,363.7. That figure is rounded and secondhand, so it is not in the CSV.

## Definitions and changes

- Coverage is company-financed R&D only, inside the US by all PhRMA member companies, US- or foreign-owned. "Abroad" counts only US-owned members and the US divisions of foreign-owned members. R&D by the foreign divisions of foreign-owned members is excluded, so domestic plus abroad is not members' global R&D.
- The 2002 and 2003 editions label the table "Ethical Pharmaceuticals". From 2004 the label is dropped, and the historical values did not change. Table 1 appears to include veterinary R&D. In the 2005 edition, Table 3 gives 2003 domestic human-use R&D as $26,744.7M, against $27,064.9M in Table 1.
- The 2002 edition footnote: "Increases in R&D expenditures are likely due to a more rigorous data collection methodology."
- The series is not a fixed panel. Each year reflects that year's membership, and the history is not restated when members join, leave or merge. Pre-2001 values have been frozen since at least the 2002 edition. PhRMA flags 1995 abroad R&D as "affected by merger and acquisition activity".
- Membership change: in May 2017 PhRMA began requiring members to spend at least 10% of global sales on R&D, and seven companies left (BioPharma Dive, 2018-08-13). PhRMA's tables carry no break note for it. 2017 onward may be biased up relative to earlier years.
- Large-pharma mergers (e.g. Pfizer-Wyeth 2009, Merck-Schering-Plough 2009) and the entry of biotech firms into PhRMA change the reporting population. No edition footnotes these. The domestic swings (2010 +15.1%, 2011 -10.6%, 2022 -5.5%, 2023 -5.1%) may reflect membership as much as spending. That is my reading, not PhRMA's.
- The 2012 edition's function table adds an "Externally Researched" category (licensing, milestones). Its definition says R&D includes funds contracted or granted to outside organizations. Whether licensing payments count in Table 1 is unclear.
- Estimates: in the 2002-2014 profiles, the latest year is flagged "Estimated". The 2021-2025 surveys flag no estimates. 2024 (2025 survey only) is a first report and may be revised.
- From 2021 the surveys show a rolling window (e.g. 1987-2024), so earlier years come from the latest edition that still prints them. 1970-74 come from the 2010 profile, 1975-79 from 2013 and 1980-81 from 2014.

## Disagreements between editions (domestic R&D, $M; the later value is used)

| Year | Earlier edition | Later/final |
|---|---|---|
| 2001 | 23,887.8 (2002 ed., est.) | 23,502.0 |
| 2002 | 26,384.0 (2003 ed., est.) | 25,655.1 |
| 2003 | 27,407.1 (2004 ed., est.) | 27,064.9 (still flagged est. in 2005-06 eds.) |
| 2004 | 30,643.9 (2005 ed., est.) | 29,555.5 |
| 2005 | 31,444.2 (2006 ed., est.) | 30,969.0 |
| 2006 | 34,467.8 (2008 ed., not flagged) | 33,967.9 (2007 ed. est. and 2009+ eds.). Looks like a one-edition misprint (exactly 500 apart) |
| 2007 | 35,394.4 (2008 ed., est.) | 36,608.4 |
| 2008 | 38,427.8 (2009 ed., est.) | 35,571.1 |
| 2009 | 34,806.0 (2010 ed., est.) | 35,356.0 |
| 2010 | 37,371.0 (2011 ed., est.) | 40,688.1 |
| 2011 | 38,529.9 (2012 ed., est.) | 36,373.6 |
| 2012 | 36,810.4 (2013 ed., est.) | 37,510.2 |
| 2013 | 40,087.4 (2014 ed., est.) | 40,396.0 |

Estimates miss the final value by up to about 8% (2008). Every non-estimate value agrees across all editions that print it, except 2006 in the 2008 edition. Abroad values differ in the same pattern (see the by-edition file).

Internal inconsistencies in PhRMA's printed totals (domestic values unaffected):
- 2001: total printed as 29,772.7 against a component sum of 29,722.6, in every edition from 2003 on.
- 1998: the 2004 edition prints the total as 20,996.9, where every other edition prints 20,966.9.

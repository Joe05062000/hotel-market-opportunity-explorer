# Public-release data review

Reviewed November 2, 2026. This document records publication conditions and unresolved permissions; it does not declare that facts are copyrightable or provide a legal clearance opinion. Public access, government hosting and attribution are not treated as an applicable open data license.

| Source group | Specific unresolved restriction | Public-release decision |
|---|---|---|
| NYC Comptroller cash and tourism reports | The website expressly prohibits commercial use of materials without written permission. No permission is documented for public portfolio hosting or redistribution. A public portfolio is not assumed to fall outside the restriction. | Exclude numerical observations and their calculated historical findings, briefs and screenshots. Keep bibliographic references and coverage metadata only. |
| NYC Tourism + Conventions / Tourism Economics / STR | No applicable open redistribution license was established for the barometer, trend report, visitor estimates or proprietary STR hotel observations. The terms page exposed navigation only on retrieval. The release’s **media asset** restrictions are press-only and require credit; those restrictions are not claimed to be a license for numerical data. | Exclude citywide/borough observations and historical derivatives. Include no publisher images, logos, charts or full reports. |
| NYS Comptroller hotel observations | The reviewed privacy/links policy does not establish an open reuse license for report observations or underlying third-party hotel measurements. The later press release was discovery-only after direct retrieval failed. | Exclude numerical observations. Preserve research references, access limitations and reporting-period metadata. |
| NYC Department of Finance and City Planning reports | NYC.gov reserves rights. The reviewed reports do not establish an open license for their contents or third-party STR figures. Tax-year reporting populations also differ from hotel-market measures. | Metadata references only; no numerical tax observations, digitized hotel charts or publisher assets. |

## What the public repository contains

Original application code, definitions, calculation methods, hypothetical defaults, tests using explicitly hypothetical inputs, and source/period/permission metadata. The public assistant is a guided data assistant requiring no API key. Scenario outputs are user-assumption calculations, not disguised historical observations. A generated public brief explains evidence availability; it does not reproduce the local research brief’s market findings.

## What is omitted

The original research CSVs, borough observation and coverage files, historical numerical KPI cards, historical charts and takeaways, derived historical Markdown briefs, screenshots of those results, downloaded reports, credentials and unrelated local files. They remain outside this repository in the separate local research workspace. The public app cannot read its parent folder or import the local research app.

## Before enabling historical results

Record written permission or an explicit applicable license covering both public display and dataset redistribution, including upstream rights where relevant. Record scope, conditions and evidence in a reviewed approval manifest. Revalidate category, geography, periods, units, population, actual/forecast status and sample coverage. Update the public release deliberately; do not rely on attribution alone or silently enable unapproved CSV loading. No permission is implied by preserving a source link.

## Primary policy references

- [NYC Comptroller disclaimer](https://comptroller.nyc.gov/disclaimer/) — commercial-use restriction.
- [NYC Tourism terms page](https://www.nyctourism.com/terms-of-use/) — substantive terms could not be verified from the retrieved page.
- [NYC Tourism release, Media Assets section](https://www.business.nyctourism.com/press-media/press-releases/NYC-Tourism-Annual-Report-March-2026) — separate press-use restriction on media assets.
- [NYS Comptroller privacy and links policy](https://www.osc.ny.gov/online-services/privacy-and-links-policy?redirect=legacy) — not an open data license.
- [NYC.gov terms, Intellectual Property](https://www.nyc.gov/main/terms-of-use) — rights reserved.

All source URLs, publication dates, reporting coverage, retrieval dates and dispositions are retained in `data/sources.json`. No blanket license for third-party data is asserted.

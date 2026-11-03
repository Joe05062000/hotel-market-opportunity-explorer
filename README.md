# Hotel Market Opportunity Explorer

A Python, Streamlit, pandas and Plotly portfolio project for evidence-based hospitality strategy in New York City. It combines a primary-source research register, a **guided data assistant that requires no API key**, and transparent hypothetical hotel room-revenue scenarios.

**Public-release scope:** historical numerical observations are withheld pending reuse clearance. This repository does not currently provide historical hotel KPIs, borough price/occupancy charts, market rankings or historical market findings. It does not substitute fabricated data. The original local research workspace is not part of this repository.

## Business problem

Hotel strategy requires more than comparing headline room rates. An analyst must distinguish realized ADR from advertised prices, utilization from absolute demand, and room revenue from profit. Borough averages may reflect different hotel classes and guest mixes, while annual, monthly and year-to-date observations may not be comparable. Public availability also does not establish permission to redistribute data.

This project makes those evidence boundaries visible and lets a reviewer test hotel revenue assumptions transparently. The public portfolio demonstrates the workflow without redistributing observations whose reuse rights have not been established.

## Tools and methodology

- **Python:** deterministic calculations, input validation and template-generated explanations/briefs.
- **Streamlit:** the interactive portfolio application, with `app.py` as the entry point.
- **pandas:** tabular scenario outputs and source coverage presentation.
- **Plotly:** readable, labelled charts of hypothetical revenue.
- **pytest / Streamlit AppTest:** arithmetic, validation, page interactions and operation without secrets.

The research register records primary publishers, URLs, reporting periods, retrieval dates, geographic coverage and unresolved reuse conditions. Historical actuals, reporting frequencies, populations and hotel categories must match before comparison. Scenarios remain separate from historical evidence. No causal inference, fabricated observation or arbitrary opportunity score is used.

## Features

- Navy, cream and teal consulting-style interface.
- Guided data assistant with five preset questions, deterministic Python/template responses, source references and honest evidence-unavailable explanations. It is **not AI-generated chat**.
- Downside/base/upside scenarios with editable rooms, operating days, occupancy and nominal ADR.
- Calculated available room-nights, expected sold room-nights, room revenue and RevPAR; chart and CSV download.
- Borough source-coverage review with missing coverage and hotel-category/sample limitations; no unsupported ranking.
- Downloadable public evidence-availability brief, with optional user scenarios separated from historical evidence.
- Source register with publication/retrieval dates, periods, upstream attribution and reuse decisions.
- No external API, credentials, runtime sign-in or historical dataset download required.

## Run locally

Use Python **3.12**, the version selected for deployment.

```bash
git clone https://github.com/Joe05062000/hotel-market-opportunity-explorer.git
cd hotel-market-opportunity-explorer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

The clone URL is the intended repository destination; publication requires GitHub authentication if the repository has not yet been created. If you already have the prepared folder, start there and skip the clone steps. On Windows, activate with `.venv\Scripts\activate`.

`app.py` at the repository root is the Streamlit entry point. `requirements.txt` pins Streamlit, pandas and Plotly to the locally verified versions. No system packages are required. **Do not add any secrets for this public app.** It neither reads API keys nor calls an AI service. An optional AI experiment exists only in the separate local research workspace and is not a public feature.

## Calculations and assumptions

Occupancy is entered as a percentage and converted to a decimal:

```text
Available room-nights = rooms × operating days
Sold room-nights      = available room-nights × occupancy / 100
Room revenue          = sold room-nights × ADR
RevPAR                = ADR × occupancy / 100
```

All default cases and user edits are hypothetical, with no historical reporting dates. Expected sold room-nights may be fractional. If rooms or operating days differ, changes in revenue also reflect capacity or horizon. Price-demand response, seasonality, costs and taxes are not modeled. Room revenue excludes costs and is **not profit**. No opportunity score or investment recommendation is generated.

## Sources and data limitations

The metadata register links to NYC Tourism + Conventions / Tourism Economics publications, NYC Comptroller reports, NYS Comptroller reports, and NYC Department of Finance and Department of City Planning publications. It identifies annual, monthly, year-to-date and tax-year coverage separately.

The reviewed borough snapshot names Manhattan, Brooklyn and Queens; the Bronx and Staten Island are absent from that selected table. Category-matched hotel rates, a fixed hotel panel and performance sample sizes are not established. Realized ADR is not an advertised booking price. No booking websites were scraped and Airbnb data are not used as hotel data.

See [the source register](data/sources.json), [release manifest](data/release_manifest.json) and [specific data-reuse review](docs/DATA_REUSE.md). Public access and attribution do not grant permission. In particular, NYC Comptroller materials restrict commercial use; tourism/STR reuse rights remain unverified; NYC.gov rights are reserved. The public repository excludes original numerical observations, historical derivatives, publisher media and full reports. No third-party data license is claimed.

To enable historical results later, document applicable public-display **and** redistribution rights, review upstream rights, and then add validated observations through a deliberate release change. Do not merely turn a flag on or upload unapproved data.

## Verify the public release

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/check_release.py
python -m pip check
```

Tests check scenario arithmetic, invalid inputs, missing historical evidence, all guided presets, every page without secrets, scenario interaction and evidence-brief boundaries. The release check verifies the file allowlist, metadata-only manifest, absence of unapproved data/media and common credential patterns. These checks do not establish legal permission or replace source review.

Only the contents of this prepared public repository should be pushed. Do not copy the parent research directory, `.venv`, `.env`, secrets, generated historical briefs or screenshots into it.

## Publication and future deployment

Publishing this GitHub repository does not deploy the app. No deployment is being performed as part of the current publication task. The settings below are retained for a future, separately authorized deployment.

Target repository: `Joe05062000/hotel-market-opportunity-explorer`.

| Setting | Value |
|---|---|
| Repository | `Joe05062000/hotel-market-opportunity-explorer` |
| Branch | `main` |
| Main file path | `app.py` |
| Python version | `3.12` |
| Secrets | Leave empty |
| Audience | Public portfolio app; verify public visibility in app settings |

If the repository has not been created, run `gh auth login --hostname github.com --git-protocol https --web` in your terminal, then `bash scripts/publish_github.sh` from this repository. The script verifies the authenticated owner, refuses an existing destination and does not rewrite history.

Sign in to [Streamlit Community Cloud](https://share.streamlit.io/), connect the GitHub account, choose **Create app → Yup, I have an app**, and enter the settings above. Select Python 3.12 under **Advanced settings**, leave secrets empty, then deploy. Confirm public visibility under the app’s sharing settings. No deployed URL is claimed until Community Cloud completes deployment.

See [the deployment checklist](docs/DEPLOYMENT.md). These steps follow [Streamlit’s official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

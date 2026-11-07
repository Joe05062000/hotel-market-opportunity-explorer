# Streamlit Community Cloud deployment

## Live app

[Hotel Market Opportunity Explorer](https://hotel-market-opportunity-explorer.streamlit.app/)

Deployment and public visibility verified November 6, 2026.

| Setting | Deployed value |
|---|---|
| GitHub repository | `Joe05062000/hotel-market-opportunity-explorer` |
| Branch | `main` |
| Entry point | `app.py` at the public repository root |
| Python setting | `3.12` |
| Runtime observed in build logs | Python `3.12.16` |
| Dependencies | Root `requirements.txt` |
| Theme | `.streamlit/config.toml` |
| Secrets | Empty; no API key required |
| Sharing | Public |

## Verification

- Fetched public `main` and confirmed it matched the prepared source before deployment.
- All thirteen public-edition tests passed locally on Python 3.12; the release allowlist and credential scan passed, and pip reported no broken requirements.
- Community Cloud installed the declared dependencies and started the application successfully.
- The live scenario explorer recalculated room revenue and RevPAR after editing ADR; the default was restored afterward.
- The guided assistant displayed the intended evidence-unavailable response with source references.
- The Markdown evidence brief downloaded successfully and retained the public-edition scope and source register.
- The sharing dialog confirmed public access.

The platform build log reported that Community Cloud replaced a known-problematic transitive pyarrow version with an older version automatically. The resulting app loaded and the live controls worked; no application-code fix was required.

## Scope and maintenance

Only the public repository is deployed. Historical numerical observations and derivatives remain excluded pending reuse clearance. The complete original research app and data remain in the separate local workspace. No API key or AI service is used by this public app.

The existing Git author identity is retained and commits have no AI co-author attribution. Future pushes to `main` are picked up by Community Cloud. Inspect build logs after dependency changes and keep Python 3.12 selected unless a different version has been tested. Do not add unapproved data or credentials to the repository.

Official references: [deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies), [sharing](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).

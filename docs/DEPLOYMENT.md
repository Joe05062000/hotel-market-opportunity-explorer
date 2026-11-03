# GitHub publication and future Streamlit deployment

Current scope: publish the public GitHub repository only. Do not deploy the app today. The Streamlit instructions below are future reference and require a separate deployment decision.

## Prepared configuration

- GitHub owner supplied by the user: `Joe05062000`.
- Repository name: `hotel-market-opportunity-explorer`.
- Intended repository URL: https://github.com/Joe05062000/hotel-market-opportunity-explorer
- Branch: `main`.
- Entry point: `app.py` at the repository root, **not the original research app**.
- Python: `3.12`.
- Dependency file: root `requirements.txt`.
- Streamlit theme: `.streamlit/config.toml`.
- Secrets: empty; no API key or secret is needed.
- Public visibility is the intended audience. No Streamlit deployment URL is reserved or asserted.

## Authentication and publication

The initial inspection found no Git repository/history in the original workspace, no global Git author identity and no authenticated GitHub CLI session. A separate Git repository is prepared in the `public_release` folder so the parent research files cannot be accidentally included. The initial local commit uses `Joe05062000` and the username-based GitHub noreply address, configured only for this repository. No global Git settings or pre-existing history are changed.

If GitHub authentication is still unavailable, do this in your own terminal:

```bash
cd public_release  # from the original local research workspace
gh auth login --hostname github.com --git-protocol https --web
gh auth status
bash scripts/publish_github.sh
```

The publish helper runs the release checks, requires a clean local commit on `main`, verifies the authenticated account is `Joe05062000`, and creates the requested **public** repository. It refuses an existing repository or remote instead of overwriting or force-pushing. If the destination exists, inspect its history and ownership before choosing how to integrate; do not delete it or rewrite history.

Do not paste credentials into this project, a chat message or a tracked file. GitHub authentication belongs in the GitHub CLI credential store.

## Streamlit Community Cloud

1. Open https://share.streamlit.io/ and sign in. Complete GitHub account connection/authorization yourself if requested.
2. Select **Create app**, then **Yup, I have an app**.
3. Repository: **Joe05062000/hotel-market-opportunity-explorer**.
4. Branch: **main**.
5. Main file path: **app.py**.
6. In **Advanced settings**, choose **Python 3.12**. Leave **Secrets empty**.
7. Choose **Deploy**. Inspect the build logs until the app is healthy.
8. In app settings/sharing, verify the app is **Public** for your portfolio. A public repository normally gives the app public visibility, but verify the setting.
9. Check Market overview, all guided questions, hypothetical scenarios and the downloadable evidence brief. Historical pages should explain that observations are withheld rather than showing values.

The sign-in and any authorization/visibility UI are the remaining user-controlled steps; this file is not evidence that the app has already been deployed.

Official references: [deploy](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies), [sharing and visibility](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).

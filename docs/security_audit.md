# Pre-Publication Security Audit

This checklist records the expected state before publishing the repository on GitHub and deploying the GUI on Streamlit Community Cloud.

## Scope

The app is a research simulation tool. It should not collect, store, or process personal, confidential, financial, health, biometric, or sensitive data.

## Repository Checks

Run before publishing:

```powershell
rg -n "SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE KEY|BEGIN RSA|sk-[A-Za-z0-9]{20,}" . -g "!uv.lock" -g "!.venv/**" -g "!docs/security_audit.md"
rg -n "Users\\\\[A-Za-z0-9_.-]+" . -g "!uv.lock" -g "!.venv/**" -g "!docs/security_audit.md"
git status --short
uv run ruff check .
uv run pytest
uv run realgrowthsim validate --preset baseline
uvx pip-audit --path .venv\Lib\site-packages --progress-spinner off
```

Expected result:

- no committed secrets
- no absolute local paths in tracked project files
- no `.streamlit/secrets.toml`
- no `.env`
- no generated `outputs/`
- no cache directories such as `__pycache__`, `.pytest_cache`, or `.ruff_cache`
- Streamlit smoke test renders `Current Reading` and reports no app exceptions

## Streamlit Cloud Checks

- Entrypoint: `streamlit_app.py`
- Dependency files: `pyproject.toml` and `uv.lock`
- App disclaimer visible in the GUI
- Scenario import limited to JSON text/file handled in session
- No default external APIs
- No telemetry implemented by the app
- README placeholder URL replaced after deployment

Official deployment references:

- Streamlit Community Cloud deploy docs: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>
- Streamlit app dependency docs: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies>
- Streamlit sharing docs: <https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app>
- Streamlit Terms of Use: <https://streamlit.io/terms-of-use>

## Residual Risks

- Public Streamlit apps are publicly accessible by URL and may be indexed.
- Streamlit/Snowflake controls Community Cloud availability and platform terms.
- Users can paste sensitive text into any free-text web input despite warnings; the app design minimizes this by restricting inputs to scenario JSON and numeric controls.

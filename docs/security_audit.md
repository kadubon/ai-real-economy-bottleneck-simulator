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
uvx pip-audit --progress-spinner off
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

## Latest Strict Audit: 2026-04-30

Results from the final pre-publication audit pass:

- `git status --short`: tracked changes were limited to this audit note and the intentional GUI preset-selection fix.
- `uv sync --extra dev --locked`: passed.
- `uv run ruff check .`: passed.
- `uv run pytest`: passed, 23 tests.
- `uv run realgrowthsim validate --preset baseline`: passed.
- `uv run realgrowthsim validate --preset resource_trust_shock`: passed, including event attribution.
- All ten scenario presets loaded, simulated, and passed identity/bounds checks for `g = gP + gI`, `BPI`, `OmegaP`, `OmegaI`, nonnegative physical states, and institutional bounds.
- `uvx pip-audit --progress-spinner off`: no known vulnerabilities found.
- Secret scan excluding `uv.lock`, `.venv`, and this audit document: no matches.
- Local absolute-path scan excluding `uv.lock` and `.venv`: no matches.
- Placeholder scan for `OWNER`, `YOUR-CUSTOM-SUBDOMAIN`, `PLACEHOLDER`, `TODO`, `FIXME`, `localhost`, and `127.0.0.1`: no matches in public docs/source/config.
- `.streamlit/secrets.toml`, `.env`, and `NOTICE`: absent.
- Generated caches and audit output files should be removed before commit.

Live Streamlit URL check:

- The deployed URL responded through Streamlit's public hosting/auth redirect flow and then returned an HTTP 200 Streamlit page.
- This confirms host reachability, but a final human browser check is still recommended because Streamlit apps hydrate client-side.

Official deployment references:

- Streamlit Community Cloud deploy docs: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>
- Streamlit app dependency docs: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies>
- Streamlit sharing docs: <https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app>
- Streamlit Terms of Use: <https://streamlit.io/terms-of-use>

## Residual Risks

- Public Streamlit apps are publicly accessible by URL and may be indexed.
- Streamlit/Snowflake controls Community Cloud availability and platform terms.
- Users can paste sensitive text into any free-text web input despite warnings; the app design minimizes this by restricting inputs to scenario JSON and numeric controls.

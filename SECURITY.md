# Security Policy

This project is a local or Streamlit-hosted research simulator. It is not designed to process personal, confidential, financial, health, biometric, or other sensitive data.

## Supported Versions

Security fixes target the current `main` branch until formal releases are created.

## Reporting A Vulnerability

Open a private security advisory on GitHub if the repository is public and advisories are enabled. If not, open an issue without including exploit details or sensitive data.

## Data Handling

- No telemetry is implemented by this application.
- No external API calls are made by default.
- Scenario JSON imports are processed in the active Streamlit session.
- Do not enter personal, confidential, financial, health, biometric, or sensitive data.
- Do not commit `.streamlit/secrets.toml`, `.env`, generated outputs, local virtual environments, or cache directories.

## Public Deployment Notes

Before deploying to Streamlit Community Cloud:

1. Confirm the repository contains no secrets or private files.
2. Use `streamlit_app.py` as the app entry point.
3. Keep `.streamlit/secrets.toml` absent from git.
4. Replace placeholder README URLs with the actual deployed `streamlit.app` URL.
5. Re-run tests and the pre-publication audit checklist in `docs/security_audit.md`.

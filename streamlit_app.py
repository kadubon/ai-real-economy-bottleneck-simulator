"""Streamlit Community Cloud entrypoint.

This file intentionally stays at repository root so Streamlit Community Cloud
can deploy the app with "Main file path: streamlit_app.py".
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

def main() -> None:
    from realgrowthsim.gui.app import main as app_main

    app_main()

if __name__ == "__main__":
    main()

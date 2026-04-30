def test_streamlit_entrypoint_imports():
    import realgrowthsim.gui.app
    import streamlit_app
    from realgrowthsim.model.catalog import INDICATOR_CATALOG, PARAMETER_CATALOG, STATE_CATALOG
    from realgrowthsim.model.state import STATE_NAMES

    assert callable(streamlit_app.main)
    assert callable(realgrowthsim.gui.app.main)
    assert set(STATE_NAMES) <= set(STATE_CATALOG)
    assert "BPI" in INDICATOR_CATALOG
    assert "theta_P" in PARAMETER_CATALOG


def test_streamlit_app_renders_current_reading_without_exceptions():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file("streamlit_app.py")
    app.run(timeout=30)
    texts = [str(node.value) for node in app.subheader]
    captions = [str(node.value) for node in app.caption]
    buttons = [str(node.label) for node in app.button]
    assert "Try One-Click Scenarios" in texts
    assert "AI Capability Growth vs Real-Economy Growth" in texts
    assert "Current Reading" in texts
    assert any("without editing parameters" in value for value in captions)
    assert "Run" in buttons
    assert len(app.exception) == 0

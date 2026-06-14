from pcobra.gui import app


def test_main_se_resuelve_sin_name_error():
    assert callable(app.main)

from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra import usar_loader as cobra_usar_loader


def test_core_usar_loader_delega_en_cobra_usar_loader(monkeypatch):
    token = object()

    def _fake_obtener_modulo(nombre, **_kwargs):
        assert nombre == "numero"
        return token

    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo", _fake_obtener_modulo)

    assert core_usar_loader.obtener_modulo("numero") is token

from pcobra.core import usar_loader as core_usar_loader
from pcobra.cobra import usar_loader as cobra_usar_loader


def test_core_usar_loader_delega_en_cobra_usar_loader(monkeypatch):
    token = object()

    def _fake_obtener_modulo(nombre, **_kwargs):
        assert nombre == "numero"
        return token

    monkeypatch.setattr(cobra_usar_loader, "obtener_modulo", _fake_obtener_modulo)

    assert core_usar_loader.obtener_modulo("numero") is token


def test_core_usar_loader_expone_resolver_modulo_cobra_proyecto(monkeypatch, tmp_path):
    token = tmp_path / "utilidades" / "fechas.co"

    def _fake_resolver(nombre, *, project_root, current_file=None):
        assert nombre == "utilidades.fechas"
        assert project_root == tmp_path
        assert current_file is None
        return token

    monkeypatch.setattr(cobra_usar_loader, "resolver_modulo_cobra_proyecto", _fake_resolver)

    assert (
        core_usar_loader.resolver_modulo_cobra_proyecto(
            "utilidades.fechas",
            project_root=tmp_path,
        )
        == token
    )

from pathlib import Path
from types import SimpleNamespace

from pcobra.cobra.usar_loader import (
    descubrir_raiz_proyecto,
    resolver_modulo_cobra_proyecto,
)
from pcobra.core.interpreter import InterpretadorCobra


def test_descubrir_raiz_proyecto_prefiere_cobra_toml_desde_archivo_principal(tmp_path):
    proyecto = tmp_path / "app"
    subdir = proyecto / "src"
    subdir.mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = subdir / "main.co"
    principal.write_text("", encoding="utf-8")

    assert descubrir_raiz_proyecto(subdir, principal) == proyecto.resolve()


def test_descubrir_raiz_proyecto_usa_directorio_principal_sin_cobra_toml(tmp_path):
    principal = tmp_path / "programa.co"
    principal.write_text("", encoding="utf-8")

    assert descubrir_raiz_proyecto(None, principal) == tmp_path.resolve()


def test_resolver_modulo_cobra_proyecto_usa_raiz_canonicalizada(tmp_path):
    proyecto = tmp_path / "app"
    modulo_dir = proyecto / "utilidades"
    modulo_dir.mkdir(parents=True)
    ruta = modulo_dir / "fechas.co"
    ruta.write_text("", encoding="utf-8")

    assert (
        resolver_modulo_cobra_proyecto("utilidades.fechas", project_root=proyecto)
        == ruta.resolve()
    )


def test_interpretador_usar_proyecto_resuelve_desde_cobra_toml(monkeypatch, tmp_path):
    proyecto = tmp_path / "app"
    (proyecto / "programas").mkdir(parents=True)
    (proyecto / "utilidades").mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "programas" / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("", encoding="utf-8")
    rutas_cargadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        rutas_cargadas.append((Path(ruta), kwargs))
        return []

    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    assert rutas_cargadas == [
        (
            modulo.resolve(),
            {
                "modules_path": str(proyecto.resolve()),
                "whitelist": {proyecto.resolve()},
            },
        )
    ]
    assert interp._project_root == proyecto.resolve()


def test_usar_proyecto_prepass_seguro_valida_sin_ejecutar(monkeypatch, tmp_path):
    proyecto = tmp_path / "app"
    (proyecto / "utilidades").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("", encoding="utf-8")
    eventos = []

    class NodoEfecto:
        def aceptar(self, validador):
            eventos.append("validado")

    def fake_cargar_ast_modulo(ruta, **kwargs):
        return [NodoEfecto()]

    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(main_file=principal)
    ejecutar_original = interp.ejecutar_nodo

    def ejecutar_nodo_con_efecto(nodo):
        eventos.append("ejecutado")
        return ejecutar_original(nodo)

    monkeypatch.setattr(interp, "ejecutar_nodo", ejecutar_nodo_con_efecto)
    interp._usar_prepass_metadata_only = True

    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    assert eventos == ["validado"]


def test_usar_proyecto_ejecucion_normal_ejecuta_modulo(monkeypatch, tmp_path):
    proyecto = tmp_path / "app"
    (proyecto / "utilidades").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("", encoding="utf-8")
    eventos = []

    class NodoEfecto:
        pass

    def fake_cargar_ast_modulo(ruta, **kwargs):
        return [NodoEfecto()]

    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )
    interp = InterpretadorCobra(main_file=principal)

    def ejecutar_nodo_con_efecto(nodo):
        eventos.append("ejecutado")

    monkeypatch.setattr(interp, "ejecutar_nodo", ejecutar_nodo_con_efecto)

    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    assert eventos == ["ejecutado"]

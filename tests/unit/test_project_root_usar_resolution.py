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


def test_interpretador_usar_proyecto_cachea_por_ruta_canonica(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    (proyecto / "utilidades").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("", encoding="utf-8")
    cargas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        cargas.append(Path(ruta))
        return [NodoAsignacion("valor", NodoValor(len(cargas)), declaracion=True)]

    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))
    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    assert cargas == [modulo.resolve()]
    assert interp.variables["valor"] == 1
    assert list(interp._usar_module_cache) == [modulo.resolve()]


def test_interpretador_usar_proyecto_detecta_ciclos_con_rutas_canonicas(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoUsar

    proyecto = tmp_path / "app"
    utilidades = proyecto / "utilidades"
    utilidades.mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo_a = utilidades / "a.co"
    modulo_b = utilidades / "b.co"
    modulo_a.write_text("", encoding="utf-8")
    modulo_b.write_text("", encoding="utf-8")

    def fake_cargar_ast_modulo(ruta, **kwargs):
        if Path(ruta).resolve() == modulo_a.resolve():
            return [NodoUsar("utilidades.b")]
        return [NodoUsar("utilidades.a")]

    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)

    try:
        interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.a"))
    except ImportError as exc:
        assert str(exc) == "Ciclo de módulos detectado en usar: a.co -> b.co -> a.co"
    else:
        raise AssertionError("Se esperaba un ImportError por ciclo de módulos")
    assert interp._usar_loading_stack == []

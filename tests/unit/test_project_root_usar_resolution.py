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


def test_interpretador_usar_proyecto_respeta_export_y_detecta_conflicto(monkeypatch, tmp_path):
    import pytest
    from pcobra.core.ast_nodes import NodoAsignacion, NodoExport, NodoValor

    proyecto = tmp_path / "app"
    (proyecto / "utilidades").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("", encoding="utf-8")

    def fake_cargar_ast_modulo(ruta, **kwargs):
        return [
            NodoExport("publico"),
            NodoAsignacion("publico", NodoValor(1), declaracion=True),
            NodoAsignacion("privado", NodoValor(2), declaracion=True),
        ]

    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    assert interp.variables["publico"] == 1
    assert "privado" not in interp.variables
    assert interp._usar_symbol_metadata["publico"]["module"] == str(modulo.resolve())

    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    interp_conflicto = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp_conflicto.contextos[-1].define("publico", 99)
    with pytest.raises(NameError, match="conflicto de símbolos"):
        interp_conflicto.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))


def test_resolver_modulo_cobra_proyecto_resuelve_modulo_misma_carpeta(tmp_path):
    proyecto = tmp_path / "app"
    proyecto.mkdir()
    modulo = proyecto / "saludos.co"
    modulo.write_text("", encoding="utf-8")

    assert resolver_modulo_cobra_proyecto("saludos", project_root=proyecto) == modulo.resolve()


def test_resolver_modulo_cobra_proyecto_resuelve_subcarpeta_con_puntos(tmp_path):
    proyecto = tmp_path / "app"
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.parent.mkdir(parents=True)
    modulo.write_text("", encoding="utf-8")

    assert resolver_modulo_cobra_proyecto("utilidades.fechas", project_root=proyecto) == modulo.resolve()


def test_resolver_modulo_cobra_proyecto_resuelve_modulo_anidado(tmp_path):
    proyecto = tmp_path / "app"
    modulo = proyecto / "a" / "b" / "c.co"
    modulo.parent.mkdir(parents=True)
    modulo.write_text("", encoding="utf-8")

    assert resolver_modulo_cobra_proyecto("a.b.c", project_root=proyecto) == modulo.resolve()


def test_interpretador_usar_proyecto_simple_se_bloquea_en_repl_estricto(monkeypatch, tmp_path):
    import pytest

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    (proyecto / "saludos.co").write_text("", encoding="utf-8")

    def fake_cargar_ast_modulo(_ruta, **_kwargs):
        raise AssertionError("REPL estricto no debe resolver módulos Cobra de proyecto")

    monkeypatch.setattr("pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo)

    interp = InterpretadorCobra(main_file=principal)
    interp.configurar_restriccion_usar_repl({"numero": "numero", "texto": "texto"})

    with pytest.raises(PermissionError, match=r"módulo externo no permitido en REPL estricto"):
        interp.ejecutar_usar(SimpleNamespace(modulo="saludos"))


def test_interpretador_usar_proyecto_misma_carpeta_con_nombre_simple(monkeypatch, tmp_path):
    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "saludos.co"
    modulo.write_text("", encoding="utf-8")
    rutas_cargadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        rutas_cargadas.append(Path(ruta))
        return []

    monkeypatch.setattr("pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo)

    interp = InterpretadorCobra(main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="saludos"))

    assert rutas_cargadas == [modulo.resolve()]


def test_interpretador_usar_proyecto_mantiene_raiz_al_cambiar_cwd(monkeypatch, tmp_path):
    proyecto = tmp_path / "app"
    externo = tmp_path / "otro-cwd"
    externo.mkdir()
    (proyecto / "utilidades").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("", encoding="utf-8")
    rutas_cargadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        rutas_cargadas.append((Path(ruta), kwargs["modules_path"]))
        return []

    monkeypatch.setattr("pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo)
    monkeypatch.chdir(externo)

    interp = InterpretadorCobra(main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    assert rutas_cargadas == [(modulo.resolve(), str(proyecto.resolve()))]
    assert interp._project_root == proyecto.resolve()


def test_interpretador_usar_proyecto_cachea_referencias_equivalentes(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    (proyecto / "a" / "b").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "a" / "b" / "c.co"
    modulo.write_text("", encoding="utf-8")
    cargas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        cargas.append(Path(ruta).resolve())
        return [NodoAsignacion("valor", NodoValor(len(cargas)), declaracion=True)]

    monkeypatch.setattr("pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo)

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="a.b.c"))
    interp.ejecutar_usar(SimpleNamespace(modulo="a.b.c"))

    assert cargas == [modulo.resolve()]
    assert interp.variables["valor"] == 1


def test_interpretador_usar_proyecto_detecta_ciclo_directo_self(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoUsar
    import pytest

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "a.co"
    modulo.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo",
        lambda _ruta, **_kwargs: [NodoUsar("a")],
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    with pytest.raises(ImportError, match=r"Ciclo de módulos detectado en usar: a\.co -> a\.co"):
        interp.ejecutar_usar(SimpleNamespace(modulo="a"))


def test_interpretador_usar_proyecto_detecta_ciclo_indirecto(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoUsar
    import pytest

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    for nombre in ("a", "b", "c"):
        (proyecto / f"{nombre}.co").write_text("", encoding="utf-8")

    def fake_cargar_ast_modulo(ruta, **kwargs):
        siguiente = {"a.co": "b", "b.co": "c", "c.co": "a"}[Path(ruta).name]
        return [NodoUsar(siguiente)]

    monkeypatch.setattr("pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo)

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    with pytest.raises(ImportError, match=r"a\.co -> b\.co -> c\.co -> a\.co"):
        interp.ejecutar_usar(SimpleNamespace(modulo="a"))


def test_interpretador_usar_proyecto_modulo_inexistente_muestra_nombre_y_ruta(tmp_path):
    import pytest

    proyecto = tmp_path / "app"
    (proyecto / "utilidades").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    ruta_buscada = proyecto / "utilidades" / "faltante.co"

    interp = InterpretadorCobra(main_file=principal)
    with pytest.raises(FileNotFoundError) as excinfo:
        interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.faltante"))

    mensaje = str(excinfo.value)
    assert "utilidades.faltante" in mensaje
    assert str(ruta_buscada) in mensaje


def test_import_archivo_co_mantiene_ejecutar_import(monkeypatch, tmp_path):
    principal = tmp_path / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = tmp_path / "archivo.co"
    modulo.write_text("", encoding="utf-8")
    llamadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        llamadas.append((ruta, kwargs["modules_path"]))
        return []

    monkeypatch.setattr("pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo)

    interp = InterpretadorCobra(main_file=principal)
    interp.ejecutar_import(SimpleNamespace(ruta=str(modulo)))

    assert llamadas == [(str(modulo), Path.home() / ".cobra" / "modules")]


def test_validacion_modulo_proyecto_acepta_puntos_y_rechaza_rutas_windows_posix():
    import pytest
    from pcobra.cobra.usar_loader import validar_nombre_modulo_cobra_proyecto

    assert validar_nombre_modulo_cobra_proyecto("utilidades.fechas") == ("utilidades", "fechas")

    for nombre in ("..", "a/../b", "../b", r"C:\\x", "a\\b"):
        with pytest.raises(ValueError):
            validar_nombre_modulo_cobra_proyecto(nombre)


def test_resolver_modulo_cobra_proyecto_bloquea_traversal_estable(tmp_path):
    import pytest

    proyecto = tmp_path / "app"
    proyecto.mkdir()

    with pytest.raises(ValueError, match="traversal"):
        resolver_modulo_cobra_proyecto("..", project_root=proyecto)

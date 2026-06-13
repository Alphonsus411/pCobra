from pathlib import Path
from types import SimpleNamespace

import pytest

from pcobra.cobra.cli.execution_pipeline import PipelineInput, ejecutar_pipeline_explicito
from pcobra.cobra.usar_loader import (
    descubrir_raiz_proyecto,
    obtener_cache_modulos_cobra_proyecto,
    obtener_pila_carga_modulos_cobra_proyecto,
    resolver_modulo_cobra_proyecto,
    usar_modulo,
    validar_nombre_modulo_cobra_proyecto,
)
from pcobra.core.interpreter import InterpretadorCobra


@pytest.fixture(autouse=True)
def limpiar_estado_usar_proyecto_compartido():
    """Aísla la caché/pila global compartida entre tests de módulos de proyecto."""

    obtener_cache_modulos_cobra_proyecto().clear()
    obtener_pila_carga_modulos_cobra_proyecto().clear()
    yield
    obtener_cache_modulos_cobra_proyecto().clear()
    obtener_pila_carga_modulos_cobra_proyecto().clear()


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


def test_ejecucion_desde_cwd_externo_resuelve_usar_con_main_file(
    monkeypatch, tmp_path
):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    externo = tmp_path / "externo"
    (proyecto / "utilidades").mkdir(parents=True)
    externo.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "programas" / "main.co"
    principal.parent.mkdir()
    principal.write_text('usar "utilidades.fechas"\n', encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("var hoy = 13\n", encoding="utf-8")
    rutas_cargadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        rutas_cargadas.append((Path(ruta), kwargs["modules_path"]))
        return [NodoAsignacion("hoy", NodoValor(13), declaracion=True)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )
    monkeypatch.chdir(externo)

    setup, _resultado = ejecutar_pipeline_explicito(
        PipelineInput(
            codigo=principal.read_text(encoding="utf-8"),
            interpretador_cls=InterpretadorCobra,
            safe_mode=False,
            main_file=principal,
        )
    )

    assert rutas_cargadas == [(modulo.resolve(), str(proyecto.resolve()))]
    assert setup.interpretador.variables["hoy"] == 13
    assert setup.interpretador._project_root == proyecto.resolve()


def test_ejecucion_real_desde_cwd_externo_resuelve_usar_en_cobra_toml(
    monkeypatch, tmp_path
):
    proyecto = tmp_path / "app"
    externo = tmp_path / "externo"
    (proyecto / "utilidades").mkdir(parents=True)
    externo.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "programas" / "main.co"
    principal.parent.mkdir()
    principal.write_text('usar "utilidades.fechas"\n', encoding="utf-8")
    (proyecto / "utilidades" / "fechas.co").write_text(
        "var hoy = 13\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(externo)

    setup, _resultado = ejecutar_pipeline_explicito(
        PipelineInput(
            codigo=principal.read_text(encoding="utf-8"),
            interpretador_cls=InterpretadorCobra,
            safe_mode=False,
            main_file=principal,
        )
    )

    assert setup.interpretador.variables["hoy"] == 13
    assert setup.interpretador._project_root == proyecto.resolve()


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
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
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
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
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
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
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
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
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

    assert (
        resolver_modulo_cobra_proyecto("a.b.c", project_root=proyecto) == modulo.resolve()
    )


def test_usar_modulo_api_resuelve_util_misma_carpeta(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "util.co"
    modulo.write_text("", encoding="utf-8")
    rutas_cargadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        rutas_cargadas.append((Path(ruta), kwargs["modules_path"]))
        return [NodoAsignacion("valor_util", NodoValor(7), declaracion=True)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    exports = usar_modulo("util", current_file=principal)

    assert exports["valor_util"] == 7
    assert rutas_cargadas == [(modulo.resolve(), str(proyecto.resolve()))]


def test_usar_modulo_api_resuelve_utilidades_fechas(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    (proyecto / "utilidades").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("", encoding="utf-8")
    rutas_cargadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        rutas_cargadas.append((Path(ruta), kwargs["modules_path"]))
        return [NodoAsignacion("hoy", NodoValor("2026-06-13"), declaracion=True)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    exports = usar_modulo("utilidades.fechas", current_file=principal)

    assert exports["hoy"] == "2026-06-13"
    assert rutas_cargadas == [(modulo.resolve(), str(proyecto.resolve()))]


def test_usar_modulo_api_nombre_simple_inexistente_mantiene_error_publico(tmp_path):
    import pytest

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")

    with pytest.raises(PermissionError, match="no canónico"):
        usar_modulo("numpy", current_file=principal)


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

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="saludos"))

    assert rutas_cargadas == [modulo.resolve()]


def test_interpretador_usar_proyecto_util_misma_carpeta(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "util.co"
    modulo.write_text("", encoding="utf-8")
    rutas_cargadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        rutas_cargadas.append((Path(ruta), kwargs["modules_path"]))
        return [NodoAsignacion("valor_util", NodoValor(11), declaracion=True)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="util"))

    assert interp.variables["valor_util"] == 11
    assert rutas_cargadas == [(modulo.resolve(), str(proyecto.resolve()))]


def test_interpretador_usar_proyecto_utilidades_fechas(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    (proyecto / "utilidades").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "utilidades" / "fechas.co"
    modulo.write_text("", encoding="utf-8")
    rutas_cargadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        rutas_cargadas.append((Path(ruta), kwargs["modules_path"]))
        return [NodoAsignacion("hoy", NodoValor("2026-06-13"), declaracion=True)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    assert interp.variables["hoy"] == "2026-06-13"
    assert rutas_cargadas == [(modulo.resolve(), str(proyecto.resolve()))]

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

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )
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

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="a.b.c"))
    interp.ejecutar_usar(SimpleNamespace(modulo="a.b.c"))

    assert cargas == [modulo.resolve()]
    assert interp.variables["valor"] == 1


def test_api_e_interpretador_comparten_cache_por_ruta_canonica(monkeypatch, tmp_path):
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
        cargas.append(Path(ruta).resolve(strict=False))
        return [NodoAsignacion("hoy", NodoValor(len(cargas)), declaracion=True)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )
    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    raiz_equivalente = proyecto / "utilidades" / ".."
    assert usar_modulo("utilidades.fechas", project_root=raiz_equivalente)["hoy"] == 1

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.fechas"))

    assert interp.variables["hoy"] == 1
    assert cargas == [modulo.resolve()]
    assert list(obtener_cache_modulos_cobra_proyecto()) == [modulo.resolve()]


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
        "pcobra.core.import_utils.cargar_ast_modulo",
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

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

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

    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(main_file=principal)
    interp.ejecutar_import(SimpleNamespace(ruta=str(modulo)))

    assert llamadas == [(str(modulo), str(Path.home() / ".cobra" / "modules"))]


def test_validacion_modulo_proyecto_acepta_puntos():
    assert validar_nombre_modulo_cobra_proyecto("utilidades.fechas") == ("utilidades", "fechas")


@pytest.mark.parametrize(
    "nombre",
    [
        "..",
        "../externo",
        "../externo.co",
        "a/../b",
        "a..b",
        "utilidades..fechas",
        ".oculto",
        "utilidades.",
        "/tmp/externo",
        r"C:\\tmp\\externo",
        "C:externo",
        "a\\b",
        "a/b",
        "externo-co",
        "externo@red",
        "externo$",
        "externo*",
        "externo?",
        "externo<privado>",
        "externo|privado",
        "externo;privado",
        "externo`privado",
        "externo privado",
    ],
)
def test_validacion_modulo_proyecto_rechaza_traversal_rutas_y_caracteres_prohibidos(nombre):
    with pytest.raises(ValueError):
        validar_nombre_modulo_cobra_proyecto(nombre)


@pytest.mark.parametrize(
    "nombre",
    [
        "..",
        "../externo",
        "../externo.co",
        "a/../b",
        "utilidades..fechas",
    ],
)
def test_resolver_modulo_cobra_proyecto_rechaza_intentos_posix_de_escape(tmp_path, nombre):
    proyecto = tmp_path / "app"
    proyecto.mkdir()
    externo = tmp_path / "externo.co"
    externo.write_text("var secreto = 1\n", encoding="utf-8")

    with pytest.raises(ValueError):
        resolver_modulo_cobra_proyecto(nombre, project_root=proyecto)


@pytest.mark.parametrize(
    "nombre",
    [
        r"C:\\tmp\\externo",
        "C:externo",
        "a\\b",
    ],
)
def test_resolver_modulo_cobra_proyecto_rechaza_rutas_windows_sin_depender_de_windows(tmp_path, nombre):
    proyecto = tmp_path / "app"
    proyecto.mkdir()

    with pytest.raises(ValueError):
        resolver_modulo_cobra_proyecto(nombre, project_root=proyecto)


def test_resolver_modulo_cobra_proyecto_no_devuelve_symlink_fuera_de_project_root(tmp_path):
    proyecto = tmp_path / "app"
    proyecto.mkdir()
    externo = tmp_path / "externo.co"
    externo.write_text("var secreto = 1\n", encoding="utf-8")
    enlace = proyecto / "escape.co"
    enlace.symlink_to(externo)

    with pytest.raises(ValueError, match="fuera de la raíz autorizada"):
        resolver_modulo_cobra_proyecto("escape", project_root=proyecto)

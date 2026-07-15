from pathlib import Path
from types import SimpleNamespace

import pytest

from pcobra.cobra.cli.execution_pipeline import PipelineInput, ejecutar_pipeline_explicito
from pcobra.cobra.usar_loader import (
    descubrir_raiz_proyecto,
    obtener_cache_ast_import_co,
    formatear_ciclo_modulos_cobra_proyecto,
    obtener_cache_modulos_cobra_proyecto,
    obtener_pila_carga_modulos_cobra_proyecto,
    resolver_modulo_cobra_proyecto,
    resolver_ruta_canonica_modulo_cobra_proyecto,
    usar_modulo,
    validar_nombre_modulo_cobra_proyecto,
)
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.ast_nodes import (
    NodoAsignacion,
    NodoExport,
    NodoImport,
    NodoUsar,
    NodoValor,
)


@pytest.fixture(autouse=True)
def limpiar_estado_usar_proyecto_compartido():
    """Aísla la caché/pila global compartida entre tests de módulos de proyecto."""

    obtener_cache_ast_import_co().clear()
    obtener_cache_modulos_cobra_proyecto().clear()
    obtener_pila_carga_modulos_cobra_proyecto().clear()
    yield
    obtener_cache_ast_import_co().clear()
    obtener_cache_modulos_cobra_proyecto().clear()
    obtener_pila_carga_modulos_cobra_proyecto().clear()


def test_formatear_ciclo_modulos_usa_rutas_relativas_en_subcarpetas(tmp_path):
    proyecto = tmp_path / "app"
    anidados = proyecto / "utilidades" / "internas"
    anidados.mkdir(parents=True)
    modulo_a = anidados / "a.co"
    modulo_b = anidados / "b.co"
    modulo_a.write_text("", encoding="utf-8")
    modulo_b.write_text("", encoding="utf-8")

    cadena = formatear_ciclo_modulos_cobra_proyecto(
        modulo_a,
        project_root=proyecto,
        loading_stack=[modulo_a, modulo_b],
    )

    assert (
        cadena
        == "utilidades/internas/a.co -> utilidades/internas/b.co -> "
        "utilidades/internas/a.co"
    )

def test_formatear_ciclo_modulos_fallback_canonico_fuera_de_project_root(tmp_path):
    proyecto = tmp_path / "app"
    externo = tmp_path / "externo"
    proyecto.mkdir()
    externo.mkdir()
    modulo = externo / "a.co"
    modulo.write_text("", encoding="utf-8")

    cadena = formatear_ciclo_modulos_cobra_proyecto(
        modulo, project_root=proyecto, loading_stack=[modulo]
    )

    assert cadena == f"{modulo.resolve()} -> {modulo.resolve()}"

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
        assert str(exc) == (
            "Ciclo de módulos detectado en usar: "
            "utilidades/a.co -> utilidades/b.co -> utilidades/a.co"
        )
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


def test_cobertura_explicita_usar_resuelve_util_subcarpeta_y_anidado(tmp_path):
    """Documenta los tres casos nominales pedidos para `usar` de proyecto.

    Mantiene la cobertura explícita sin tocar gramática, tokens, Lexer ni Parser:
    - `usar util` -> `util.co` en la raíz del proyecto;
    - `usar utilidades.fechas` -> subcarpeta;
    - `usar a.b.c` -> módulo anidado.
    """

    proyecto = tmp_path / "app"
    rutas_esperadas = {
        "util": proyecto / "util.co",
        "utilidades.fechas": proyecto / "utilidades" / "fechas.co",
        "a.b.c": proyecto / "a" / "b" / "c.co",
    }
    for ruta in rutas_esperadas.values():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text("", encoding="utf-8")

    for nombre_modulo, ruta_esperada in rutas_esperadas.items():
        assert (
            resolver_modulo_cobra_proyecto(nombre_modulo, project_root=proyecto)
            == ruta_esperada.resolve()
        )


def test_usar_modulo_api_resuelve_util_misma_carpeta(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    (proyecto / "utilidades" / "internas").mkdir(parents=True)
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



def test_resolver_ruta_canonica_modulo_cobra_proyecto_normaliza_project_root_equivalente(tmp_path):
    proyecto = tmp_path / "app"
    subdir = proyecto / "subdir"
    modulo = proyecto / "utilidades" / "fechas.co"
    subdir.mkdir(parents=True)
    modulo.parent.mkdir(parents=True)
    modulo.write_text("", encoding="utf-8")

    ruta_desde_root = resolver_ruta_canonica_modulo_cobra_proyecto(
        "utilidades.fechas", project_root=proyecto
    )
    ruta_desde_root_equivalente = resolver_ruta_canonica_modulo_cobra_proyecto(
        "utilidades.fechas", project_root=subdir / ".."
    )

    assert ruta_desde_root == modulo.resolve()
    assert ruta_desde_root_equivalente == modulo.resolve()
    assert ruta_desde_root_equivalente == ruta_desde_root


def test_usar_modulo_cachea_referencias_equivalentes_al_mismo_co(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoAsignacion, NodoValor

    proyecto = tmp_path / "app"
    subdir = proyecto / "subdir"
    modulo = proyecto / "utilidades" / "fechas.co"
    subdir.mkdir(parents=True)
    modulo.parent.mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo.write_text("", encoding="utf-8")
    cargas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        cargas.append((Path(ruta).resolve(strict=False), kwargs["modules_path"]))
        return [NodoAsignacion("hoy", NodoValor(len(cargas)), declaracion=True)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    exports_root = usar_modulo(
        "utilidades.fechas", project_root=proyecto, current_file=principal
    )
    exports_root_equivalente = usar_modulo(
        "utilidades.fechas", project_root=subdir / "..", current_file=principal
    )

    assert exports_root["hoy"] == 1
    assert exports_root_equivalente["hoy"] == 1
    assert cargas == [(modulo.resolve(), str(proyecto.resolve()))]
    assert list(obtener_cache_modulos_cobra_proyecto()) == [modulo.resolve()]

def test_api_e_interpretador_aislan_cache_por_ejecucion_independiente(monkeypatch, tmp_path):
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

    assert interp.variables["hoy"] == 2
    assert cargas == [modulo.resolve(), modulo.resolve()]
    assert list(obtener_cache_modulos_cobra_proyecto()) == [modulo.resolve()]
    assert list(interp._usar_module_cache) == [modulo.resolve()]
    assert interp._usar_module_cache is not obtener_cache_modulos_cobra_proyecto()


def test_interpretes_independientes_no_comparten_cache_ni_pila_usar(tmp_path):
    proyecto_a = tmp_path / "a"
    proyecto_b = tmp_path / "b"
    proyecto_a.mkdir()
    proyecto_b.mkdir()
    principal_a = proyecto_a / "main.co"
    principal_b = proyecto_b / "main.co"
    principal_a.write_text("", encoding="utf-8")
    principal_b.write_text("", encoding="utf-8")

    interp_a = InterpretadorCobra(safe_mode=False, main_file=principal_a)
    interp_b = InterpretadorCobra(safe_mode=False, main_file=principal_b)

    assert interp_a._usar_module_cache is not interp_b._usar_module_cache
    assert interp_a._usar_loading_stack is not interp_b._usar_loading_stack
    assert interp_a._import_ast_cache is not interp_b._import_ast_cache


def test_interpretador_usar_proyecto_detecta_ciclo_directo_self(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoUsar
    import pytest

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    anidados = proyecto / "utilidades" / "internas"
    anidados.mkdir(parents=True)
    modulo = anidados / "a.co"
    modulo.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo",
        lambda _ruta, **_kwargs: [NodoUsar("utilidades.internas.a")],
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    with pytest.raises(
        ImportError,
        match=(
            r"Ciclo de módulos detectado en usar: "
            r"utilidades/internas/a\.co -> utilidades/internas/a\.co"
        ),
    ):
        interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.internas.a"))


def test_interpretador_usar_proyecto_detecta_ciclo_indirecto(monkeypatch, tmp_path):
    from pcobra.core.ast_nodes import NodoUsar
    import pytest

    proyecto = tmp_path / "app"
    (proyecto / "utilidades" / "internas").mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    for nombre in ("a", "b", "c"):
        (proyecto / "utilidades" / "internas" / f"{nombre}.co").write_text(
            "", encoding="utf-8"
        )

    def fake_cargar_ast_modulo(ruta, **kwargs):
        siguiente = {
            "a.co": "utilidades.internas.b",
            "b.co": "utilidades.internas.c",
            "c.co": "utilidades.internas.a",
        }[Path(ruta).name]
        return [NodoUsar(siguiente)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    with pytest.raises(
        ImportError,
        match=(
            r"utilidades/internas/a\.co -> utilidades/internas/b\.co -> "
            r"utilidades/internas/c\.co -> utilidades/internas/a\.co"
        ),
    ):
        interp.ejecutar_usar(SimpleNamespace(modulo="utilidades.internas.a"))




def test_interpretador_usar_proyecto_detecta_ciclo_directo_en_root_con_mensaje_exacto(
    monkeypatch, tmp_path
):
    from pcobra.core.ast_nodes import NodoUsar

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
    with pytest.raises(ImportError) as excinfo:
        interp.ejecutar_usar(SimpleNamespace(modulo="a"))

    assert str(excinfo.value) == "Ciclo de módulos detectado en usar: a.co -> a.co"
    assert obtener_pila_carga_modulos_cobra_proyecto() == []


def test_interpretador_usar_proyecto_detecta_ciclo_indirecto_en_root_con_cadena_completa(
    monkeypatch, tmp_path
):
    from pcobra.core.ast_nodes import NodoUsar

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    for nombre in ("a", "b", "c"):
        (proyecto / f"{nombre}.co").write_text("", encoding="utf-8")

    def fake_cargar_ast_modulo(ruta, **_kwargs):
        siguiente = {
            "a.co": "b",
            "b.co": "c",
            "c.co": "a",
        }[Path(ruta).name]
        return [NodoUsar(siguiente)]

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    with pytest.raises(ImportError) as excinfo:
        interp.ejecutar_usar(SimpleNamespace(modulo="a"))

    assert str(excinfo.value) == (
        "Ciclo de módulos detectado en usar: a.co -> b.co -> c.co -> a.co"
    )
    assert obtener_pila_carga_modulos_cobra_proyecto() == []


def test_usar_proyecto_limpia_pila_si_falla_cargar_ast_modulo(monkeypatch, tmp_path):
    proyecto = tmp_path / "app"
    proyecto.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "a.co"
    modulo.write_text("", encoding="utf-8")

    def fake_cargar_ast_modulo(_ruta, **_kwargs):
        assert obtener_pila_carga_modulos_cobra_proyecto() == [modulo.resolve()]
        raise RuntimeError("fallo sintético de carga")

    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    with pytest.raises(RuntimeError, match="fallo sintético de carga"):
        usar_modulo("a", project_root=proyecto, current_file=principal)

    assert obtener_pila_carga_modulos_cobra_proyecto() == []

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


def test_resolver_modulo_cobra_proyecto_rechaza_resultado_manipulado_fuera_de_root(
    monkeypatch, tmp_path
):
    from pcobra.cobra import usar_loader
    from pcobra.cobra.imports.resolver import ResolutionResult

    proyecto = tmp_path / "app"
    externo = tmp_path / "externo"
    proyecto.mkdir()
    externo.mkdir()
    ruta_externa = externo / "fechas.co"
    ruta_externa.write_text("", encoding="utf-8")

    class FakeResolver:
        def __init__(self, **_kwargs):
            pass

        def resolve(self, nombre):
            return ResolutionResult(
                request=nombre,
                source="project",
                resolved_name=nombre,
                file_path=str(ruta_externa),
            )

    monkeypatch.setattr(usar_loader, "CobraImportResolver", FakeResolver)

    with pytest.raises(ValueError, match="fuera de la raíz autorizada"):
        resolver_modulo_cobra_proyecto("utilidades.fechas", project_root=proyecto)


def test_resolver_modulo_cobra_proyecto_fallback_devuelve_ruta_canonica(
    monkeypatch, tmp_path
):
    from pcobra.cobra import usar_loader
    from pcobra.cobra.imports.resolver import ResolutionResult

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    ruta_modulo = proyecto / "utilidades" / "fechas.co"
    ruta_modulo.parent.mkdir()
    ruta_modulo.write_text("", encoding="utf-8")

    class FakeResolver:
        def __init__(self, **_kwargs):
            pass

        def resolve(self, nombre):
            ruta_legacy = (
                proyecto / "." / "utilidades" / ".." / "utilidades" / "fechas.co"
            )
            return ResolutionResult(
                request=nombre,
                source="project",
                resolved_name=nombre,
                file_path=str(ruta_legacy),
            )

    ruta_modulo.unlink()
    monkeypatch.setattr(usar_loader, "CobraImportResolver", FakeResolver)

    assert (
        resolver_modulo_cobra_proyecto("utilidades.fechas", project_root=proyecto)
        == ruta_modulo.resolve(strict=False)
    )


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


def test_import_archivo_co_via_nodo_import_usa_flujo_legacy_y_whitelist(
    monkeypatch, tmp_path
):
    """`import 'archivo.co'` conserva el loader legacy de `NodoImport`."""

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    principal = proyecto / "main.co"
    principal.write_text("import 'archivo.co'\n", encoding="utf-8")
    modulo = proyecto / "archivo.co"
    modulo.write_text("var valor_importado = 42\n", encoding="utf-8")
    llamadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        llamadas.append((ruta, kwargs))
        return [NodoAsignacion("valor_importado", NodoValor(42), declaracion=True)]

    import pcobra.core.interpreter as interpreter_module

    monkeypatch.setattr(interpreter_module, "MODULES_PATH", proyecto)
    monkeypatch.setattr(interpreter_module, "IMPORT_WHITELIST", {proyecto})
    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    from pcobra.core.lexer import Lexer
    from pcobra.core.parser import Parser

    ast_principal = Parser(
        Lexer(principal.read_text(encoding="utf-8")).analizar_token()
    ).parsear()

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_import(ast_principal[0])

    assert isinstance(ast_principal[0], NodoImport)
    assert ast_principal[0].ruta == "archivo.co"
    assert interp.variables["valor_importado"] == 42
    assert llamadas == [
        (
            "archivo.co",
            {
                "modules_path": str(proyecto),
                "whitelist": {proyecto},
                "loading_stack": interp._usar_loading_stack,
            },
        )
    ]


def test_usar_loader_no_altera_semantica_de_nodo_import(monkeypatch, tmp_path):
    """`NodoImport` no delega en `usar_modulo` ni aplica semántica pública de `usar`."""

    proyecto = tmp_path / "app"
    proyecto.mkdir()
    principal = proyecto / "main.co"
    principal.write_text("", encoding="utf-8")
    modulo = proyecto / "archivo.co"
    modulo.write_text("", encoding="utf-8")
    llamadas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        llamadas.append(Path(ruta))
        return [
            NodoAsignacion("publico_import", NodoValor("legacy"), declaracion=True),
            NodoAsignacion("_privado_import", NodoValor("visible"), declaracion=True),
        ]

    def fail_usar_modulo(*_args, **_kwargs):
        raise AssertionError("NodoImport no debe usar usar_modulo")

    import pcobra.core.interpreter as interpreter_module

    monkeypatch.setattr(interpreter_module, "MODULES_PATH", proyecto)
    monkeypatch.setattr(interpreter_module, "IMPORT_WHITELIST", {proyecto})
    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )
    monkeypatch.setattr("pcobra.core.interpreter.usar_modulo", fail_usar_modulo)

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_import(NodoImport(str(modulo)))

    assert llamadas == [modulo]
    assert interp.variables["publico_import"] == "legacy"
    assert interp.variables["_privado_import"] == "visible"
    assert "publico_import" not in interp._usar_symbol_metadata


def test_import_archivo_co_y_usar_utilidades_fechas_conviven_sin_semantica_publica_compartida(
    monkeypatch, tmp_path
):
    proyecto = tmp_path / "app"
    utilidades = proyecto / "utilidades"
    utilidades.mkdir(parents=True)
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text(
        "import 'archivo.co'\nusar utilidades.fechas\n", encoding="utf-8"
    )
    archivo = proyecto / "archivo.co"
    fechas = utilidades / "fechas.co"
    archivo.write_text("", encoding="utf-8")
    fechas.write_text("", encoding="utf-8")
    cargas = []

    def fake_cargar_ast_modulo(ruta, **kwargs):
        ruta_path = Path(ruta).resolve()
        cargas.append((ruta_path, kwargs["modules_path"], kwargs["whitelist"]))
        if ruta_path == archivo.resolve():
            return [
                NodoAsignacion("import_publico", NodoValor("legacy"), declaracion=True),
                NodoAsignacion(
                    "_import_privado", NodoValor("legacy-privado"), declaracion=True
                ),
            ]
        if ruta_path == fechas.resolve():
            return [
                NodoExport("fecha_publica"),
                NodoAsignacion("fecha_publica", NodoValor("usar"), declaracion=True),
                NodoAsignacion(
                    "fecha_privada", NodoValor("no-export"), declaracion=True
                ),
            ]
        raise AssertionError(f"Ruta inesperada: {ruta}")

    import pcobra.core.interpreter as interpreter_module

    monkeypatch.setattr(interpreter_module, "MODULES_PATH", proyecto)
    monkeypatch.setattr(interpreter_module, "IMPORT_WHITELIST", {proyecto})
    monkeypatch.setattr(
        "pcobra.core.interpreter.cargar_ast_modulo", fake_cargar_ast_modulo
    )
    monkeypatch.setattr(
        "pcobra.core.import_utils.cargar_ast_modulo", fake_cargar_ast_modulo
    )

    interp = InterpretadorCobra(safe_mode=False, main_file=principal)
    interp.ejecutar_import(NodoImport(str(archivo)))
    interp.ejecutar_usar(NodoUsar("utilidades.fechas"))

    assert interp.variables["import_publico"] == "legacy"
    assert interp.variables["_import_privado"] == "legacy-privado"
    assert interp.variables["fecha_publica"] == "usar"
    assert "fecha_privada" not in interp.variables
    assert "import_publico" not in interp._usar_symbol_metadata
    assert interp._usar_symbol_metadata["fecha_publica"]["module"] == str(
        fechas.resolve()
    )
    assert cargas == [
        (archivo.resolve(), str(proyecto), {proyecto}),
        (fechas.resolve(), str(proyecto.resolve()), {proyecto.resolve()}),
    ]

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


def test_usar_anidado_mantiene_raiz_autorizada_estable_con_current_file(
    monkeypatch, tmp_path
):
    proyecto = tmp_path / "app"
    externo = tmp_path / "externo"
    modulo_dir = proyecto / "a"
    modulo_dir.mkdir(parents=True)
    externo.mkdir()
    (proyecto / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    # Este cobra.toml anidado detecta regresiones: la raíz autorizada debe seguir
    # siendo la descubierta desde main.co, no la del módulo actualmente cargado.
    (modulo_dir / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
    principal = proyecto / "main.co"
    principal.write_text("usar a.b\n", encoding="utf-8")
    (modulo_dir / "b.co").write_text(
        "usar a.c\nvar desde_b = 2\n",
        encoding="utf-8",
    )
    (modulo_dir / "c.co").write_text("var desde_c = 3\n", encoding="utf-8")

    rutas_cargadas = []
    roots_usados = []
    current_files_usados = []
    original_usar_modulo = usar_modulo

    def spy_usar_modulo(nombre, *, project_root=None, current_file=None):
        roots_usados.append(Path(project_root).resolve())
        current_files_usados.append(
            Path(current_file).resolve() if current_file is not None else None
        )
        exports = original_usar_modulo(
            nombre,
            project_root=project_root,
            current_file=current_file,
        )
        rutas_cargadas.extend(
            Path(metadata["module"]).resolve()
            for metadata in exports.get("metadata", {}).values()
        )
        return exports

    import pcobra.core.interpreter as interpreter_module

    monkeypatch.setattr(interpreter_module, "usar_modulo", spy_usar_modulo)
    monkeypatch.chdir(externo)

    setup, _resultado = ejecutar_pipeline_explicito(
        PipelineInput(
            codigo=principal.read_text(encoding="utf-8"),
            interpretador_cls=InterpretadorCobra,
            safe_mode=False,
            main_file=principal,
        )
    )

    assert setup.interpretador.variables["desde_b"] == 2
    assert setup.interpretador._project_root == proyecto.resolve()
    assert roots_usados == [proyecto.resolve(), proyecto.resolve()]
    assert current_files_usados == [
        principal.resolve(),
        (modulo_dir / "b.co").resolve(),
    ]
    assert (modulo_dir / "b.co").resolve() in rutas_cargadas
    assert (modulo_dir / "c.co").resolve() in rutas_cargadas
    assert all(ruta.is_relative_to(proyecto.resolve()) for ruta in rutas_cargadas)

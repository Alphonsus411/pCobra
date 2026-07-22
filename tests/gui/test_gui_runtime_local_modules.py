"""Regresión de módulos Cobra locales ejecutados por la ruta GUI."""

from pathlib import Path
from types import SimpleNamespace

from pcobra.gui import runtime


def _crear_proyecto(
    raiz: Path,
    *,
    factor: int,
) -> tuple[Path, str]:
    raiz.mkdir(parents=True)

    (raiz / "utilidades.cobra").write_text(
        (
            "func duplicar(valor):\n"
            f"    retorno valor * {factor}\n"
            "fin\n"
        ),
        encoding="utf-8",
    )

    codigo = 'usar "utilidades"\nimprimir(duplicar(21))\n'
    principal = raiz / "principal.cobra"
    principal.write_text(codigo, encoding="utf-8")
    return principal, codigo


def test_handler_gui_resuelve_modulo_local_desde_archivo_activo(
    tmp_path: Path,
) -> None:
    principal_a, codigo = _crear_proyecto(
        tmp_path / "proyecto_a",
        factor=2,
    )
    principal_b, _ = _crear_proyecto(
        tmp_path / "proyecto_b",
        factor=3,
    )

    estado = runtime.GuiFileState(ruta=principal_a)
    salida = SimpleNamespace(value="")
    selector = SimpleNamespace(value="python")
    activar = SimpleNamespace(value=False)
    actualizaciones: list[bool] = []
    page = SimpleNamespace(
        update=lambda: actualizaciones.append(True)
    )

    handler = runtime.crear_handler_ejecucion(
        leer_codigo=lambda: codigo,
        obtener_main_file=lambda: estado.ruta,
        salida=salida,
        selector=selector,
        activar=activar,
        page=page,
    )

    handler(None)
    assert salida.value.strip() == "42"

    # Debe consultar el archivo activo al ejecutar, no al crear el handler.
    estado.ruta = principal_b
    handler(None)

    assert salida.value.strip() == "63"
    assert len(actualizaciones) == 2

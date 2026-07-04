from pathlib import Path

import pytest

from pcobra.corelibs import temporal


def test_superficie_publica_temporal() -> None:
    assert temporal.__all__ == ["archivo_temporal", "directorio_temporal", "limpiar"]


def test_archivo_temporal_devuelve_str_y_cierra_descriptor() -> None:
    ruta = temporal.archivo_temporal(prefijo="cobra-", sufijo=".txt", texto=True)

    try:
        assert isinstance(ruta, str)
        archivo = Path(ruta)
        assert archivo.exists()
        assert archivo.name.startswith("cobra-")
        assert archivo.suffix == ".txt"
        archivo.write_text("ok", encoding="utf-8")
        assert archivo.read_text(encoding="utf-8") == "ok"
    finally:
        temporal.limpiar(ruta)


def test_directorio_temporal_y_limpieza_recursiva() -> None:
    ruta = temporal.directorio_temporal(prefijo="cobra-dir-")
    directorio = Path(ruta)
    archivo = directorio / "datos.txt"
    archivo.write_text("cobra", encoding="utf-8")

    assert isinstance(ruta, str)
    assert directorio.exists()
    assert directorio.name.startswith("cobra-dir-")
    assert temporal.limpiar(ruta) is True
    assert not directorio.exists()


def test_limpiar_archivo_existente_y_ruta_inexistente(tmp_path: Path) -> None:
    archivo = tmp_path / "temporal.txt"
    archivo.write_text("cobra", encoding="utf-8")

    assert temporal.limpiar(archivo) is True
    assert temporal.limpiar(archivo) is False


def test_argumentos_invalidos_generan_mensajes_deterministas() -> None:
    with pytest.raises(TypeError, match="prefijo debe ser texto o None"):
        temporal.archivo_temporal(prefijo=123)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="sufijo debe ser texto o None"):
        temporal.archivo_temporal(sufijo=123)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="texto debe ser booleano"):
        temporal.archivo_temporal(texto="si")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="ruta no puede estar vacía"):
        temporal.limpiar("")

from pathlib import Path

import pytest

from pcobra.corelibs import _sandbox_paths


def test_resuelve_ruta_existente_desde_raiz_configurada(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))
    archivo = tmp_path / "datos.txt"
    archivo.write_text("ok", encoding="utf-8")

    assert _sandbox_paths.resolver_ruta_existente("datos.txt") == archivo


def test_raiz_por_defecto_es_privada(monkeypatch):
    monkeypatch.delenv("COBRA_IO_BASE_DIR", raising=False)
    monkeypatch.setattr(_sandbox_paths, "_raiz_privada", None)

    destino = _sandbox_paths.resolver_destino_nuevo("datos.txt")

    assert destino.parent != Path.cwd().resolve()
    assert destino.parent.stat().st_mode & 0o077 == 0


@pytest.mark.parametrize(
    "ruta",
    ["/etc/passwd", r"C:\Windows\system.ini", r"\\servidor\recurso\dato"],
)
def test_rechaza_rutas_absolutas_de_ambas_plataformas(monkeypatch, tmp_path, ruta):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))

    with pytest.raises(ValueError, match="absolutas"):
        _sandbox_paths.resolver_ruta_existente(ruta)


@pytest.mark.parametrize("ruta", ["../dato", "carpeta/../../dato", r"carpeta\..\..\dato"])
def test_rechaza_componentes_de_traversal(monkeypatch, tmp_path, ruta):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))

    with pytest.raises(ValueError, match=r"\.\."):
        _sandbox_paths.resolver_destino_nuevo(ruta)


def test_rechaza_symlink_existente_que_sale_de_la_raiz(monkeypatch, tmp_path):
    raiz = tmp_path / "raiz"
    exterior = tmp_path / "exterior"
    raiz.mkdir()
    exterior.mkdir()
    secreto = exterior / "secreto.txt"
    secreto.write_text("no", encoding="utf-8")
    (raiz / "enlace").symlink_to(exterior, target_is_directory=True)
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(raiz))

    with pytest.raises(ValueError, match="fuera"):
        _sandbox_paths.resolver_ruta_existente("enlace/secreto.txt")


@pytest.mark.parametrize("ruta", ["carpeta/dato.txt", r"carpeta\dato.txt"])
def test_normaliza_separadores_posix_y_windows(monkeypatch, tmp_path, ruta):
    carpeta = tmp_path / "carpeta"
    carpeta.mkdir()
    archivo = carpeta / "dato.txt"
    archivo.write_text("ok", encoding="utf-8")
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))

    assert _sandbox_paths.resolver_ruta_existente(ruta) == archivo


def test_destino_inexistente_valida_symlinks_del_padre(monkeypatch, tmp_path):
    raiz = tmp_path / "raiz"
    exterior = tmp_path / "exterior"
    raiz.mkdir()
    exterior.mkdir()
    (raiz / "enlace").symlink_to(exterior, target_is_directory=True)
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(raiz))

    with pytest.raises(ValueError, match="fuera"):
        _sandbox_paths.resolver_destino_nuevo("enlace/nuevo.txt")


def test_modos_distinguen_existencia_del_objetivo(monkeypatch, tmp_path):
    monkeypatch.setenv("COBRA_IO_BASE_DIR", str(tmp_path))

    with pytest.raises(FileNotFoundError):
        _sandbox_paths.resolver_ruta_existente("nuevo.txt")
    assert _sandbox_paths.resolver_destino_nuevo("nuevo.txt") == tmp_path / "nuevo.txt"


def test_modulo_no_se_exporta_desde_corelibs():
    assert "_sandbox_paths" not in __import__("pcobra.corelibs", fromlist=["__all__"]).__all__

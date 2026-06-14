from pathlib import Path

from pcobra.gui import runtime


def test_es_archivo_cobra_prioriza_extensiones_documentadas():
    assert runtime.es_archivo_cobra("programa.co")
    assert runtime.es_archivo_cobra("paquete.COBRA")
    assert not runtime.es_archivo_cobra("README.md")


def test_listar_directorio_cobra_filtra_y_ordena(tmp_path: Path):
    (tmp_path / "zeta").mkdir()
    (tmp_path / "beta.co").write_text("", encoding="utf-8")
    (tmp_path / "alfa.cobra").write_text("", encoding="utf-8")
    (tmp_path / "ignorado.py").write_text("", encoding="utf-8")

    assert [path.name for path in runtime.listar_directorio_cobra(tmp_path)] == [
        "zeta",
        "alfa.cobra",
        "beta.co",
    ]


def test_escribir_archivo_texto_no_parsea_ni_modifica_contenido(tmp_path: Path):
    (tmp_path / "sub").mkdir()
    destino = tmp_path / "sub" / "codigo.co"
    codigo = "var x = 1\ntexto inválido para parser ???\n"

    escrito = runtime.escribir_archivo_texto(destino, codigo)

    assert escrito == codigo
    assert destino.read_text(encoding="utf-8") == codigo


def test_escribir_archivo_texto_propaga_ruta_inexistente(tmp_path: Path):
    destino = tmp_path / "no_existe" / "codigo.co"

    try:
        runtime.escribir_archivo_texto(destino, "contenido")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("La escritura debe fallar si el directorio no existe")

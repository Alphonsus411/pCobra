from pathlib import Path

from pcobra.cobra.packaging import (
    MANIFEST_NAME,
    construir_paquete,
    crear_paquete,
    extraer_paquete,
    inspeccionar_paquete,
    validar_paquete,
)


def test_paquete_cobra_conserva_estructura_y_recursos(tmp_path: Path):
    proyecto = tmp_path / "demo"
    crear_paquete(proyecto, nombre="demo", version="1.0.0")
    (proyecto / "src" / "main.cobra").write_text("imprimir('hola')\n", encoding="utf-8")
    (proyecto / "README.md").write_text("# Demo\n", encoding="utf-8")
    (proyecto / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
    (proyecto / "assets").mkdir()
    (proyecto / "assets" / "dato.txt").write_text("recurso", encoding="utf-8")

    paquete = construir_paquete(proyecto, tmp_path / "demo.co")

    info = validar_paquete(paquete)
    assert info.manifest["format"] == "cobra-package-v1"
    assert MANIFEST_NAME in info.files
    assert "src/main.cobra" in info.files
    assert "Dockerfile" in info.files
    assert "assets/dato.txt" in info.files

    inspeccion = inspeccionar_paquete(paquete)
    assert inspeccion.checksum

    destino = extraer_paquete(paquete, tmp_path / "instalado")
    assert (destino / "src" / "main.cobra").read_text(encoding="utf-8") == "imprimir('hola')\n"

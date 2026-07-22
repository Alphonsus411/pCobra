"""Gate de auditoría para el contrato fuente/paquete de Cobra."""

from pathlib import Path
import subprocess
import zipfile

from pcobra.cobra.imports.resolver import CobraImportResolver
from pcobra.cobra.packaging import MANIFEST_NAME


def test_resolvedor_local_solo_declara_candidatos_cobra(tmp_path: Path) -> None:
    (tmp_path / "modulo.co").write_text("imprimir(13)", encoding="utf-8")
    assert CobraImportResolver(project_root=tmp_path)._resolve_local_file_module("modulo") is None

    fuente = tmp_path / "modulo.cobra"
    fuente.write_text("imprimir(42)", encoding="utf-8")
    resultado = CobraImportResolver(project_root=tmp_path)._resolve_local_file_module("modulo")
    assert resultado is not None
    assert resultado.file_path == str(fuente.resolve())


def test_todos_los_co_rastreados_son_paquetes_validos() -> None:
    raiz = Path(__file__).resolve().parents[1]
    salida = subprocess.run(
        ["git", "ls-files", "-z", "*.co"],
        cwd=raiz,
        check=True,
        capture_output=True,
    ).stdout
    rutas = [Path(raw.decode()) for raw in salida.split(b"\0") if raw]

    invalidos: list[str] = []
    for relativa in rutas:
        paquete = raiz / relativa
        if not zipfile.is_zipfile(paquete):
            invalidos.append(f"{relativa}: no es ZIP")
            continue
        with zipfile.ZipFile(paquete) as archivo:
            if MANIFEST_NAME not in archivo.namelist():
                invalidos.append(f"{relativa}: falta {MANIFEST_NAME}")
    assert not invalidos, "Archivos .co rastreados inválidos: " + "; ".join(invalidos)

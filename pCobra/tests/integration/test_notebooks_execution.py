import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat")

NOTEBOOKS = list(Path("notebooks").rglob("*.ipynb"))


@pytest.mark.parametrize("notebook_path", NOTEBOOKS)
def test_notebook_execution(notebook_path, tmp_path):
    has_papermill = importlib.util.find_spec("papermill") is not None
    has_nbconvert = importlib.util.find_spec("nbconvert") is not None

    if not has_papermill and not has_nbconvert:
        pytest.skip("Se requiere papermill o nbconvert")

    executed = tmp_path / notebook_path.name

    if has_papermill:
        import papermill

        papermill.execute_notebook(
            str(notebook_path),
            str(executed),
            kernel_name="python3",
        )
    else:
        cmd = [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=300",
            "--ExecutePreprocessor.kernel_name=python3",
            "--output",
            executed.name,
            "--output-dir",
            str(tmp_path),
            str(notebook_path),
        ]
        subprocess.run(cmd, check=True)

    nb = nbformat.read(executed, as_version=nbformat.NO_CONVERT)
    for cell in nb.get("cells", []):
        for output in cell.get("outputs", []):
            assert output.get("output_type") != "error", f"Errores en {notebook_path}"

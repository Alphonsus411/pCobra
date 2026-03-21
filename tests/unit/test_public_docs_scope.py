from pathlib import Path


EXPERIMENTAL_DOCS = [
    Path("docs/experimental/README.md"),
    Path("docs/experimental/llvm_prototype.md"),
    Path("docs/experimental/construcciones_llvm_ir.md"),
    Path("docs/experimental/soporte_latex.md"),
    Path("docs/experimental/limitaciones_wasm_reverse.md"),
]

REMOVED_PUBLIC_DOCS = [
    Path("docs/llvm_prototype.md"),
    Path("docs/construcciones_llvm_ir.md"),
    Path("docs/soporte_latex.md"),
    Path("docs/limitaciones_wasm_reverse.md"),
]


def test_experimental_docs_estan_segregados_y_marcados():
    for path in EXPERIMENTAL_DOCS:
        assert path.exists(), f"Falta documento experimental: {path}"
        contenido = path.read_text(encoding="utf-8").lower()
        assert "experimental" in contenido
        assert "política" in contenido


def test_docs_experimentales_ya_no_viven_en_rutas_publicas_principales():
    for path in REMOVED_PUBLIC_DOCS:
        assert not path.exists(), f"La ruta antigua debe haber sido movida: {path}"


def test_politica_y_docs_clave_explican_separacion_de_experimentos_y_reverse():
    policy = Path("docs/targets_policy.md").read_text(encoding="utf-8").lower()
    assert "docs/experimental/" in policy
    assert "orígenes reverse" in policy

    lenguajes = Path("docs/lenguajes.rst").read_text(encoding="utf-8").lower()
    assert "no targets de salida" in lenguajes

    hololang = Path("docs/frontend/hololang.rst").read_text(encoding="utf-8").lower()
    assert "hololang`` en ``cobra compilar``" in hololang

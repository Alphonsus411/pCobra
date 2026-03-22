import re
from pathlib import Path

from scripts.targets_policy_common import PUBLIC_TEXT_PATHS


EXPERIMENTAL_DOCS = [
    Path("docs/experimental/README.md"),
    Path("docs/experimental/llvm_prototype.md"),
    Path("docs/experimental/construcciones_llvm_ir.md"),
    Path("docs/experimental/soporte_latex.md"),
    Path("docs/experimental/limitaciones_wasm_reverse.md"),
    Path("docs/experimental/hololang_pipeline.md"),
]

REMOVED_PUBLIC_DOCS = [
    Path("docs/llvm_prototype.md"),
    Path("docs/construcciones_llvm_ir.md"),
    Path("docs/soporte_latex.md"),
    Path("docs/limitaciones_wasm_reverse.md"),
    Path("docs/frontend/hololang.rst"),
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


PUBLIC_GUIDES_WITHOUT_RETIRED_REVERSE_REFERENCES = [
    Path("README.md"),
    Path("docs/instalacion.md"),
]

RETIRED_REVERSE_PUBLIC_TERMS = [
    "reverse wasm",
    "wasm reverse",
    "extra legado de reverse wasm",
]


def test_guias_publicas_no_reintroducen_reverse_wasm_ni_extras_retirados():
    for path in PUBLIC_GUIDES_WITHOUT_RETIRED_REVERSE_REFERENCES:
        contenido = path.read_text(encoding="utf-8").lower()
        for termino in RETIRED_REVERSE_PUBLIC_TERMS:
            assert termino not in contenido, (
                f"La guía pública {path} no debe reintroducir menciones retiradas: {termino}"
            )


def test_documentacion_de_tiers_no_sobredimensiona_contrato_holobit():
    plan = Path("docs/frontend/transpilers_tier_plan.md").read_text(encoding="utf-8").lower()
    assert "javascript figura como `partial`" in plan
    assert "javascript figura como `full`" not in plan


def test_politica_y_docs_clave_explican_separacion_de_experimentos_y_reverse():
    policy = Path("docs/targets_policy.md").read_text(encoding="utf-8").lower()
    assert "docs/experimental/" in policy
    assert "orígenes reverse" in policy
    assert "fuera de la navegación pública principal" in policy

    lenguajes = Path("docs/lenguajes.rst").read_text(encoding="utf-8").lower()
    assert "no targets de salida" in lenguajes

    frontend = Path("docs/frontend/index.rst").read_text(encoding="utf-8").lower()
    assert "ir **interno**" in frontend or "ir interno" in frontend
    assert "hololang" not in frontend


PUBLIC_HOLOBIT_CONTRACT_DOCS = [
    Path("README.md"),
    Path("docs/instalacion.md"),
    Path("docs/contrato_runtime_holobit.md"),
    Path("docs/matriz_transpiladores.md"),
    Path("docs/targets_policy.md"),
]

FORBIDDEN_NON_PYTHON_HOLOBIT_PROMOTION_PATTERNS = [
    re.compile(
        r"(javascript|rust|wasm|go|cpp|java|asm)[^\n]{0,120}"
        r"(figura como|aparece como|es|tiene)[^\n]{0,40}"
        r"(full|compatibilidad total con holobit sdk|compatibilidad sdk completa)",
        re.IGNORECASE,
    ),
]

PUBLIC_CANONICAL_NAME_DOCS = [
    Path("README.md"),
    Path("docs/README.en.md"),
    Path("docs/config_cli.md"),
    Path("docs/frontend/arquitectura.rst"),
]

FORBIDDEN_PUBLIC_JS_ALIAS_PATTERN = re.compile(r"(?<![\w.-])js(?![\w.-])", re.IGNORECASE)
FORBIDDEN_PUBLIC_ALIAS_PATTERNS = [
    re.compile(r"(?<![\w.+/-])js(?![\w.+/-])", re.IGNORECASE),
    re.compile(r"(?<![\w.+/-])c\+\+(?![\w.+/-])", re.IGNORECASE),
    re.compile(r"(?<![\w.+/-])assembly(?![\w.+/-])", re.IGNORECASE),
    re.compile(r"(?<![\w.+/-])ensamblador(?![\w.+/-])", re.IGNORECASE),
]
FORBIDDEN_PUBLIC_LEGACY_OPTION_PATTERNS = [
    re.compile(r"(?<![\w-])--a(?![\w-])"),
]


def _normalized_public_line(line: str) -> str:
    return (
        line.replace(".js", "")
        .replace(".mjs", "")
        .replace(".cjs", "")
        .replace(".cpp", "")
        .replace(".wasm", "")
        .replace("Node.js", "Node")
    )


def test_docs_publicas_no_promocionan_backends_no_python_a_sdk_full():
    for path in PUBLIC_HOLOBIT_CONTRACT_DOCS:
        contenido = path.read_text(encoding="utf-8")
        lowered = contenido.lower()
        for pattern in FORBIDDEN_NON_PYTHON_HOLOBIT_PROMOTION_PATTERNS:
            assert not pattern.search(contenido), (
                f"La documentación pública {path} no debe promocionar backends no Python a SDK full"
            )
        if path in {Path("docs/contrato_runtime_holobit.md"), Path("docs/matriz_transpiladores.md"), Path("docs/targets_policy.md")}:
            assert "python" in lowered and "full" in lowered
            assert "partial" in lowered


def test_docs_publicas_exigen_error_explicito_para_backends_partial_en_holobit():
    contenido = Path("docs/contrato_runtime_holobit.md").read_text(encoding="utf-8").lower()
    assert "no-op silencioso" in contenido
    assert "error explícito" in contenido or "fallos explícitos" in contenido


def test_docs_contractuales_no_mezclan_helpers_python_con_contrato_holobit():
    contenido = " ".join(
        Path("docs/contrato_runtime_holobit.md")
        .read_text(encoding="utf-8")
        .lower()
        .split()
    )
    assert "escalar" in contenido
    assert "mover" in contenido
    assert "solo python" in contenido or "runtime python" in contenido
    assert (
        "no forman parte del contrato" in contenido
        or "no forman parte de esta matriz" in contenido
        or "fuera de alcance del contrato" in contenido
    )


def test_docs_frontend_marcan_escalar_y_mover_como_helpers_python():
    for path in (Path("docs/frontend/referencia.rst"), Path("docs/frontend/caracteristicas.rst")):
        contenido = " ".join(path.read_text(encoding="utf-8").lower().split())
        assert "escalar" in contenido
        assert "mover" in contenido
        assert "runtime python" in contenido
        assert "no forman parte del contrato" in contenido


def test_docs_publicas_clave_no_reintroducen_js_como_nombre_canonico():
    for path in PUBLIC_CANONICAL_NAME_DOCS:
        contenido = path.read_text(encoding="utf-8")
        assert not FORBIDDEN_PUBLIC_JS_ALIAS_PATTERN.search(contenido), (
            f"La documentación pública {path} no debe usar 'js' como nombre canónico público"
        )


def test_scope_publico_vigilado_no_reintroduce_aliases_legacy_ni_flags_obsoletos():
    for path in PUBLIC_TEXT_PATHS:
        assert path.exists(), f"La ruta pública vigilada debe existir: {path}"
        for line_no, raw_line in enumerate(
            path.read_text(encoding="utf-8", errors="ignore").splitlines(),
            start=1,
        ):
            line = _normalized_public_line(raw_line)
            for pattern in FORBIDDEN_PUBLIC_ALIAS_PATTERNS:
                assert not pattern.search(line), (
                    f"La ruta pública {path}:{line_no} reintroduce un alias legacy fuera de política: {raw_line.strip()}"
                )
            for pattern in FORBIDDEN_PUBLIC_LEGACY_OPTION_PATTERNS:
                assert not pattern.search(line), (
                    f"La ruta pública {path}:{line_no} reintroduce una flag de CLI obsoleta: {raw_line.strip()}"
                )


def test_glosario_historico_de_aliases_existe_y_esta_marcado_como_no_normativo():
    path = Path("docs/historico/targets_aliases_legacy.md")
    contenido = path.read_text(encoding="utf-8").lower()
    assert "histórico" in contenido or "historico" in contenido
    assert "sin vigencia normativa" in contenido
    assert "js" in contenido
    assert "c++" in contenido


def test_readme_y_guias_publicas_no_presentan_hololang_como_documentacion_normal():
    for path in (
        Path("README.md"),
        Path("docs/README.en.md"),
        Path("docs/lenguajes_soportados.rst"),
        Path("docs/proposals/plan_nuevas_funcionalidades.md"),
    ):
        contenido = path.read_text(encoding="utf-8").lower()
        assert "hololang" not in contenido, f"La guía pública {path} no debe mencionar Hololang como parte del recorrido normal"

    experimental = Path("docs/experimental/hololang_pipeline.md").read_text(encoding="utf-8").lower()
    assert "experimental" in experimental
    assert "fuera de política" in experimental or "fuera de la navegación pública" in experimental

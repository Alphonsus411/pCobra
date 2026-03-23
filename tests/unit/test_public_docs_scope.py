import re
from pathlib import Path

from scripts.ci.validate_targets import validate_public_documentation_alignment
from scripts.generate_target_policy_docs import generate as generate_target_policy_docs
from scripts.targets_policy_common import PUBLIC_TEXT_PATHS
from pcobra.cobra.transpilers.reverse import REVERSE_SCOPE_LANGUAGES
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

EXPERIMENTAL_DOCS = [
    Path("docs/experimental/README.md"),
]

REMOVED_PUBLIC_DOCS = [
    Path("docs") / f"{'ll' 'vm'}_prototype.md",
    Path("docs") / ("construcciones_" + f"{'ll' 'vm'}_ir.md"),
    Path("docs") / f"soporte_{'la' 'tex'}.md",
    Path("docs/limitaciones_wasm_reverse.md"),
    Path("docs/frontend") / f"{'holo' 'lang'}.rst",
]


def test_experimental_docs_estan_segregados_y_marcados():
    for path in EXPERIMENTAL_DOCS:
        assert path.exists(), f"Falta documento experimental: {path}"
        contenido = path.read_text(encoding="utf-8").lower()
        assert "experimental" in contenido
        assert "árbol principal" in contenido or "oficial" in contenido


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
    assert "archive/retired_targets/" in policy
    assert "orígenes reverse" in policy
    assert "recorrido normativo principal" in policy or "árbol principal" in policy

    lenguajes = Path("docs/lenguajes.rst").read_text(encoding="utf-8").lower()
    assert "no targets de salida" in lenguajes

    frontend = Path("docs/frontend/index.rst").read_text(encoding="utf-8").lower()
    assert "artefactos internos" in frontend or "internos" in frontend
    assert "archive/retired_targets/" not in frontend


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
        r"\b(figura como|aparece como|es|tiene)\b[^\n]{0,40}"
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




def test_validador_documental_ci_no_detecta_divergencias_publicas():
    assert not validate_public_documentation_alignment(
        tuple(OFFICIAL_TARGETS), tuple(REVERSE_SCOPE_LANGUAGES)
    )


def test_docs_publicas_enumeran_exactamente_los_8_backends_oficiales_en_tablas_clave():
    expected = set(OFFICIAL_TARGETS)
    for path in (
        Path("docs/targets_policy.md"),
        Path("docs/matriz_transpiladores.md"),
        Path("docs/contrato_runtime_holobit.md"),
    ):
        rows = {line.split("|")[1].strip().strip("`") for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("| `")}
        assert rows == expected, f"{path} debe documentar exactamente los 8 backends oficiales"


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


def test_el_historial_de_aliases_sale_del_arbol_documental_publico():
    assert not Path("docs/historico/targets_aliases_legacy.md").exists()

    path = Path("archive/retired_targets/docs/targets_aliases_legacy.md")
    contenido = path.read_text(encoding="utf-8").lower()
    assert "histórico" in contenido or "historico" in contenido
    assert "sin vigencia normativa" in contenido
    assert "js" in contenido
    assert "c++" in contenido


def test_guias_publicas_no_reintroducen_artefactos_retirados_en_recorrido_normal():
    forbidden_terms = (
        "holo" "lang",
        "ll" "vm",
        "la" "tex",
        "reverse" "-wasm",
    )
    for path in (
        Path("README.md"),
        Path("docs/README.en.md"),
        Path("docs/especificacion_tecnica.md"),
        Path("docs/lenguajes_soportados.rst"),
        Path("docs/proposals/plan_nuevas_funcionalidades.md"),
    ):
        contenido = path.read_text(encoding="utf-8").lower()
        for termino in forbidden_terms:
            assert termino not in contenido, (
                f"La guía pública {path} no debe mencionar artefactos retirados del recorrido normal: {termino}"
            )


def test_snippets_generados_siguen_sincronizados_con_la_fuente_canonica():
    watched = [
        Path("README.md"),
        Path("docs/README.en.md"),
        Path("docs/_generated/target_policy_summary.rst"),
        Path("docs/_generated/official_targets_table.rst"),
        Path("docs/_generated/runtime_capability_matrix.rst"),
        Path("docs/_generated/reverse_scope_table.rst"),
        Path("docs/_generated/cli_backend_examples.rst"),
    ]
    before = {path: path.read_text(encoding="utf-8") for path in watched}
    generate_target_policy_docs()
    after = {path: path.read_text(encoding="utf-8") for path in watched}
    assert before == after

# Inventario de deuda de formato Black

Estado: deuda heredada visible; no autoriza reformateos.

Referencia: `master` en `746a009d911283a45aec5687f8ea97e65f2ec226`.
Herramienta: Black 26.5.1, con `line-length = 88` y objetivo Python 3.11.

La política incremental de CI comprueba los archivos Python añadidos o
modificados. Este inventario preserva la deuda histórica para tratarla por las
fases FMT-003 a FMT-007 del roadmap, sin convertirla en una exclusión silenciosa.

## Fuentes y utilidades no protegidas

- `audit_evidence/phase1/classes-backends.py`
- `scripts/lint_policy_drift.py`
- `src/pcobra/cobra/build/__init__.py`
- `src/pcobra/cobra/build/backend_pipeline.py`
- `src/pcobra/cobra/build/orchestrator.py`
- `src/pcobra/cobra/cli/commands/profile_cmd.py`
- `src/pcobra/cobra/core/resolucion_instancias.py`
- `src/pcobra/cobra/transpilers/transpiler/python_nodes/metodo.py`
- `src/pcobra/core/interpreter.py`

## Pruebas ordinarias

- `tests/cli/test_repl_cobra_lexer_contract.py`
- `tests/integration/test_core_audit_phase1.py`
- `tests/integration/test_usar_core_contract_full.py`
- `tests/test_transpilers.py`
- `tests/test_vscode_textmate_enum_contract.py`
- `tests/unit/test_desde_usar_auditoria.py`
- `tests/unit/test_grammar_coverage.py`
- `tests/unit/test_holobit_graficar_contract.py`
- `tests/unit/test_interpreter_constructor_poo006.py`
- `tests/unit/test_interpreter_scope_contract.py`
- `tests/unit/test_javascript_poo009.py`
- `tests/unit/test_parser_metodos_sin_fin.py`
- `tests/unit/test_project_root_usar_resolution.py`
- `tests/unit/test_resolucion_instancias_poo004.py`
- `tests/unit/test_semantico_atributos_poo016.py`
- `tests/unit/test_usar_symbol_policy.py`

## Protegidos: requieren fase y autorización específicas

- `src/pcobra/cobra/core/lexer.py`
- `src/pcobra/cobra/core/parser.py`

## Snapshots byte-a-byte: requieren evaluación contractual

- `tests/data/expected_examples/async_await.py`
- `tests/data/expected_examples/ejemplo.py`
- `tests/data/expected_examples/factorial_recursivo.py`
- `tests/data/expected_examples/hola.py`
- `tests/data/expected_examples/suma.py`
- `tests/data/expected_examples/suma_matrices.py`

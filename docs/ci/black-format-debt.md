# Inventario de deuda de formato Black

Estado: cierre FMT-007; deuda heredada visible y delimitada. No autoriza
reformateos automáticos de contratos, snapshots ni evidencia.

Referencia inicial: `master` en `746a009d911283a45aec5687f8ea97e65f2ec226`.
Cierre calculado sobre la cadena FMT que termina en
`cb5a6322c6b769926fa9b9b0dc28a6b6f8d9dba8`.
Herramienta: Black 26.5.1, con `line-length = 88` y objetivo Python 3.11.

La política incremental de CI comprueba los archivos Python añadidos o
modificados. Por tanto, no permite añadir deuda nueva y mantiene esta deuda
histórica visible hasta que cada contrato reciba una decisión específica.

## Evidencia: preservada

- `audit_evidence/phase1/classes-backends.py`

Es una evidencia reproducible de auditoría; no se debe mezclar su formateo con
cambios funcionales ni de contratos.

## Pruebas contractuales: preservadas

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

Estas pruebas cubren Lexer/Parser, POO, intérprete, transpiladores, `usar`,
diagnósticos y salidas textuales. Su formato sólo puede cambiarse con una PR
exclusiva y una decisión contractual explícita.

## Lexer y Parser: verificados sin deuda

- `src/pcobra/cobra/core/lexer.py`
- `src/pcobra/cobra/core/parser.py`

FMT-006 verificó que Black no propone cambios en estas rutas.

## Snapshots byte-a-byte: preservados

- `tests/data/expected_examples/async_await.py`
- `tests/data/expected_examples/ejemplo.py`
- `tests/data/expected_examples/factorial_recursivo.py`
- `tests/data/expected_examples/hola.py`
- `tests/data/expected_examples/suma.py`
- `tests/data/expected_examples/suma_matrices.py`

FMT-005 verificó sus consumidores: 44 pruebas correctas. Las exclusiones de
Black protegen los snapshots frente a reescrituras accidentales.

## Resultado del cierre

No se restaura `black --check .` global: todavía detectaría los 17 archivos
enumerados arriba. La comprobación incremental se mantiene porque evita deuda
nueva sin desactivar ni ocultar la existente.

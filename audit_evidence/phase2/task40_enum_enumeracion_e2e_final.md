# TASK 40 — Auditoría E2E final de `enum` / `enumeracion`

## Metadatos y alcance

- Repositorio: `Alphonsus411/pCobra`.
- Rama observada durante la auditoría: `work`.
- SHA base auditado: `33823f8efe4ad9593c9ecccd2ef33725b2eb91ea`.
- Fecha de auditoría: 2026-09-19 (UTC).
- Naturaleza: verificación forense de extremo a extremo.
- Alcance: registro de reservadas, lexer, parser, AST, backends Python,
  JavaScript y Rust, REPL/Pygments, VS Code, SPEC, EBNF, libro y tests.
- Cambios de comportamiento: ninguno.
- Artefactos creados: únicamente este informe.

## Conclusión ejecutiva

**Clasificación: B — COMPLETO CON DEUDA NO BLOQUEANTE.**

El contrato de `enum` / `enumeracion` está alineado y es funcionalmente
coherente en todas las superficies auditadas. `enumeracion` es la forma
canónica, `enum` es un alias de compatibilidad y ambas grafías se normalizan a
`TipoToken.ENUMERACION`, recorren `declaracion_enum()` y producen el mismo
`NodoEnum`. No se encontró una contradicción funcional reproducible.

La clasificación no es A por deuda de automatización: no hay test comprometido
para el enum JavaScript vacío ni validaciones con `node --check` o `rustc`; el
Python normal no usa `compile(...)` en su test; y los filtros recomendados
`-k enum` en los módulos generales de los backends seleccionan cero pruebas.
Estas carencias no afectan al comportamiento observado, que sí fue validado
manualmente durante esta auditoría.

## Contrato verificado

```text
enumeracion:
    ("enumeracion"|"enum")
    IDENTIFICADOR
    ":"
    [IDENTIFICADOR ("," IDENTIFICADOR)* [","]]
    "fin"
```

Se reprodujeron como válidos un enum vacío, uno con un miembro, varios miembros
separados por coma y una coma final. Se reprodujo como inválida la adyacencia de
miembros sin coma con las dos grafías.

## Matriz de trazabilidad de superficies

| # | Superficie | Estado | Evidencia de implementación | Evidencia de test/sonda |
| --- | --- | --- | --- | --- |
| 1 | `PALABRAS_RESERVADAS` | Correcto | `src/pcobra/cobra/core/utils.py:33-97` contiene `enum` y `enumeracion`. | `tests/unit/test_reserved_identifiers.py:67-73`. |
| 2 | Lexer core | Correcto | `src/pcobra/cobra/core/lexer.py:25,192-250`; una regla `\b(enum\|enumeracion)\b` produce `ENUMERACION`. | `tests/test_lexer_parser_contract.py:65-90`; sonda E2E A/B. |
| 3 | Parser | Correcto | `src/pcobra/cobra/core/parser.py:86-95,1379-1413`; un solo factory y una sola ruta semántica. | `tests/unit/test_parser.py:90-140`; `tests/unit/test_enum.py:13-35`. |
| 4 | AST | Correcto | `src/pcobra/core/ast_nodes.py:279-284`; único `NodoEnum(nombre, miembros)`. | Sondas A/B producen campos idénticos. |
| 5 | Python | Correcto | `src/pcobra/cobra/transpilers/transpiler/python_nodes/enum.py:4-13`; miembros numerados y `pass` para vacío. | `tests/unit/test_enum.py:38-50`; `compile(...)` E2E normal/vacío. |
| 6 | JavaScript | Correcto | `src/pcobra/cobra/transpilers/transpiler/js_nodes/enum.py:1-4`; vacío genera `{}`. | `tests/unit/test_enum.py:53-57`; `node --check` E2E normal/vacío. |
| 7 | Rust | Correcto | `rust_nodes/enum.py:1-7`; scopes y acceso en `to_rust.py:217-266,321-327`. | `tests/unit/test_enum.py:60-374`; cinco compilaciones mínimas con `rustc`. |
| 8 | REPL/Pygments | Correcto | `src/pcobra/cobra/cli/repl/cobra_lexer.py:27-75`; una regla para ambas grafías. | `tests/cli/test_repl_cobra_lexer_contract.py:52-63`. |
| 9 | VS Code | Correcto | `extensions/vscode/syntaxes/cobra.tmLanguage.json:19-28`. | `tests/test_vscode_textmate_enum_contract.py:15-26`. |
| 10 | SPEC | Correcto | `docs/SPEC_COBRA.md:32-35,74-82,147-152`. | Revisión estática y sincronización documental. |
| 11 | EBNF | Correcto | `docs/gramatica.ebnf:27-33`. | Revisión estática y suite general de grammar coverage. |
| 12 | Libro/documentación | Correcto | `docs/LIBRO_PROGRAMACION_COBRA.md:116-134,206-214`. | `scripts/sync_libro_programacion.py --check`. |
| 13 | Tests | Completo con deuda menor | Suite dedicada en `tests/unit/test_enum.py`. | Resultados exactos documentados abajo. |

## 1. Registro de palabras reservadas

`PALABRAS_RESERVADAS` contiene explícitamente `enum` y `enumeracion` en
`src/pcobra/cobra/core/utils.py:93-94`. Ambas entradas representan el contrato
público real: no son identificadores legales y corresponden a dos grafías de
la misma declaración. No se modificó el registro.

## 2. Lexer core

`TipoToken` define un único miembro `ENUMERACION` en
`src/pcobra/cobra/core/lexer.py:25`. La lista ordenada de especificaciones
incluye exactamente una regla relevante en la línea 218:

```python
(TipoToken.ENUMERACION, re.compile(r"\b(enum|enumeracion)\b"))
```

La regla aparece dentro del bloque de palabras clave y antes del identificador
genérico. No hay una segunda regla enum que pueda eclipsarla. Las sondas de A y
B confirmaron que el primer token de las dos fuentes tiene
`tipo.name == "ENUMERACION"`.

## 3. Parser

La tabla `_factories` asocia solamente `TipoToken.ENUMERACION` con
`declaracion_enum` (`parser.py:142`). Como el lexer normaliza ambas grafías,
ninguna necesita un handler separado.

`declaracion_enum()` (`parser.py:1379-1413`):

1. consume el token compartido mediante `_consumir_alias_palabra_clave`;
2. exige un nombre identificador;
3. exige `:`;
4. permite encontrar `fin` inmediatamente, por lo que el enum puede estar vacío;
5. consume miembros identificadores;
6. después de cada miembro exige `,` o `fin`;
7. permite que una coma sea seguida por `fin`;
8. exige y consume `fin`;
9. devuelve siempre `NodoEnum(nombre, miembros)`.

Las fuentes sin coma fueron rechazadas con:

```text
Se esperaba ',' o 'fin' después del miembro de enumeración
```

## 4. AST

Hay una sola clase `NodoEnum` en `src/pcobra/core/ast_nodes.py:280-284`, con
campos `nombre: str` y `miembros: List[str]`. No existe una variante AST para el
alias. Las sondas canónica y alias produjeron el mismo tipo, nombre y lista de
miembros.

## 5. Backend Python

El visitante emite una clase, asigna índices consecutivos desde cero y escribe
`pass` cuando `miembros` está vacío. Los resultados relevantes fueron:

```python
class Color:
    ROJO = 0
    VERDE = 1
```

```python
class Vacia:
    pass
```

Los dos códigos completos generados superaron
`compile(codigo, "<enum>", "exec")`. El test comprometido valida texto para el
caso normal y texto más `compile(...)` para el vacío
(`tests/unit/test_enum.py:38-50`).

## 6. Backend JavaScript

El visitante construye un objeto literal con índices consecutivos. Se observó:

```javascript
const Color = {ROJO: 0, VERDE: 1};
const Vacia = {};
```

Los dos módulos completos superaron `node --check` con Node v20.20.2. El caso
normal tiene test textual directo (`tests/unit/test_enum.py:53-57`); el vacío
sólo quedó cubierto por la sonda E2E de esta auditoría.

## 7. Backend Rust

### Declaraciones y acceso

`rust_nodes/enum.py:1-7` genera una declaración Rust única para cualquier
`NodoEnum`; una lista vacía produce un cuerpo vacío válido. Las fuentes canónica
y alias generan el mismo lowering.

`TranspiladorRust.obtener_valor()` (`to_rust.py:250-266`) emite `::` sólo si el
objeto es un `NodoIdentificador` visible en `_enum_names`; en otro caso mantiene
`.`. Se verificó:

```text
Color.ROJO   -> Color::ROJO
objeto.campo -> objeto.campo
```

### Scopes

`_enum_scope()` (`to_rust.py:236-248`) une los enums directos de un bloque con
los heredados y restaura el conjunto anterior en `finally`. `transpilar()`
reinicializa `_enum_names` para cada generación (`to_rust.py:321-327`).

El helper se usa en:

- funciones: `rust_nodes/funcion.py:31-41`;
- métodos: `rust_nodes/metodo.py:6-12`;
- `mientras`: `rust_nodes/bucle_mientras.py:4-10`;
- ramas `si/sino`: `rust_nodes/condicional.py:2-18`;
- `try/catch`: `rust_nodes/try_catch.py:4-24`;
- casos y default de switch: `rust_nodes/switch.py:7-24`;
- `with/con`: `to_rust.py:143-152`.

La suite dedicada cubre funciones hermanas, métodos hermanos, herencia de enum
exterior, combinación global/local, ausencia de fuga entre generaciones,
`mientras`, `si/sino`, `try/catch`, `switch` y `with/con`
(`tests/unit/test_enum.py:110-374`).

### `rustc`

Con rustc 1.87.0 compilaron fragmentos mínimos para enum normal, enum vacío,
`Color::ROJO`, enum local dentro de función y enum local dentro de método. Los
únicos mensajes fueron advertencias esperables por código no usado.

## 8. REPL / Pygments

`TOKEN_REGEX_MAP` contiene una sola regla
`r"\b(enum|enumeracion)\b"` asociada a `TipoToken.ENUMERACION` y `Keyword`
(`cobra_lexer.py:51`). El test directo verifica ambas grafías y usa
`enumerador` como control negativo para impedir coincidencias parciales.

## 9. VS Code

La gramática TextMate incluye `enum|enumeracion` dentro de la misma regla
`keyword.control.cobra` (`cobra.tmLanguage.json:27`). El test carga el JSON y
comprueba con `re.fullmatch` que las dos grafías coincidan con al menos un
patrón de keywords.

## 10. SPEC

La producción de `docs/SPEC_COBRA.md:35` coincide exactamente con el contrato.
Las líneas 147-152 declaran a `enumeracion` canónica y recomendada, mantienen
`enum` como alias de compatibilidad no deprecado y afirman que ambas producen
la misma construcción. No se documentan miembros adyacentes sin coma.

## 11. EBNF

`docs/gramatica.ebnf:32` contiene:

```text
enumeracion: ("enumeracion"|"enum") IDENTIFICADOR ":" [IDENTIFICADOR ("," IDENTIFICADOR)* [","]] "fin"
```

La producción permite vacío y coma final, obliga la coma entre miembros y
acepta el alias.

## 12. Libro y documentación pública

Clasificación de las referencias encontradas:

| Referencia | Clasificación | Motivo |
| --- | --- | --- |
| `docs/LIBRO_PROGRAMACION_COBRA.md:128` | Correcta | Declara `enumeracion` canónica y `enum` alias de compatibilidad. |
| `docs/LIBRO_PROGRAMACION_COBRA.md:206-214` | Correcta | Incluye `enumeracion` como sentencia. |
| `docs/SPEC_COBRA.md:35,78,147-152` | Correcta | Gramática y política de alias coinciden con el core. |
| `docs/gramatica.ebnf:32` | Correcta | Producción exacta. |
| `docs/api/...enum...` | Puramente técnica | Son nombres de módulos internos, no sintaxis fuente. |
| `audit_evidence/phase2/task34_enum_enumeracion_forensics.md` | Puramente histórica | Describe el estado anterior a las reparaciones 38–38E. |

No se hallaron referencias públicas vigentes obsoletas o ambiguas que
contradigan el contrato actual.

## 13. Matriz de tests

| Caso mínimo | Tipo de cobertura | Localización |
| --- | --- | --- |
| Lexer canónico | Directa | `tests/test_lexer_parser_contract.py:78-79`. |
| Lexer alias | Directa | `tests/test_lexer_parser_contract.py:78-79`. |
| Parser canónico | Directa | `tests/unit/test_enum.py:13-18`. |
| Parser alias | Directa | `tests/unit/test_enum.py:21-26`. |
| Vacío | Directa | `tests/unit/test_parser.py:103-112`. |
| Un miembro | Directa | `tests/unit/test_parser.py:103-112`. |
| Varios miembros | Directa | `tests/unit/test_parser.py:90-112`. |
| Coma final | Directa | `tests/unit/test_parser.py:103-112`. |
| Rechazo sin coma | Directa, ambas grafías | `tests/unit/test_parser.py:118-126`. |
| Python normal | Directa textual | `tests/unit/test_enum.py:38-42`. |
| Python normal `compile` | Sonda E2E | No hay test comprometido. |
| Python vacío | Directa + `compile` | `tests/unit/test_enum.py:45-50`. |
| JavaScript normal | Directa textual | `tests/unit/test_enum.py:53-57`. |
| JavaScript vacío | Sonda E2E | No hay test comprometido. |
| Rust normal | Directa textual | `tests/unit/test_enum.py:60-64,73-84`. |
| Rust vacío | Directa textual | `tests/unit/test_enum.py:67-70,87-91`. |
| Rust acceso `::` | Directa | `tests/unit/test_enum.py:94-107`. |
| Rust atributo `.` | Directa | `tests/unit/test_enum.py:261-263`. |
| Rust scopes | Directa amplia | `tests/unit/test_enum.py:110-374`. |
| Tooling REPL | Directa | `tests/cli/test_repl_cobra_lexer_contract.py:52-63`. |
| Tooling VS Code | Directa | `tests/test_vscode_textmate_enum_contract.py:15-26`. |
| Grammar coverage | Indirecta/general | `tests/unit/test_grammar_coverage.py`. |
| Docs sync | Directa/general | `scripts/sync_libro_programacion.py --check`. |

## Pruebas E2E A–H

| Caso | Resultado observado |
| --- | --- |
| A. Canónico | Primer token `ENUMERACION`; `NodoEnum("Color", ["ROJO", "VERDE"])`; Python, JS y Rust válidos. |
| B. Alias | Primer token `ENUMERACION`; mismo tipo y contenido AST que A. |
| C. Vacío | `NodoEnum("Vacia", [])`; Python con `pass`, JS `{}`, Rust `enum Vacia {}`. |
| D. Coma final | Mismo nombre y miembros que A. |
| E. Sin coma | `ParserError` para canónico y alias. |
| F. Variante Rust | La salida contiene `Color::ROJO`. |
| G. Atributo ordinario | La salida contiene `objeto.campo`. |
| H. Scope Rust | Pasan funciones/métodos hermanos, ramas, bloques y herencia exterior. |

## Comandos y resultados

### Suites recomendadas

| Comando | Resultado |
| --- | --- |
| `pytest -q tests/unit/test_enum.py` | 31 passed. |
| `pytest -q tests/unit/test_parser.py -k enum` | 8 passed, 2 deselected. |
| `pytest -q tests/test_lexer_parser_contract.py` | 5 passed. |
| `pytest -q tests/unit/test_parser.py::test_parser_advertencia_alias_enum` | 1 passed. |
| `pytest -q tests/unit/test_grammar_coverage.py` | 5 passed. |
| `pytest -q tests/unit/test_to_python.py -k enum` | 0 selected, 30 deselected, exit 5. No se cuenta como passed. |
| `pytest -q tests/unit/test_to_js.py -k enum` | 0 selected, 19 deselected, exit 5. No se cuenta como passed. |
| `pytest -q tests/unit/test_to_rust.py -k enum` | 0 selected, 20 deselected, exit 5. No se cuenta como passed. |
| `python scripts/sync_libro_programacion.py --check` | `Sin drift documental.` |
| `git diff --check` | Exit 0. |

### Tooling y reservadas

| Comando | Resultado |
| --- | --- |
| `pytest -q tests/cli/test_repl_cobra_lexer_contract.py -k enum` | 3 passed, 12 deselected. |
| `pytest -q tests/test_vscode_textmate_enum_contract.py` | 1 passed. |
| `pytest -q tests/unit/test_reserved_identifiers.py -k enum` | 2 passed, 10 deselected. |

### Validación de sintaxis destino

- Python: `compile(..., "<enum>", "exec")` pasó para normal y vacío.
- JavaScript: `node --check` pasó para normal y vacío con Node v20.20.2.
- Rust: `rustc --edition 2021` pasó para normal, vacío, acceso de variante,
  enum local en función y enum local en método con rustc 1.87.0.
- Los archivos de sonda se crearon bajo `/tmp` y se eliminaron.

El primer intento del harness E2E se ejecutó sin `PYTHONPATH=src` y falló con
`ModuleNotFoundError: No module named 'pcobra'`. Se repitió correctamente con
`PYTHONPATH=src`; el fallo inicial fue de configuración de la sonda, no del
repositorio.

## Hallazgos

### Contradicciones funcionales

Ninguna. No existe una entrada mínima que demuestre divergencia entre lexer,
parser, AST, backends, tooling y documentación para el contrato auditado.

### Deuda 1 — JavaScript vacío sin test directo

- Superficie: tests/backend JavaScript.
- Archivo: `tests/unit/test_enum.py`.
- Símbolo relacionado: `test_transpilador_js_enum`.
- Entrada mínima: `enumeracion Vacia: fin`.
- Resultado actual: genera `const Vacia = {};` y pasa `node --check`.
- Resultado esperado: prueba comprometida específica.
- Gravedad: baja.
- Microtarea: añadir sólo el test, sin cambiar backend o sintaxis.

### Deuda 2 — Validadores destino no automatizados completamente

- Superficie: tests Python normal y Rust.
- Archivo: `tests/unit/test_enum.py`.
- Entrada mínima: enum normal/vacío y `Color.ROJO`.
- Resultado actual: comparación textual correcta; validación manual correcta.
- Resultado esperado: smoke tests opcionales con `compile`, Node y rustc.
- Gravedad: baja.
- Microtarea: reforzar tests, sin tocar implementación.

### Deuda 3 — Filtros recomendados seleccionan cero pruebas

- Superficie: organización de tests.
- Archivos: `tests/unit/test_to_python.py`, `test_to_js.py`, `test_to_rust.py`.
- Resultado actual: los tres `-k enum` terminan con exit 5; la suite real está
  en `tests/unit/test_enum.py`.
- Resultado esperado: documentar la ubicación o reorganizar mínimamente tests.
- Gravedad: informativa/baja.

## Revisión Git y preservación del core

Durante la auditoría original, `git status --short --branch` mostró un árbol
limpio y `git diff --check` terminó con exit 0. También terminó con exit 0:

```bash
git diff --exit-code -- \
  src/pcobra/cobra/core/lexer.py \
  src/pcobra/cobra/core/parser.py
```

La materialización posterior de este informe sólo añade este archivo Markdown;
no modifica Lexer, Parser, AST, backends, tooling, documentación normativa,
tests, workflows ni dependencias.

## Recomendación

No se requiere corregir la implementación. Para elevar la clasificación a A,
realizar una microtarea exclusivamente de tests que añada cobertura directa de
JavaScript vacío, `compile(...)` para Python normal, smoke checks opcionales de
Node/rustc y una aserción dedicada a la producción EBNF. Mantener esa tarea
separada de cualquier cambio de sintaxis o backend.

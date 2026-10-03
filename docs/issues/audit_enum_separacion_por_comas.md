# Tarea bloqueada: separación por comas en enumeraciones

## Hallazgo

La regla `enumeracion` de `docs/gramatica.ebnf` exige una coma entre miembros.
Sin embargo, el `ClassicParser` actual acepta declaraciones como
`enumeracion Color: ROJO VERDE fin` y produce dos miembros.

Las pruebas de regresión de `tests/unit/test_parser.py` conservan el contrato
esperado: cubren enumeraciones vacías, de un miembro, con varios miembros, con
coma final y el rechazo de miembros consecutivos sin coma. Las dos pruebas de
rechazo permanecen fallidas mientras exista la discrepancia.

## Bloqueo

**Estado: BLOQUEADA a la espera de autorización explícita y específica.**

Corregir el comportamiento requiere modificar
`src/pcobra/cobra/core/parser.py`. `AGENTS.md` prohíbe modificar Lexer o Parser
sin esa autorización; revertir un cambio anterior no la concede. Por ello este
hallazgo no modifica el Parser, no elimina ni debilita las pruebas y no altera
la gramática ni la documentación normativa para ocultar el fallo.

## Criterios de desbloqueo y cierre

1. Obtener autorización explícita y específica para corregir
   `ClassicParser.declaracion_enum`.
2. Hacer la corrección del Parser en una unidad de trabajo independiente.
3. Ejecutar primero las pruebas `test_parser_enum_formas_validas` y
   `test_parser_enum_rechaza_miembros_sin_coma`.
4. Ejecutar después las suites relacionadas del Parser y de enumeraciones.
5. Verificar en el diff final que Lexer no cambió y que el cambio del Parser se
   limita a la autorización concedida.

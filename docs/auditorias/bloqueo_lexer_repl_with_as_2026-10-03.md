# Bloqueo: aliases `with` y `as` en el resaltador del REPL

## Hallazgo

El resaltador del REPL reconoce `with` y `as` como palabras clave, aunque la
sintaxis normativa documentada usa `con` y `como`. Corregir esa divergencia
exige modificar `CobraLexer`, ubicado en
`src/pcobra/cobra/cli/repl/cobra_lexer.py`.

## Bloqueo

`AGENTS.md` prohíbe modificar cualquier Lexer o Parser sin autorización
explícita y específica. La solicitud revisada no concede esa autorización;
por tanto, se conserva el comportamiento existente de `CobraLexer` y no se
incorpora una prueba que exija retirar esos aliases.

## Acción requerida

Antes de retomar el hallazgo, una solicitud debe autorizar explícita y
específicamente el cambio de `CobraLexer`. Hasta entonces, el hallazgo queda
bloqueado y no se modifica la sintaxis, el resaltador ni sus contratos.

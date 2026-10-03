# Bloqueo: aliases `with` y `as` en el resaltador del REPL

## Hallazgo

La reversión propuesta volvería a hacer que el resaltador del REPL reconociera
`with` y `as` como palabras clave, aunque la sintaxis normativa documentada
solo usa `con` y `como`. Esa reversión modificaría `CobraLexer`, ubicado en
`src/pcobra/cobra/cli/repl/cobra_lexer.py`.

## Bloqueo

`AGENTS.md` prohíbe modificar cualquier Lexer o Parser sin autorización
explícita y específica. La solicitud revisada no concede esa autorización;
por tanto, este seguimiento no modifica `CobraLexer` ni altera su prueba de
contrato. En particular, documentar el bloqueo no justifica restaurar aliases
que la sintaxis normativa no define.

## Acción requerida

Antes de realizar cualquier cambio adicional en `CobraLexer`, una solicitud
debe autorizarlo explícita y específicamente. Hasta entonces, el hallazgo
queda documentado sin modificar la sintaxis, el resaltador ni sus contratos.

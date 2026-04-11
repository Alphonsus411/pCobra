# Checklist manual Windows — Unicode en REPL

Objetivo: validar manualmente que el REPL no falla con entradas Unicode mixtas y surrogates inválidos en Windows.

## Contrato de saneamiento en frontera (CLI)

Todo texto que cruce el boundary de entrada de la CLI/REPL **debe** pasar por
`sanitize_input` antes de validación, dispatch o persistencia en historial.

Puntos de referencia del contrato:

- `sanitize_input`: normaliza Unicode y reemplaza surrogates inválidos por `�`.
- `InteractiveCommand._run_repl_loop`: sanea cada línea antes de
  validación/comandos especiales/ejecución.
- `SafeFileHistory.append_string`: sanea antes de persistir en el historial.

Además, en modo debug (y mientras Python no se ejecute con `-O`) existen
aserciones ligeras en frontera para detectar tempranamente cualquier surrogate
aislado remanente.

## Pasos

- [ ] Pegar emoji válido (`🚀`) en modo interactivo.
  - Esperado: se procesa correctamente y persiste en historial sin corrupción.
- [ ] Pegar texto roto con surrogate huérfano (por ejemplo `\ud83d`).
  - Esperado: no crashea; la entrada se sanea con `�`.
- [ ] Ejecutar con `stdin` redirigido que combine texto válido + surrogate inválido.
  - Esperado: ejecución estable, sin excepción por Unicode.

## Criterio de aceptación

- [ ] Cero crashes por errores tipo `surrogates not allowed`.
- [ ] Unicode válido preservado.
- [ ] Sin cambios en parser/AST/interpreter.

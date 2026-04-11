# Checklist manual Windows — Unicode en REPL

Objetivo: validar manualmente que el REPL no falla con entradas Unicode mixtas y surrogates inválidos en Windows.

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

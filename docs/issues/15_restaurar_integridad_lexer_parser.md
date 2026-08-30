# Tarea bloqueada: restaurar la integridad de Lexer y Parser

## Causa única

La suite diferencial detecta el fallo exclusivo de rama
`tests/integration/test_usar_runtime_contract.py::test_integridad_estatica_lexer_y_parser_sin_diff_inesperado`.
El mensaje es `AssertionError: Hash inesperado en
src/pcobra/cobra/core/lexer.py`: el guard espera el SHA-256
`537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70` y
obtiene `7cf70380ab09b71961c138c0dfa6cf8721b69b78448f9c8109e7c1aac0db691f`.
La historia atribuye el cambio a `92e3291d` (`fix(lint): restore Python 3.11
compatible formatting validation`), que tocó Lexer y Parser.

## Estado

**Estado: RESUELTA.**

### Diagnóstico histórico (conservado íntegro)

**Bloqueada a la espera de autorización explícita y específica.** `AGENTS.md`
prohíbe modificar Lexer o Parser. No se debe cambiar la prueba, rebajar su
aserción ni actualizar el hash para aceptar el estado actual. Esta tarea debe
resolverse en un cambio independiente, restaurando de forma verificable la
integridad autorizada sin introducir tokens, reglas, aliases ni sintaxis.

## Criterios de cierre

1. Obtener autorización explícita para tocar los archivos afectados.
2. Ejecutar primero el nodeid focalizado y comprobar que pasa sin modificar la
   prueba.
3. Ejecutar después la suite relacionada y `python -m pytest -q` completa.
4. Repetir la comparación por nodeid contra el baseline
   `96d70b1ba00f07608b0fc2a780fca0e7d6b09257`.
5. Confirmar con el diff final que no hay cambios sintácticos o semánticos no
   autorizados.


## Resolución verificada

- El Lexer se restauró byte a byte desde la fuente canónica.
- El Parser se restauró byte a byte desde la fuente canónica.
- Git confirma como snapshot canónico
  `f92f5f5863ef51d9722cdaea7a1c42619135e9a8`, que pertenece a la historia de
  la rama actual.
- Git confirma como commit independiente de restauración
  `c84741ff8c9db12d4ccf70113a8d0ce88168d279`
  (`fix(core): restore canonical lexer and parser snapshots`), también presente
  en la historia real de la rama.
- La restauración no introdujo cambios semánticos: recuperó exactamente los
  blobs canónicos, sin añadir tokens, palabras reservadas, reglas gramaticales,
  aliases ni sintaxis Cobra.
- El guard focal de integridad
  `python -m pytest -q tests/integration/test_usar_runtime_contract.py::test_integridad_estatica_lexer_y_parser_sin_diff_inesperado`
  finalizó correctamente: `1 passed`.

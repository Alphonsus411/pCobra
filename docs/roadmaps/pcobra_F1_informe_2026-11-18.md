# pCobra — F1: expediente provisional de diagnóstico

**Fecha:** 2026-11-18  
**Baseline fijado:** `68e0465d3793078f2c7763f1e51f7748eb8e9f60`  
**Issues:** [#3873](https://github.com/Alphonsus411/pCobra/issues/3873) · [#3874](https://github.com/Alphonsus411/pCobra/issues/3874)  
**Estado:** F1 **NO CERRADA** por falta de pruebas ejecutadas en el entorno objetivo. Este informe no indica tests superados.

## Evidencia estática contrastada

- `src/pcobra/cobra/cli/commands_v2/test_cmd.py`: `cobra test` usa por defecto todos los targets de `VERIFICATION_EXECUTABLE_TARGETS` y valida políticas de runtime; `--langs` existe como opción oculta, por lo que no se recomienda usarla para sortear el contrato público.
- `src/pcobra/cobra/cli/services/test_service.py`: ejecuta AST con intérprete para obtener salida esperada, transpila y ejecuta cada backend en paralelo, y agrupa tanto errores de ejecución como divergencias bajo `diferencias`, retornando 1.
- `src/pcobra/cobra/cli/commands_v2/run_cmd.py`: `cobra run` sigue un servicio diferente, con backend Python por defecto.
- `src/pcobra/cobra/bindings/runtime_manager.py`: la política `test` exige sandbox para Python y contenedor para JS y Rust. No modificar.
- `scripts/ci/audit_reglas_libro_programacion.py`: audita referencias/secciones y fragmentos de las reglas a nivel Lexer/Parser, pero no ejecuta todos los bloques `.cobra` del libro.
- `docs/LIBRO_PROGRAMACION_COBRA.md`: sus fragmentos con `funcion`, `retornar`, f-strings y parámetros por defecto están presentes, aunque aún no se han reproducido en esta revisión.
- `tests/unit/test_cli_v2_command_contract.py`: existen pruebas de selección y seguridad de backends; `tests/unit/test_audit_reglas_libro_programacion.py` verifica `auditar() == []`. Ninguna de estas observaciones sustituye una ejecución del caso del issue.

## Barreras observadas

- El entorno del asistente no tiene un checkout de pCobra.
- `git ls-remote https://github.com/Alphonsus411/pCobra.git HEAD` no puede resolver `github.com` desde el contenedor.
- La operación de actualización del roadmap de GitHub fue rechazada por el control de autorización. No se ha vuelto a invocar.

## Matriz de ejecución por cubrir

| ID | Caso | Evidencia exigida | Estado |
| --- | --- | --- | --- |
| R01 | `cobra run` sobre función simple | stdout, stderr, exit code | Pendiente |
| R02 | `cobra test` mismo programa | stdout, stderr, exit code | Pendiente |
| R03 | Ejemplo `funcion`/`retornar`/f-string | stdout, stderr, exit code | Pendiente |
| R04 | Función con parámetro por defecto | stdout, stderr, exit code | Pendiente |
| R05 | Función canónica `func`/`retorno`/`fin` | stdout, stderr, exit code | Pendiente |
| R06 | Auditor actual de reglas del libro | stdout, stderr, exit code | Pendiente |

## Colección reproducible de evidencias

El archivo `scripts/diagnostics/pcobra_f1_repro.sh` proporcionado junto a este informe se ejecuta **desde un checkout local de confianza** con Bash, en HEAD exactamente igual al baseline. Genera ejemplos temporales fuera del repositorio y guarda salidas en un directorio externo. **No hace commits, pushes, merges ni edita fuentes**. No fuerza un resultado verde cuando falten dependencias: registra el error real.

```bash
bash scripts/diagnostics/pcobra_f1_repro.sh /ruta/a/pCobra /ruta/externa/evidencias
```

**Notas:** Se necesita un entorno donde `cobra` esté instalado. El script no instala dependencias ni elude políticas de sandbox. Puede existir requisito de `SQLITE_DB_KEY` propio de la CLI: no pegues secretos en esta conversación. Los fixtures del issue original no están adjuntos, por lo que los ejemplos generados son *probes equivalentes*, no reproducción byte a byte del programa original.

## Criterio de cierre

F1 solo se cerrará si se obtienen resultados reales, se cotejan con los issues y se clasifican sin confundir errores del lenguaje, de runtime o de infraestructura. Hasta entonces: **0 % formal del roadmap, inspección estática parcial realizada**.

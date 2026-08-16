# Auditoría 3495: modalidad de CodeQL (2026-08-16 UTC)

## Alcance y resultado

Se intentó realizar el cambio administrativo solicitado en
`Alphonsus411/pCobra`, conservando el workflow avanzado
`.github/workflows/codeql.yml` y sin modificar la configuración, las queries,
los fixtures ni el harness de CodeQL. El resultado es **BLOQUEADO**: este
entorno no dispone de una sesión autenticada de GitHub ni de credenciales con
permisos administrativos. Por ello no fue posible abrir la vista autenticada
`Settings > Security > Code security`, comprobar visualmente el estado de
Default setup, desactivarlo ni relanzar manualmente el workflow.

No se presenta como realizada ninguna mutación de la configuración del
repositorio. La consulta REST a
`GET /repos/Alphonsus411/pCobra/code-scanning/default-setup` respondió
`401 Requires authentication`, y `gh auth status` informó que no existe una
sesión iniciada. Conforme a la instrucción de no introducir workarounds, se
detuvo la actuación administrativa sin modificar el workflow ni los recursos
CodeQL protegidos.

## Ejecución remota observada

Durante la comprobación existía una ejecución automática por evento `push`;
no fue lanzada ni relanzada desde este entorno. Se registra porque analiza el
commit disponible y reproduce exactamente el bloqueo de coexistencia:

| Campo | Evidencia |
|---|---|
| URL | <https://github.com/Alphonsus411/pCobra/actions/runs/31937290255> |
| Run ID | `31937290255` |
| Job / URL | `analyze`, ID `95141098691`; <https://github.com/Alphonsus411/pCobra/actions/runs/31937290255/job/95141098691> |
| Evento | `push` |
| Commit analizado | `df361693a94f23ccedc9d59fe3bd97b5713eb2d2` |
| Inicio | `2026-08-16T08:46:05Z` |
| Fin | `2026-08-16T08:51:00Z` |
| Conclusión global | `completed / failure` |

### Resultado de pasos relevantes

| Paso | Resultado |
|---|---|
| `Initialize CodeQL` | `completed / success` |
| `Autobuild` | `completed / success` |
| `Test custom CodeQL queries` | `completed / success` |
| `Perform CodeQL Analysis` | `completed / failure` |

La anotación pública del check para `Perform CodeQL Analysis` dice:

> Code Scanning could not process the submitted SARIF file: CodeQL analyses
> from advanced configurations cannot be processed when the default setup is
> enabled

Por tanto, **no desapareció el rechazo por coexistencia de modalidades**. Esta
evidencia tampoco permite afirmar que Default setup se hubiese desactivado:
faltó la comprobación administrativa autenticada exigida. No se intentó
corregir el fallo mediante cambios en el repositorio.

## Integridad del alcance protegido

Esta auditoría añade únicamente este registro. Permanecen sin cambios:

- `.github/workflows/codeql.yml`;
- `.github/codeql/custom/codeql-config.yml` y las cuatro queries de su sección
  `queries`;
- los fixtures de las queries;
- el harness `Test custom CodeQL queries`;
- Lexer y Parser.

## Acción necesaria para desbloquear

Una persona o automatización con permisos administrativos debe iniciar una
sesión autenticada, desactivar exclusivamente **Default setup** en la vista de
Code scanning, comprobar visualmente que **Advanced setup** continúa activo y
relanzar `CodeQL`. Sólo entonces puede registrarse un run nuevo en el que
`Initialize CodeQL`, los harnesses y `Perform CodeQL Analysis` finalicen
correctamente. Si ese run conserva el mismo mensaje tras la comprobación
visual, deberá documentarse como un nuevo bloqueo sin introducir workarounds.

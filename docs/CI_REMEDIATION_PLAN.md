# Plan de recuperación de CI

> Estado: propuesta técnica. No autoriza cambios en workflows, reglas de rama,
> secretos ni configuración de seguridad sin una decisión explícita del
> mantenedor.

## Objetivo

Restablecer una señal de CI fiable y atribuible al cambio evaluado. Los fallos
históricos, de infraestructura o de configuración no deben ocultar regresiones
funcionales de una PR.

## Evidencia de partida

Las ejecuciones recientes muestran tres bloqueos independientes:

1. **Label PRs by branch:** falla por un esquema inválido en
   `.github/labeler.yml`. La acción espera que cada patrón se asocie a una
   lista de etiquetas.
2. **Lint:** ejecuta `black --check .`, lo que alcanza archivos bajo
   `.git/` creados por el checkout y falla por contenido que no forma parte del
   código versionado.
3. **CodeQL:** el workflow avanzado carga configuración y consultas propias,
   pero el repositorio mantiene activo Code Scanning Default setup. GitHub
   rechaza el SARIF porque no admite ambas modalidades a la vez.

El gate contractual de runtime sí se completa correctamente. La suite general
puede quedar bloqueada antes de ejecutar pruebas por los fallos anteriores.

## Fase 0 — preservar la evidencia

- No reintentar ni enmascarar fallos sin conservar el SHA, workflow, job y
  salida asociada.
- Diferenciar en cada PR: fallo introducido, deuda preexistente y fallo de
  plataforma.
- Mantener las pruebas focales y los gates contractuales bloqueantes.

**Criterio de salida:** inventario reproducible de fallos por SHA.

## Fase 1 — reparar configuraciones deterministas

### 1. Labeler

Corregir `.github/labeler.yml` a la sintaxis de `actions/labeler`:

```yaml
feature/*:
  - feature
bugfix/*:
  - bug
doc/*:
  - documentation
perf/*:
  - performance
  - "priority: low"
```

**Validación:** abrir una PR de prueba con un prefijo cubierto y comprobar que
el job asigna la etiqueta esperada.

### 2. Black

Sustituir el escaneo de directorio completo por archivos Python rastreados por
Git, por ejemplo:

```bash
git ls-files -z -- '*.py' | xargs -0r black --check
```

Si se requieren ficheros generados, declararlos explícitamente y mantenerlos
fuera de `.git/`, entornos virtuales y artefactos de build.

**Validación:** el job deja de inspeccionar `.git/`; un archivo Python
versionado deliberadamente mal formateado sigue provocando fallo.

## Fase 2 — decisión de seguridad CodeQL

El repositorio debe utilizar **una sola modalidad**:

- **Opción recomendada:** conservar el workflow avanzado porque ejecuta queries
  propias. Requiere desactivar Default setup desde la configuración de
  *Code security and analysis*.
- **Alternativa:** conservar Default setup y retirar el workflow avanzado,
  incluidas las queries personalizadas o moviéndolas a otro mecanismo admitido.

Esta fase requiere permisos administrativos sobre la configuración de seguridad
del repositorio y aprobación explícita antes de realizarla.

**Validación:** CodeQL publica un análisis correcto y continúa ejecutando, si se
elige la opción recomendada, las pruebas de queries personalizadas.

## Fase 3 — recuperar la señal completa

Después de Fases 1 y 2:

1. Reejecutar CI sobre un SHA sin cambios funcionales.
2. Ejecutar primero pruebas focales y gates contractuales.
3. Ejecutar matriz Tier 1 y clasificar cada fallo restante por propietario y
   causa.
4. Corregir una sola familia de fallos por PR; no rebajar cobertura, aserciones
   ni umbrales para obtener verde.
5. Revisar reglas de protección de rama solo al final, cuando los checks sean
   estables.

## Orden de ejecución y permisos

| Orden | Acción | Permiso especial |
|---|---|---|
| 1 | Corregir labeler | No |
| 2 | Limitar Black a archivos versionados | No |
| 3 | Elegir y aplicar modalidad CodeQL | Sí: administrador de seguridad |
| 4 | Reejecutar y clasificar CI | No |
| 5 | Cambiar protección de rama, si hiciera falta | Sí: administrador del repositorio |

## Fuera de alcance

- Desactivar checks obligatorios.
- Ocultar errores con `continue-on-error`, `skip`, `xfail` o rebaja de
  cobertura.
- Cambiar secretos, tokens o permisos de workflows sin aprobación.
- Mezclar reparaciones de CI con cambios funcionales de lenguaje.

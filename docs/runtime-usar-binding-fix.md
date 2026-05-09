# Runtime `usar`: corrección de binding en llamadas a funciones públicas

## 1) Síntoma observado en REPL

En sesiones REPL se observaba el fallo:

- `Función 'es_finito' no implementada`

Escenario típico:

```cobra
usar "numero"
imprimir(es_finito(10))
```

Aunque `es_finito` estaba exportada por el módulo cargado con `usar`, la ejecución podía caer en la rama de función no soportada durante la invocación.

## 2) Causa raíz

La causa raíz histórica fue la resolución estricta de símbolos en contexto durante la llamada:

- `ejecutar_llamada_funcion` priorizaba el descriptor interno de función Cobra (`dict` con `tipo == "funcion"`),
- y no ejecutaba primero callables Python ya saneados/injectados por `usar`.

Como resultado, un símbolo válido en el contexto (por ejemplo `es_finito`) podía no entrar al camino de ejecución correcto si su representación era un callable Python y no un descriptor Cobra.

## 3) Solución aplicada en `ejecutar_llamada_funcion`

La corrección se aplicó en la ruta de ejecución del intérprete para soportar explícitamente callables Python en primer término.

Flujo implementado:

1. Resolver función por nombre en el contexto activo.
2. Si el valor resuelto es `callable(...)`:
   - evaluar y resolver argumentos;
   - validar cada argumento con `self._verificar_valor_contexto(...)`;
   - ejecutar el callable (`funcion(*argumentos_resueltos)`);
   - validar el resultado con `self._verificar_valor_contexto(...)`;
   - capturar y reportar excepciones (logging + propagación controlada).
3. Si no es callable Python, conservar la rama existente para funciones Cobra definidas por usuario (`dict` con `tipo == "funcion"`).

Con esto se mantiene compatibilidad entre funciones definidas en Cobra y funciones públicas importadas por `usar`.

## 4) Flujo de seguridad preservado

La corrección no relaja el modelo de seguridad. Se preserva el encadenado:

1. `usar_loader` resuelve únicamente módulos permitidos por política canónica/allowlist.
2. `sanitizar_exports_publicos` filtra y sanea símbolos exportables.
3. Inyección controlada al contexto del intérprete con validación de colisiones y bloqueo de sobreescritura silenciosa.

La nueva rama callable solo ejecuta símbolos **ya admitidos** en ese flujo, no introduce imports dinámicos adicionales ni bypass de saneamiento.

## 5) Matriz de pruebas

### 5.1 Pruebas manuales (REPL)

| Caso | Entrada | Resultado esperado |
|---|---|---|
| Llamada pública básica | `usar "numero"` + `es_finito(10)` | Retorna `verdadero` / `True` sin error de “no implementada”. |
| Callable alterno | `usar "numero"` + `es_nan(NAN)` | Ejecuta callable saneado y retorna booleano. |
| Colisión de símbolo | definir `es_finito` antes de `usar` | Rechazo por política de colisión; no sobreescribe. |
| Módulo no permitido | `usar "numpy"` (u otro no canónico) | Rechazo por política de `usar_loader`. |

### 5.2 Regresiones automatizadas

Cobertura principal esperada en:

- `tests/unit/test_usar.py`
  - ejecución de callables importados por `usar` (`es_finito`, `es_nan`);
  - semántica plana REPL sin prefijo de módulo;
  - validaciones de colisión y políticas de carga/saneamiento.

## 6) No cambios en Lexer/Parser

Esta corrección **no introduce cambios** en el frente léxico/sintáctico.

Rutas explícitamente no modificadas por este ajuste:

- `src/pcobra/core/lexer.py`
- `src/pcobra/core/parser.py`
- `src/pcobra/core/token_contract.py`

## 7) Referencia de commit/PR

Corrección aplicada en el commit:

- `a3072e9` — *Fix runtime binding for usar-imported callables*

Documentación relacionada posterior:

- `d973c94` — *docs: documentar QA de runtime binding para usar numero*

PR asociado: no se encontró identificador de PR persistido en este repositorio local para ese commit (si existe en remoto, vincularlo aquí como referencia canónica).

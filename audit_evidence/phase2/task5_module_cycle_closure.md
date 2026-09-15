# Fase 2 — tarea 5: cierre de ciclos de módulos

Fecha de reproducción: **2026-09-15 (UTC)**. Directorio de trabajo:
`/workspace/pCobra`. Rama: `work`.

## Resultado ejecutivo

Las cuatro ejecuciones solicitadas terminaron con código de salida `0`. En total
se observaron **190 passed, 0 failed, 0 skipped, 0 xfailed y 0 xpassed** (las
pruebas repetidas entre ejecuciones se contabilizan en cada invocación, no como
casos únicos). Las excepciones de ciclo descritas abajo son resultados esperados
capturados por las propias pruebas; no son fallos de pytest.

## Ejecuciones, en el orden solicitado

| Paso | Comando | passed | failed | skipped | xfailed | xpassed | salida |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `python -m pytest -q tests/unit/test_project_root_usar_resolution.py` | 77 | 0 | 0 | 0 | 0 | 0 |
| 2 | `python -m pytest -q tests/unit/test_project_root_usar_resolution.py::test_interpretador_usar_proyecto_detecta_ciclos_con_rutas_canonicas tests/unit/test_project_root_usar_resolution.py::test_interpretador_usar_proyecto_detecta_ciclo_indirecto tests/unit/test_project_root_usar_resolution.py::test_interpretador_usar_proyecto_detecta_ciclo_directo_en_root_con_mensaje_exacto tests/unit/test_project_root_usar_resolution.py::test_interpretador_usar_proyecto_detecta_ciclo_indirecto_en_root_con_cadena_completa` | 4 | 0 | 0 | 0 | 0 | 0 |
| 3 | `python -m pytest -q tests/unit/test_interpreter_recursion_runtime.py tests/unit/test_interpreter_cycles.py` | 13 | 0 | 0 | 0 | 0 | 0 |
| 4 | `python -m pytest -q tests/unit/test_project_root_usar_resolution.py tests/integration/test_usar_project_modules.py` | 96 | 0 | 0 | 0 | 0 | 0 |

Resúmenes literales de pytest, respectivamente:

```text
77 passed in 1.07s
4 passed in 0.69s
13 passed in 0.67s
96 passed in 0.87s
```

No apareció sección de `short test summary info`, ni registro de pruebas
fallidas, omitidas, `xfail` o `xpass`, en ninguna de las cuatro ejecuciones.

## Excepciones de ciclo verificadas

Los cuatro tests históricos seleccionados comprobaron el tipo `ImportError` y
los siguientes textos completos:

1. Ciclo canónico de dos módulos:
   `Ciclo de módulos detectado en usar: utilidades/a.cobra -> utilidades/b.cobra -> utilidades/a.cobra`.
2. Ciclo indirecto anidado:
   `Ciclo de módulos detectado en usar: utilidades/internas/a.cobra -> utilidades/internas/b.cobra -> utilidades/internas/c.cobra -> utilidades/internas/a.cobra`.
3. Ciclo directo en la raíz:
   `Ciclo de módulos detectado en usar: a.cobra -> a.cobra`.
4. Ciclo indirecto en la raíz:
   `Ciclo de módulos detectado en usar: a.cobra -> b.cobra -> c.cobra -> a.cobra`.

La prueba de recuperación ante un fallo de carga, incluida en los pasos 1 y 4,
también capturó la excepción esperada de tipo `RuntimeError` con texto completo
`fallo sintético de carga`.

## Controles explícitos y limpieza

Además de las suites, se ejecutó una sonda aislada con módulos temporales, AST
de `NodoUsar` y conteo de llamadas a `cargar_ast_modulo`. Se lanzó como
`PYTHONPATH=. python /tmp/task5_module_cycle_probe.py` y terminó con código `0`.
La sonda hizo aserciones tanto sobre `interp._usar_loading_stack` como sobre
`obtener_pila_carga_modulos_cobra_proyecto()` después de cada escenario.
Para reproducirla, guardar este contenido en
`/tmp/task5_module_cycle_probe.py` y ejecutar el comando anterior:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from pcobra.core.ast_nodes import NodoUsar
from pcobra.cobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.usar_loader import obtener_pila_carga_modulos_cobra_proyecto


def run_case(name, graph, initial, expected_exception=None):
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "cobra.toml").write_text("[proyecto]\n", encoding="utf-8")
        main = root / "main.cobra"
        main.write_text("", encoding="utf-8")
        for module in graph:
            (root / f"{module}.cobra").write_text("", encoding="utf-8")
        calls = []

        def fake_load(path, **_kwargs):
            module = Path(path).stem
            calls.append(module)
            return [NodoUsar(child) for child in graph[module]]

        interp = InterpretadorCobra(safe_mode=False, main_file=main)
        caught = None
        with patch("pcobra.core.import_utils.cargar_ast_modulo", fake_load):
            try:
                for module in initial:
                    interp.ejecutar_usar(SimpleNamespace(modulo=module))
            except Exception as exc:
                caught = exc

        if expected_exception is None:
            assert caught is None, repr(caught)
        else:
            assert isinstance(caught, expected_exception), repr(caught)
        assert interp._usar_loading_stack == []
        assert obtener_pila_carga_modulos_cobra_proyecto() == []
        print(name, calls, type(caught).__name__ if caught else None, caught)


run_case("carga_simple", {"a": []}, ["a"])
run_case("reimportacion_aciclica", {"a": []}, ["a", "a"])
run_case("cadena_aciclica", {"a": ["b"], "b": ["c"], "c": []}, ["a"])
run_case("diamante", {"a": ["c"], "b": ["c"], "c": []}, ["a", "b"])
run_case("ciclo_directo", {"a": ["a"]}, ["a"], ImportError)
run_case(
    "ciclo_indirecto",
    {"a": ["b"], "b": ["c"], "c": ["a"]},
    ["a"],
    ImportError,
)
```

| Control | Secuencia de cargas observada | Excepción | `_usar_loading_stack` final | pila compartida final | Confirmación |
|---|---|---|---|---|---|
| carga simple | `['a']` | ninguna | `[]` | `[]` | correcta |
| reimportación acíclica (`a`, `a`) | `['a']` | ninguna | `[]` | `[]` | correcta; la segunda importación usó caché |
| cadena acíclica (`a -> b -> c`) | `['a', 'b', 'c']` | ninguna | `[]` | `[]` | correcta |
| diamante (`a -> c`, `b -> c`) | `['a', 'c', 'b']` | ninguna | `[]` | `[]` | correcta; `c` se cargó una sola vez |
| ciclo directo (`a -> a`) | `['a']` | `ImportError`: `Ciclo de módulos detectado en usar: a.cobra -> a.cobra` | `[]` | `[]` | detectado y limpiado |
| ciclo indirecto (`a -> b -> c -> a`) | `['a', 'b', 'c']` | `ImportError`: `Ciclo de módulos detectado en usar: a.cobra -> b.cobra -> c.cobra -> a.cobra` | `[]` | `[]` | detectado y limpiado |

Por tanto, quedan confirmados explícitamente los controles de **carga simple,
reimportación acíclica, cadena acíclica, diamante, ciclo directo y ciclo
indirecto**. En todos los casos la pila de carga terminó vacía. En particular,
las pruebas históricas también verifican `[]` tras el ciclo canónico, tras los
dos ciclos en la raíz y tras el `RuntimeError` sintético.

## Mecanismo arquitectónico actual

La función `_cargar_exports_modulo_cobra_proyecto` de
`src/pcobra/cobra/usar_loader.py` aplica el siguiente ciclo de vida:

1. Después de resolver y validar la ruta canónica, consulta primero esa ruta en
   `module_cache`. Si ya existe, devuelve sus exports sin volver a cargar ni a
   interpretar el módulo.
2. `loading_stack` contiene únicamente las rutas de los módulos cuya carga está
   en curso. Si la ruta solicitada ya figura en esa pila,
   `formatear_ciclo_modulos_cobra_proyecto` construye la cadena del ciclo y la
   función lanza `ImportError` con dicha cadena.
3. La ruta se incorpora a la pila antes de cargar el AST y antes de iniciar su
   interpretación.
4. La entrada de caché se construye y almacena sólo después de que la
   interpretación termine correctamente y se hayan extraído y construido los
   exports. Una carga fallida, por tanto, no publica un resultado parcial.
5. El bloque `finally` libera los contextos temporales y la memoria local del
   intérprete, y retira la ruta de la pila de carga. Esta limpieza se ejecuta
   tanto después del éxito como después de una excepción.

## Distinción entre estados

- **Módulo cargado correctamente:** tiene una entrada finalizada en la caché,
  creada después de interpretar el AST y construir sus exports.
- **Módulo visitado anteriormente:** es un concepto histórico. Por sí solo no
  representa una carga activa ni demuestra la existencia de un ciclo.
- **Módulo en la pila activa:** su carga todavía no ha terminado y forma parte
  de la cadena de importación que se está evaluando.

Una reimportación acíclica encuentra la entrada finalizada y usa la caché. En
un grafo en diamante, el nodo compartido puede haberse cargado durante una rama
anterior sin continuar activo cuando otra rama lo referencia. Sólo la reentrada
en un módulo que aún pertenece a la cadena activa constituye un ciclo
estructural.

## Revisión histórica de las PR relacionadas

La inspección local de los commits fusionados y de sus metadatos disponibles
permitió comprobar lo siguiente:

- **PR #3571, commit `0f9c7c0f`:** reemplazó las expectativas antiguas del ciclo
  canónico de dos módulos por el mensaje exacto con la cadena completa. Sólo
  modificó `tests/unit/test_project_root_usar_resolution.py`; no cambió el
  contrato de runtime. Redujo el riesgo de aceptar mensajes incompletos o del
  contrato anterior.
- **PR #3572, commit `9975d75e`:** exigió la cadena completa del ciclo indirecto
  anidado. Sólo cambió el mismo archivo de tests; no alteró runtime. Amplió la
  precisión de la cobertura de ciclos indirectos.
- **PR #3573, commit `1a046b00`:** actualizó el ciclo directo en la raíz para
  exigir `a.cobra -> a.cobra`. Sólo modificó tests; no cambió el contrato
  funcional. Eliminó una expectativa negativa antigua sobre la presencia de la
  ruta.
- **PR #3574, commit `733a8b35`:** exigió la cadena completa
  `a.cobra -> b.cobra -> c.cobra -> a.cobra` para el ciclo indirecto en la
  raíz. Sólo modificó tests; no cambió runtime. Cerró el riesgo de validar
  únicamente un prefijo genérico.

Esta revisión se limita a los commits y metadatos de merge disponibles en el
repositorio local. No permite afirmar detalles de conversaciones, revisiones o
checks remotos que no puedan comprobarse allí.

## EXPECTATIVAS OBSOLETAS — CERRADO

El runtime detecta ciclos reales y no produce falsos positivos en
reimportaciones legítimas. Además, limpia el estado temporal después del éxito
y de una excepción, conserva la recursividad legítima verificada por las suites
relacionadas y no necesita cambios adicionales para Task 5.

## Riesgos residuales

### Riesgos del contrato de módulos

La conclusión depende del contrato observado: rutas canónicas como claves,
publicación en caché únicamente tras el éxito y pertenencia a la pila activa
como criterio de ciclo. Las pruebas y la sonda reproducible sustentan ese
comportamiento para carga simple, reimportación, cadenas, diamantes y ciclos
directos e indirectos, además de la limpieza tras una excepción. El riesgo
residual real es una regresión futura que altere alguno de esos invariantes; no
hay en esta evidencia un defecto vigente conocido del contrato. En particular,
los cuatro fallos históricos eran expectativas de tests obsoletas o
insuficientemente precisas, no cuatro defectos actuales del runtime.

### Defectos independientes de CI

El fallo
`tests/unit/test_parser_error_reporting.py::test_error_en_declaracion_para`, con
`AttributeError: IN`, es independiente del contrato de módulos y queda fuera
del alcance de Task 5. Un fallo global ajeno no invalida por sí solo la
conclusión funcional aquí sustentada y debe investigarse sin mezclarlo con este
cierre.

## Siguiente acción recomendada

Cerrar Task 5 y abrir cualquier fallo independiente de CI como una tarea
separada. En concreto, `AttributeError: IN` es candidato de investigación, pero
no debe corregirse como parte de este cambio documental.

## Alcance del cambio

Esta tarea sólo añade la presente evidencia reproducible. No modifica código de
runtime, pruebas, ejemplos, documentación normativa, Lexer ni Parser.

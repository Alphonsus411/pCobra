# Auditoría diferencial de Black y Pylint

## Fuente de los comandos

La revisión de `.github/workflows/lint.yml` y de todos los scripts que ese
workflow invoca encuentra un único formateador Python. El runner selecciona
Python 3.11, instala la versión fijada en `requirements-dev.txt` y ejecuta,
literalmente:

```bash
pip install "$(grep -E '^black==' requirements-dev.txt)"
black --check .
```

En esta revisión la expresión de instalación resuelve a `black==26.5.1`.
Black lee `[tool.black]` de `pyproject.toml`: `line-length = 88`,
`target-version = ["py311"]` y el `extend-exclude` declarado allí. La ruta que
recibe es `.` desde la raíz del repositorio; ninguno de los scripts invocados
llama a Black de nuevo.

El mismo inventario no encuentra **ningún comando de Pylint** en el workflow
ni en sus scripts, ninguna sección de configuración de Pylint y ninguna
dependencia `pylint` fijada. Por ello no existe un comando exacto, conjunto de
rutas ni configuración que se pueda ejecutar o trasladar al baseline sin
inventar un nuevo gate. Añadir arbitrariamente Pylint, su versión o sus
argumentos habría incumplido el requisito de reproducir exactamente CI.

## Ejecución no destructiva y baseline

Se creó el worktree detached `/tmp/pcobra-baseline-pylint` para
`96d70b1ba00f07608b0fc2a780fca0e7d6b09257`. Tanto la comprobación de la rama
como la del baseline usaron el mismo intérprete del entorno aislado,
`/tmp/pcobra-lint-venv/bin/python` (Python 3.11.15), y las mismas dependencias.
La comprobación explícita `python -m pylint --version` devuelve en ambos
árboles `No module named pylint`, coherente con el inventario. No se instaló
una versión no declarada.

Las salidas sin versionar quedaron en `/tmp/pcobra-black-current.log`,
`/tmp/pcobra-black-current-after.log`,
`/tmp/pcobra-pylint-current-execution.log` y
`/tmp/pcobra-pylint-baseline-execution.log`. Los inventarios ordenados están
en `/tmp/pcobra-pylint-{current,baseline}-normalized.txt`.

## Normalización y clasificación

El formato solicitado para un diagnóstico era la tupla ordenable
`ruta|código|símbolo|mensaje|línea-estable`. Como Pylint no está configurado
ni disponible, no hubo salida de diagnósticos que pudiera transformarse a
esas tuplas. Se compararon de forma determinista los dos inventarios vacíos
con `sort -u` y `comm` para no confundir ausencia del gate con una ejecución
verde:

| Clasificación | Cantidad | Interpretación |
|---|---:|---|
| Compartidos | 0 | Pylint no llegó a ejecutarse en ninguno de los árboles. |
| Exclusivos del baseline | 0 | No existe conjunto de diagnósticos baseline. |
| Exclusivos del current | 0 | No existe conjunto de diagnósticos current. |

Estos ceros significan **no evaluado**, no «Pylint verde». Si se incorpora un
gate reproducible en otro cambio, un resultado no verde podrá ser deuda
compartida; el criterio diferencial deberá seguir siendo cero diagnósticos
nuevos atribuibles a la rama.

## Hallazgo de Black y corrección acotada

La primera ejecución exacta de `black --check .`, sin escritura, detectó
`lexer.py`, `parser.py` y `tests/test_codeql_config.py`. Los dos primeros están
protegidos por hashes canónicos y las reglas del repositorio prohíben
modificarlos. Se corrigió únicamente el alcance de `extend-exclude` para que
Black respete ese guard. El archivo de prueba, modificado en esta rama, se
ajustó manualmente al diff mostrado por `black --check --diff`; no se lanzó
Black en modo escritura.

Tras esos cambios, el comando exacto de CI termina correctamente y deja 1157
archivos sin cambios. Los hashes protegidos permanecen
`537554f0cab9fb4ca456b2b99a43fca7b275241dcddfa5bb0fc3dcad78534e70`
para `lexer.py` y
`3017fa31e1707ca82358d548e71ba27d4b8e73342950ab6959b32c13dcc02505`
para `parser.py`.

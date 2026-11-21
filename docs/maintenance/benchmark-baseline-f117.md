# F1.17 — Procedimiento para establecer una referencia real de benchmarks

Estado: **procedimiento documental; sin baseline aprobado ni publicado**.

## Bloqueos comprobados
- `compare_releases.py` consulta `releases/latest` si no se indica `--base`. Sin una release elegible con `benchmarks.json`, la comparación falla y **debe seguir fallando**.
- `run_benchmarks.py` invoca actualmente `cobra.cli.cli compilar`. Los logs del CI muestran que `compilar` no es un subcomando aceptado. El runner puede omitir backends tras `CalledProcessError` y producir una lista vacía. **No se puede certificar una referencia con esos resultados sin corregir y validar antes el runner en una tarea separada**.
- El runner usa `subprocess.run(..., check=False)`; se debe comprobar explícitamente que cada ejecución termina con código cero antes de aceptar sus métricas.
- La medición de memoria depende de `resource` o `psutil`; `-1` indica memoria no medida y no debe aceptarse como referencia comparable.
- No se ha verificado ninguna release estable ni rama histórica utilizable.

## Procedimiento propuesto (NO publicar automáticamente)
1. Elegir un commit inmutable y registrar SHA completo, sistema operativo/arquitectura, CPU, Python, Node, Rust y versiones de dependencias. Utilizar un runner reproducible y el mismo entorno para baseline y futuras comparaciones.
2. En rama **distinta** de la corrección UTF-8, corregir y probar la invocación del CLI del runner, sin tocar Lexer, Parser, AST, gramática, fixtures ni contratos.
3. Ejecutar `python scripts/benchmarks/run_benchmarks.py > benchmarks.json` sin activar `--include-best-effort-runtime` ni `--include-transpilation-only`. No instalar Go, Java, JDK, Chocolatey ni MinGW.
4. Validar manualmente el JSON: array no vacío, solo backends oficiales `python`, `javascript`, `rust`; claves `backend`, `time`, `memory_kb`; backends sin duplicados; tiempo numérico finito positivo; memoria entera no negativa y realmente medida; ejecución de cada comando con exit code 0. Si falta algún backend previsto, **bloquear la aprobación** y documentar la causa.
5. Repetir mediciones bajo condiciones estables, documentar dispersión y método de agregación. No mezclar sistemas operativos, runtimes o herramientas diferentes sin establecer una política de comparabilidad.
6. Guardar el JSON original, metadatos del entorno, SHA del commit, logs y hashes SHA-256 de los archivos. Revisar resultados por pares y aprobar explícitamente el baseline.
7. **Solo tras aprobación humana**, publicar `benchmarks.json` como asset de una release estable, o mantener una referencia versionada en `benchmarks-history/benchmarks/history/<version>.json`. Verificar mediante lectura remota que el archivo publicado coincide byte a byte con el aprobado.
8. Ejecutar la comparación canónica contra esa referencia. Mantener el umbral de regresión del 10 %, sin `continue-on-error`, valores ficticios, listas vacías, ni fallback que convierta falta de referencia en éxito.

## Criterios de cierre
- Baseline real, no vacío, comparable y trazable a commit y entorno.
- Todos los backends oficiales requeridos medidos con éxito.
- Referencia accesible por el mismo mecanismo usado en CI.
- Ejecución remota del job de benchmarks satisfactoria, con reporte de diferencias.
- Cualquier problema MyPy o del CI general permanece independiente; no autoriza merge del PR UTF-8.

**No confundir este documento con evidencia de benchmarks ejecutados.**

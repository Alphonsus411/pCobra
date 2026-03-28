# Tutorial Básico

Este directorio contiene un ejemplo mínimo de un programa escrito en Cobra y su
transpilación manual a Python.

Aunque este tutorial usa Python, la política pública del proyecto mantiene 8
targets oficiales de salida con nombres canónicos: `python`, `rust`,
`javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.

## Archivos

- `hola_mundo.co`: Código Cobra que imprime un saludo.
- `hola_mundo.py`: Resultado de la transpilación a Python.
- `hola_mundo.out`: Salida generada al ejecutar el script Python.

## Pasos para reproducir

1. Ejecutar la transpilación:
   ```bash
   PYTHONPATH=..:../src python compile_manual.py > hola_mundo.py
   ```
   El script `compile_manual.py` usa los módulos de Cobra para convertir el archivo `hola_mundo.co` en Python.
2. Ejecutar el script generado:
   ```bash
   PYTHONPATH=..:../src python hola_mundo.py > hola_mundo.out
   ```
3. Revisar `hola_mundo.out` para ver el texto `Hola, mundo!`.

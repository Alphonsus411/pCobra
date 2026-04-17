# Ejemplos

Este directorio reúne distintos ejemplos de uso de Cobra y material relacionado.

## Política canónica de targets en ejemplos públicos

Para recorrido de usuario final, este directorio debe sugerir únicamente:
`python`, `rust`, `javascript`.

Los targets `go`, `cpp`, `java`, `wasm` y `asm` se mantienen como **internal-only**
para migración/regresión técnica y no deben presentarse como opción pública de CLI.

## Subcarpetas

- **avanzados/**: ejercicios que profundizan en control de flujo, funciones y clases. Para ejecutar uno:
  ```bash
  cobra ejecutar examples/avanzados/<tema>/<archivo>.co
  ```
- **hello_world/**: demostraciones para targets públicos (`python`, `rust`, `javascript`) y artefactos legacy internal-only de referencia técnica.
- **[hola_mundo](hola_mundo/)**: ejemplo mínimo para transpilar a Python.
  ```bash
  cobra compilar examples/hola_mundo/hola.co --backend python
  ```
- **plugins/**: plugins de muestra instalables en modo editable. Para probarlos:
  ```bash
  cd examples/plugins
  pip install -e .
  cobra plugins
  ```
- **tutorial_basico/**: guía básica con un hola mundo y utilidades de compilación manual. El programa principal se corre con:
  ```bash
  cobra ejecutar examples/tutorial_basico/hola_mundo.co
  ```

- **main.py**: script Python que muestra cómo usar `standard_library.interfaz` para
  imprimir tablas y barras de progreso enriquecidas en la consola.

## Archivos individuales

- `clase_metodo_atributo.co`
- `funciones_principales.co`
- `patrones.co`

Cada uno puede ejecutarse con:
```bash
cobra ejecutar examples/<archivo>.co
```

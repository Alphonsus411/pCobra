# Ejemplos

Este directorio reúne distintos ejemplos de uso de Cobra y material relacionado.

## Política canónica de targets en ejemplos públicos

Toda la documentación y los ejemplos públicos de este directorio deben usar solo
los 8 nombres canónicos de targets oficiales de transpilación:
`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.

Además, conviene leerlos con esta distinción:

- **Transpilación oficial**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Runtime oficial**: `python`, `rust`, `javascript`, `cpp`.
- **Runtime experimental/best-effort**: `go`, `java`.
- **Solo transpilación sin runtime público**: `wasm`, `asm`.

## Subcarpetas

- **avanzados/**: ejercicios que profundizan en control de flujo, funciones y clases. Para ejecutar uno:
  ```bash
  cobra ejecutar examples/avanzados/<tema>/<archivo>.co
  ```
- **hello_world/**: demostraciones "Hola Mundo" para los 8 targets oficiales (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`).
- **[hola_mundo](hola_mundo/)**: ejemplo mínimo para transpilar a Python.
  ```bash
  cobra examples/hola_mundo/hola.co --to python
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

# Ejemplos

Este directorio reúne distintos ejemplos de uso de Cobra y material relacionado.

## Subcarpetas

- **avanzados/**: ejercicios que profundizan en control de flujo, funciones y clases. Para ejecutar uno:
  ```bash
  cobra ejecutar examples/avanzados/<tema>/<archivo>.co
  ```
- **hello_world/**: demostraciones "Hola Mundo" en varios lenguajes. El ejemplo en Cobra se ejecuta con:
  ```bash
  cobra ejecutar examples/hello_world/cobra/hola.co
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

## Archivos individuales

- `clase_metodo_atributo.co`
- `funciones_principales.co`
- `patrones.co`

Cada uno puede ejecutarse con:
```bash
cobra ejecutar examples/<archivo>.co
```

# Hololang y transpilación cruzada

Este directorio reúne fragmentos mínimos que ilustran el flujo de trabajo entre
Cobra y Hololang.  Los comandos están pensados para ejecutarse desde la raíz del
repositorio.

## Archivos

- `saludo.co`: versión en Cobra del ejemplo básico con holobits.
- `saludo.holo`: contraparte Hololang generada por el transpilador.

## De Cobra a Hololang

```bash
cobra compilar examples/hololang/saludo.co --backend hololang --salida saludo.holo
```

El parámetro `--salida` guarda la traducción en un archivo.  Si lo omites, la
salida se muestra por consola.

## Hololang de vuelta a Cobra

```bash
cobra transpilar-inverso examples/hololang/saludo.holo --origen hololang --destino hololang
```

El comando `transpilar-inverso` parsea el código Hololang, lo convierte al AST
de Cobra y lo reemite con el transpilador seleccionado.  Aunque en este ejemplo
se vuelve a generar Hololang, el paso intermedio valida que la estructura del
programa sea compatible con Cobra.

Para inspeccionar cómo se vería el mismo programa si el destino fuera Python
puedes ejecutar:

```bash
cobra transpilar-inverso examples/hololang/saludo.holo --origen hololang --destino python
```

## Hololang a otros lenguajes

Desde los mismos archivos puedes emitir ensamblador simbólico u otros backends
soportados:

```bash
cobra transpilar-inverso examples/hololang/saludo.holo --origen hololang --destino asm
cobra transpilar-inverso examples/hololang/saludo.holo --origen hololang --destino rust
```

El primer comando produce instrucciones de bajo nivel basadas en el IR de
Hololang, mientras que el segundo genera una implementación equivalente en Rust.

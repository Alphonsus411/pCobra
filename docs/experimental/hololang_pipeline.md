# EXPERIMENTAL · FUERA DE LA NAVEGACIÓN PÚBLICA · Pipeline interno de Hololang

> **Estado:** documentación archivada para mantenimiento interno y contexto técnico.
>
> **Política:** este documento **no forma parte del recorrido público normal** y **no** convierte `hololang` en un lenguaje de usuario, un target oficial de `cobra compilar` ni un origen reverse soportado por política.

## Alcance

Hololang se conserva aquí únicamente como nombre histórico de una representación intermedia usada internamente por el compilador. Su función es describir estados intermedios del pipeline entre el AST de Cobra y algunos generadores de código o herramientas de diagnóstico.

La documentación pública normal del proyecto solo debe hablar, como mucho, de una **IR interna del compilador**. El detalle nominal y la sintaxis archivada permanecen en esta ruta experimental para tareas de mantenimiento.

## Flujo resumido

1. El front-end analiza el código fuente y construye el AST de Cobra.
2. El compilador puede normalizar ese AST y bajarlo a una representación intermedia interna.
3. Los backends oficiales consumen esa IR para producir `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` o `asm`.

## Sintaxis histórica de referencia

Todo archivo Hololang comenzaba importando módulos estándar generados por el transpilador:

```hololang
use holo.core::*;
use holo.bits::*;
```

A partir de ahí se podían declarar variables, funciones y holobits:

- Declaraciones: `let` crea variables inmutables y admite anotaciones de tipo opcionales.
- Funciones: `fn` define rutinas con parámetros separados por comas.
- Bloques: se delimitan con llaves `{` y `}`.
- Impresión: `print(expr);` envía datos a la salida estándar.
- Holobits: `holobit([1.0, -0.5, 0.8]);` construye estructuras multidimensionales.

Ejemplo histórico generado a partir de un programa Cobra:

```hololang
use holo.core::*;
use holo.bits::*;

let saludo = "Hola desde Hololang";

fn principal() {
    let espectro = holobit([0.8, -0.5, 1.2]);
    print(saludo);
    print("Norma:" + norma(espectro));
}

fn norma(holo) {
    return magnitud(holo);
}
```

## Relación con la CLI pública

La CLI pública de Cobra **no** expone `hololang` como destino oficial independiente. Los flujos soportados por política siguen limitados a los backends y orígenes reverse documentados como oficiales.

```bash
cobra compilar examples/hola_mundo/hola.co --backend python
```

```bash
cobra transpilar-inverso examples/hello_world/python.py --origen python --destino java
```

## Nota de mantenimiento

Si este material vuelve a citarse desde documentación pública, debe hacerse solo como referencia breve a una **IR interna** y sin restaurar una guía pública dedicada ni añadir `hololang` a índices, tablas de targets o ejemplos de CLI dirigidos a usuarios.

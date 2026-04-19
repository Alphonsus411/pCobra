# Manual del Lenguaje Cobra

> **Estado del documento: Referencia**
>
> Documento de referencia técnica. No sustituye la ruta pedagógica del [Libro de Programación con Cobra](LIBRO_PROGRAMACION_COBRA.md).

Versión 10.0.13

## Propósito y alcance

Este manual define, de forma compacta, los elementos técnicos del lenguaje y la CLI:

- sintaxis y palabras clave,
- estructuras soportadas,
- aliases reconocidos por parser/transpiladores,
- reglas de control de flujo y errores,
- comportamiento esperado de la herramienta.

Para aprendizaje paso a paso, usa el [Libro principal](/docs/LIBRO_PROGRAMACION_COBRA.md).
Para un resumen breve, usa la [Guía básica](/docs/guia_basica.md).

## ¿Por dónde empezar?

1. [Libro de Programación Cobra (ruta principal de aprendizaje)](/docs/LIBRO_PROGRAMACION_COBRA.md).
2. Este documento, **MANUAL_COBRA**, como referencia técnica canónica.
3. [Guía básica](/docs/guia_basica.md) y [contenido histórico](/docs/historico/README.md) como material secundario.

## 1) CLI pública y contrato

Comandos oficiales:

```bash
cobra run archivo.co
cobra build archivo.co
cobra test archivo.co
cobra mod list
```

> Los comandos legacy pueden existir por compatibilidad, pero no forman parte del contrato público recomendado.

## 2) Léxico y sintaxis esencial

- Asignación: `x = 1`
- Condicionales: `si`, `sino_si`/`sino si`, `sino`
- Bucles: `mientras`, `para`
- Funciones: `funcion` / `func`
- Clases: `clase` (aliases históricos: `estructura`, `registro`)
- Comentarios: `# ...`

Operadores lógicos aceptados:

- simbólicos: `&&`, `||`, `!`
- alias: `y`, `o`, `no`

## 3) Tipos y estructuras

- escalares: texto, números, booleanos
- contenedores: listas, diccionarios, tuplas/conjuntos (según backend)
- objetos/clases con atributos y métodos

## 4) Alias de métodos especiales

Alias habituales soportados por el parser (mapeados a nombres especiales):

- `inicializar` → `__init__`
- `iterar` → `__iter__`
- `texto` → `__str__`
- `representar` → `__repr__`
- `llamar` → `__call__`
- `obtener_item` / `poner_item` / `borrar_item` → `__getitem__` / `__setitem__` / `__delitem__`
- `entrar` / `salir` → `__enter__` / `__exit__`
- `entrar_async` / `salir_async` → `__aenter__` / `__aexit__`

Si dos declaraciones colisionan tras normalización (por ejemplo `inicializar` y `__init__`), el parser emite advertencia.

## 5) Control de flujo y semántica

- Condicionales encadenados con `sino_si`.
- `romper` y `continuar` dentro de bucles.
- Guard clauses con `garantia`/`guard`.
- Diferidos con `defer`/`aplazar` (orden LIFO).

## 6) Errores y excepciones

- Bloques: `try/catch/finally` o `intentar/capturar/finalmente`.
- Lanzamiento: `throw` o `lanzar`.
- Excepción base de runtime: `ExcepcionCobra`.

## 7) Módulos e imports

- `import` y variantes de importación por símbolo.
- Resolución de módulos según estructura de proyecto.
- Paquetes históricos (`cobra.pkg`) quedan como compatibilidad legacy.

## 8) Asincronía y concurrencia

- Funciones con `asincronico`.
- Espera con `esperar`.
- Utilidades de runtime asincrónico disponibles vía `corelibs.asincrono` y estándar.

## 9) Compatibilidad y targets

La superficie oficial prioriza:

- `python`
- `javascript`
- `rust`

Otros targets/documentos legacy se consideran históricos o de migración interna.

## 10) Referencias relacionadas

- Ruta pedagógica principal: [Libro de Programación Cobra](/docs/LIBRO_PROGRAMACION_COBRA.md)
- Referencia técnica canónica: [MANUAL_COBRA.md](/docs/MANUAL_COBRA.md)
- Resumen rápido (histórico): [guia_basica.md](/docs/guia_basica.md)
- Índice histórico secundario: [historico/README.md](/docs/historico/README.md)
- Especificación formal: [SPEC_COBRA.md](/docs/SPEC_COBRA.md)
- Contratos técnicos de runtime: [contrato_runtime_holobit.md](/docs/contrato_runtime_holobit.md)

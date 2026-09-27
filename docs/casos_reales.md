# Casos de uso reales

Esta sección reúne ejemplos pequeños que se ejecutan con el Lexer, el Parser y
la CLI actuales. Los archivos fuente están en `examples/casos_reales/` y los cuadernos
equivalentes en `notebooks/casos_reales/`.

Los cuadernos deben iniciarse desde la raíz del repositorio. Cada uno muestra el
fuente correspondiente y lo ejecuta mediante la entrada pública actual:

```bash
PYTHONPATH=src python -m pcobra.cli run examples/casos_reales/<ruta>.cobra
```

## Alcance de los ejemplos

Las tres fuentes Cobra son autocontenidas:

- `examples/casos_reales/bioinformatica/ejemplo_gc.cobra` calcula el porcentaje
  de bases G y C de un texto.
- `examples/casos_reales/inteligencia_artificial/modelo_ia.cobra` aplica una
  combinación lineal sencilla a dos valores.
- `examples/casos_reales/analisis_datos/estadisticas.cobra` calcula el promedio
  de tres valores.

Las celdas Python de preparación de los cuadernos ilustran el contexto del caso
de uso, pero no convierten sus paquetes en módulos Cobra. En particular,
`usar` no importa directamente paquetes Python como `sklearn`, `pandas`,
`matplotlib`, `flask`, `pygame` o `biopython`.

## Contrato vigente

Para ampliar estos ejemplos, utiliza estas referencias:

1. [Libro de Programación Cobra](LIBRO_PROGRAMACION_COBRA.md), fuente normativa
   de sintaxis y comportamiento.
2. [Manual de Cobra](MANUAL_COBRA.md), referencia técnica canónica.
3. [Especificación del lenguaje](SPEC_COBRA.md), gramática implementada.
4. [Inventario público de módulos de `usar`](inventario_usar_modulos.md).
5. [Manual de CobraHub](frontend/cobrahub.rst), para empaquetado y distribución
   de artefactos `.co`.

Instalar una dependencia externa no la convierte en un módulo Cobra. AGIX es el
motor interno de sugerencias de la distribución Python, no un módulo público
accesible mediante `usar "analizador_agix"`; del mismo modo, instalar un paquete
desde CobraHub no amplía automáticamente el catálogo público de `usar`.

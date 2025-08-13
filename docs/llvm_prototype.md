# Prototipo LLVM

Este documento actúa como README del experimento para compilar Cobra con LLVM. Resume el estado actual del prototipo, sus limitaciones y los siguientes pasos propuestos.

## Limitaciones actuales

- Traducción parcial del árbol de sintaxis abstracta; solo se cubren expresiones aritméticas y estructuras de control básicas.
- Falta de runtime propio para administrar memoria, manejo de errores y entrada/salida.
- Ausencia de integración con el sistema de tipos estático de Cobra.
- No existen pruebas automáticas que validen la generación de IR.
- Documentación dispersa y sin guía para reproducir resultados.

## Mejoras recomendadas

1. Completar la conversión del AST a LLVM IR, incluyendo funciones, clases y manejo de excepciones.
2. Diseñar un runtime mínimo que permita memoria gestionada y llamadas a librerías estándar.
3. Integrar la verificación de tipos y optimizaciones básicas durante la generación de IR.
4. Incorporar pruebas unitarias y de integración que comparen el IR esperado con el generado.
5. Consolidar la documentación y crear ejemplos reproducibles.

## Plan futuro

- **Soporte completo del lenguaje:**
  - Fase 1: cubrir estructuras de datos y funciones.
  - Fase 2: implementar runtime y gestión de memoria.
  - Fase 3: optimizaciones, empaquetado y distribución.

- **Cierre del experimento:**
  - Documentar los hallazgos técnicos.
  - Mantener la rama prototipo como referencia histórica.
  - Redirigir esfuerzos a otros backends o prioridades del proyecto.


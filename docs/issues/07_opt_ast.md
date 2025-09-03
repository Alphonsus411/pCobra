---
name: Solicitud de mejora
about: Sugiere una nueva función o mejora
title: "[Mejora] Optimizar el AST para mayor rendimiento"
labels: [enhancement, avanzado]
assignees: ''
---

**¿Tu solicitud está relacionada con un problema? Por favor descríbelo.**

Algunos programas complejos generan árboles de sintaxis muy grandes y se observa un consumo alto de memoria.

**Describe la solución que te gustaría**

Implementar pases de optimización que simplifiquen nodos redundantes y fusionen operaciones cuando sea posible.

**Alternativas consideradas**

Limitar el tamaño del código fuente o dividir el proyecto en módulos más pequeños.

**Contexto adicional**

Revisar `src/backend/cobra/parser/optimizations.py` si existe, o crear un nuevo módulo para estas optimizaciones.

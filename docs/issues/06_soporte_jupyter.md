---
name: Solicitud de mejora
about: Sugiere una nueva función o mejora
title: "[Mejora] Soporte para ejecución en Jupyter"
labels: [enhancement, medio]
assignees: ''
---

**¿Tu solicitud está relacionada con un problema? Por favor descríbelo.**

Los usuarios desean escribir código Cobra en cuadernos Jupyter para experimentación interactiva.

**Describe la solución que te gustaría**

Desarrollar un kernel basado en `ipykernel` que ejecute código Cobra y se integre con la CLI.

**Alternativas consideradas**

Proveer scripts de conversión a Python antes de ejecutar en Jupyter.

**Contexto adicional**

Consultar el submódulo `src/backend/jupyter_kernel` para ver la estructura inicial del kernel.

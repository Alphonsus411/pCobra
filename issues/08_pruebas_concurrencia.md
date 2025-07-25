---
name: Solicitud de mejora
about: Sugiere una nueva función o mejora
title: "[Mejora] Pruebas de concurrencia"
labels: [enhancement, medio]
assignees: ''
---

**¿Tu solicitud está relacionada con un problema? Por favor descríbelo.**

El intérprete ofrece soporte básico para hilos pero carece de pruebas que validen su estabilidad en escenarios concurrentes.

**Describe la solución que te gustaría**

Crear un conjunto de pruebas en `src/tests/unit` que ejecuten tareas paralelas y verifiquen la integridad de los datos y la ausencia de bloqueos.

**Alternativas consideradas**

Limitar el uso de concurrencia a ejemplos simples sin cubrir casos de carrera.

**Contexto adicional**

Revisar `src/tests/unit/test_hilos.py` como punto de partida y extenderlo con casos más complejos.

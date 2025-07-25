---
name: Solicitud de mejora
about: Sugiere una nueva función o mejora
title: "[Mejora] Optimizar validación del modo seguro"
labels: [enhancement, medio]
assignees: ''
---

**¿Tu solicitud está relacionada con un problema? Por favor descríbelo.**

La verificación del modo seguro puede resultar lenta en proyectos grandes.

**Describe la solución que te gustaría**

Refactorizar el validador para reducir pasos innecesarios y mejorar el rendimiento sin comprometer la seguridad.

**Alternativas consideradas**

Aplicar un caché simple de resultados parciales.

**Contexto adicional**

Analizar las funciones en `backend/src/cobra/safe` y revisar las pruebas relacionadas en `src/tests/unit`.

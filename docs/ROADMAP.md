# Roadmap

Este documento detalla los hitos planificados para la serie 10.x del proyecto.

## v10.1
- Mejorar la integración con plugins mediante una API estable.
- Optimizar el sistema de caché para compilaciones incrementales.
- Añadir documentación sobre despliegue en entornos *serverless*.

## v10.2
- Extender la transpilación a nuevos lenguajes objetivo.
- Incorporar análisis estático avanzado para detección temprana de errores.
- Proveer un modo de ejecución distribuido.

## Referencias históricas
Las metas anteriores de las versiones 0.x y 1.3 se han movido a `docs/historico/ROADMAP_v0_v1.md` para consulta de legado.

## Reparaciones POO pendientes

- [x] **POO-012 / 42F — miembros de clase en contenedor incorrecto.**
  El Parser rechaza explícitamente asignaciones y `pasar` en el cuerpo de una
  clase; las clases vacías y las que contienen métodos permanecen válidas.
  No se introducen campos de clase, sintaxis nueva ni cambios de AST.
  Véanse la evidencia y los criterios de cierre en
  [POO_ROADMAP.md — POO-012](POO_ROADMAP.md#poo-012--miembros-de-clase-no-método).
  Este cierre no implica que 42F completo ni las tareas posteriores estén
  resueltos.

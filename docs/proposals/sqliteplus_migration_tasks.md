# Plan de trabajo para integrar `sqliteplus-enhanced`

Este plan desglosa en tareas independientes las acciones necesarias para adoptar `sqliteplus-enhanced` 1.0.6 como motor de base de datos por defecto dentro del núcleo de Cobra. Cada bloque incluye el objetivo, subtareas claras, entregables esperados y dependencias para facilitar su seguimiento.

## 1. Preparación de dependencias y compatibilidad
- **Objetivo:** Actualizar la configuración del proyecto para incluir `sqliteplus-enhanced` y garantizar la compatibilidad con Python ≥ 3.10.
- **Subtareas:**
  - Añadir la dependencia en `pyproject.toml`, `requirements.txt` y archivos relacionados.
  - Ajustar clasificadores, notas de instalación y cualquier referencia a la versión mínima de Python.
  - Blindar el registro de módulos en `pcobra.__init__` y `pcobra.cli` para evitar colisiones con los paquetes `core` y `utils` de la nueva librería.
- **Entregables:** Commits que actualicen los archivos de configuración y documentación correspondiente.
- **Dependencias:** Ninguna.

## 2. Creación del adaptador de base de datos en `pcobra.core`
- **Objetivo:** Centralizar el acceso a SQLitePlus en un módulo dedicado.
- **Subtareas:**
  - Implementar un módulo `pcobra.core.database` con inicialización perezosa, control de llave `SQLITE_DB_KEY` y definición de la ruta por defecto (`~/.cobra/sqliteplus/core.db`).
  - Gestionar la carga del backend evitando conflictos de nombres con módulos externos.
  - Exponer funciones utilitarias (`get_connection`, `store_ast`, `load_ast`, etc.).
- **Entregables:** Nuevo módulo y pruebas de smoke básicas.
- **Dependencias:** Tarea 1.

## 3. Migración de la caché de AST y fragmentos a SQLitePlus
- **Objetivo:** Sustituir los archivos JSON por tablas en la base de datos para tokens, AST completos y fragmentos.
- **Subtareas:**
  - Reescribir `pcobra.core.ast_cache` para delegar en el adaptador.
  - Implementar índices y limpieza (`DELETE`, `VACUUM`) dentro del backend.
  - Actualizar el comando `cobra cache` para trabajar con la nueva estrategia.
  - Gestionar la variable `COBRA_AST_CACHE` como ruta alternativa o deprecada.
- **Entregables:** Código refactorizado y documentación interna actualizada.
- **Dependencias:** Tareas 1 y 2.

## 4. Persistencia de Qualia en la base de datos
- **Objetivo:** Unificar el almacenamiento de estado de Qualia con el resto de la información en SQLitePlus.
- **Subtareas:**
  - Modificar `pcobra.core.qualia_bridge` para leer/escribir desde la tabla `qualia_state`.
  - Implementar migración automática desde el archivo JSON previo si existe.
  - Mantener la interfaz pública intacta y añadir pruebas unitarias.
- **Entregables:** Módulo refactorizado, lógica de migración y pruebas.
- **Dependencias:** Tareas 1 y 2.

## 5. Actualización de la suite de pruebas
- **Objetivo:** Alinear las pruebas unitarias e integrales con el backend SQLite.
- **Subtareas:**
  - Crear fixtures temporales para inicializar una base de datos aislada en cada prueba.
  - Reescribir las pruebas de caché (`test_ast_cache`, `test_token_cache`) para usar consultas SQL o el adaptador.
  - Incorporar casos para la limpieza de caché y la migración de Qualia.
- **Entregables:** Suite de pruebas actualizada y verde.
- **Dependencias:** Tareas 2, 3 y 4.

## 6. Documentación y notas de versión
- **Objetivo:** Reflejar la transición a SQLitePlus en toda la documentación oficial.
- **Subtareas:**
  - Actualizar `README.md`, `docs/README.en.md`, `docs/cache_incremental.md` y cualquier referencia adicional.
  - Añadir entradas al `CHANGELOG` y a los manuales técnicos sobre la nueva configuración.
  - Revisar referencias a `COBRA_AST_CACHE` para guiarlas hacia la nueva variable de entorno o proceso.
- **Entregables:** Documentación sincronizada con los cambios de arquitectura.
- **Dependencias:** Tareas 1 a 5.

## 7. Seguimiento y comunicación
- **Objetivo:** Garantizar que el equipo tenga visibilidad del progreso y pendientes.
- **Subtareas:**
  - Registrar el estado de cada tarea en el tablero de proyecto o herramienta equivalente.
  - Crear issues individuales por tarea para facilitar la asignación.
  - Preparar un comunicado de cambios internos para los mantenedores.
- **Entregables:** Issues creados, tablero actualizado y comunicado interno.
- **Dependencias:** Tarea 1 (para iniciar el seguimiento) y las posteriores según avance.

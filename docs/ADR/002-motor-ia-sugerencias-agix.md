# ADR 002: Motor IA canónico para sugerencias Cobra

## Estado

Aceptada.

## Contexto

Durante la revisión de cambios potenciales del motor IA apareció el nombre
`agi-core` como posible sustituto de `agix`. La comprobación de dependencias y
código vigente muestra que Cobra no usa `agi-core` como dependencia declarada ni
como API pública de integración:

- `pyproject.toml` declara `agix>=1.11.0,<1.12` dentro de
  `[project].dependencies`, por lo que forma parte de la distribución oficial y
  no de un extra opcional.
- `src/pcobra/gui/runtime.py` define `CANONICAL_SUGGESTION_ENGINE = "agix"` y
  usa ese nombre para detectar de forma liviana si el motor está disponible.
- `src/pcobra/ia/analizador_sugerencias.py` es la fachada pública estable y
  delega en `src/pcobra/ia/analizador_agix.py`.
- `src/pcobra/ia/analizador_agix.py` importa API pública de `agix`, en concreto
  `agix.reasoning.basic.Reasoner` y `agix.emotion.emotion_simulator.PADState`.

Existe un paquete externo publicado con el nombre `agi-core`, pero su mera
existencia en el ecosistema Python no implica que sea compatible con Cobra ni
que deba reemplazar la integración actual. No se ha identificado en Cobra una
historia de usuario aprobada, contrato de API, pruebas de compatibilidad ni
plan de migración que justifiquen sustituir `agix`.

## Decisión

El nombre canónico del motor IA de sugerencias en Cobra sigue siendo `agix`.
La referencia `agi-core`, cuando aparezca en tareas o conversaciones sin un
contrato técnico adicional, debe tratarse como una referencia informal o una
incoherencia nominal, no como una instrucción de migración.

No se debe cambiar `CANONICAL_SUGGESTION_ENGINE = "agix"` ni añadir detección,
imports o dependencias de `agi-core` sin una ADR nueva que apruebe una migración
o una integración paralela.

`agix` debe permanecer en `[project].dependencies`: la instalación completa de
pCobra lo instala como dependencia oficial y no se crea un extra para el motor.
La carga continúa siendo diferida para tolerar instalaciones parciales o
entornos headless donde el import no sea posible. Esa tolerancia operativa no
convierte la dependencia en opcional: al solicitar sugerencias, la fachada debe
emitir un error claro con instrucciones de instalación, mientras los flujos que
no usan IA pueden continuar.

## API pública usada por Cobra

La integración vigente con `agix` usa esta superficie mínima:

1. Paquete Python real: `agix`.
2. Razonador: `agix.reasoning.basic.Reasoner`.
3. Estado emocional opcional: `agix.emotion.emotion_simulator.PADState`.
4. Método esperado del razonador: `select_best_model(evaluaciones)`.
5. Modulación emocional opcional: `modular_por_emocion(pad)` cuando se reciben
   valores completos de placer, activación y dominancia.

La API pública estable para el resto de Cobra no es `agix` directamente, sino
`pcobra.ia.analizador_sugerencias.generar_sugerencias()`. La GUI debe seguir
usando esa fachada bajo demanda después de validar el código con `Lexer` y
`Parser`.

## Política de compatibilidad

- `agix` es el único motor soportado para sugerencias mientras esta ADR esté
  vigente.
- `agix` permanece como dependencia oficial en `[project].dependencies`; solo
  su disponibilidad en instalaciones parciales o headless se trata de forma
  tolerante hasta que se intenta usar el servicio.
- `pcobra.ia.analizador_sugerencias` es la fachada estable para consumidores
  internos y externos del paquete Cobra.
- `pcobra.ia.analizador_agix` puede contener shims o alias técnicos necesarios
  para compatibilidad con versiones de `agix`, pero esos detalles no forman
  parte del contrato público de Cobra.
- `agi-core` no tiene compatibilidad implícita con `agix`; cualquier soporte de
  `agi-core` requiere una ADR separada con contrato de API, estrategia de
  instalación, pruebas y plan de migración o coexistencia.

## Cambios requeridos ante una futura migración

Si una ADR futura decide sustituir o complementar `agix` con otro motor, deberá
cubrir como mínimo:

1. Actualización de dependencias en `pyproject.toml` y documentación de
   instalación.
2. Cambio explícito de la detección en `src/pcobra/gui/runtime.py`, incluyendo
   el valor de `CANONICAL_SUGGESTION_ENGINE` si el motor canónico cambia.
3. Adaptación de `pcobra.ia.analizador_sugerencias` para mantener una fachada
   estable aunque cambie la implementación interna.
4. Nuevo adaptador de motor o reemplazo controlado de `analizador_agix.py`.
5. Pruebas que verifiquen disponibilidad, errores cuando falta la dependencia,
   validación previa con `Lexer`/`Parser` y validación de fragmentos sugeridos.
6. Actualización de `docs/LIBRO_PROGRAMACION_COBRA.md`,
   `docs/gui_idle_especificacion.md` y cualquier guía de GUI o dependencias.

## Consecuencias

- Se evita introducir una dependencia externa no validada solo por similitud de
  nombre.
- La GUI conserva una detección liviana y coherente con la dependencia oficial,
  sin bloquear entornos parciales o headless que no solicitan sugerencias.
- Los usuarios reciben instrucciones consistentes: instalar `agix` para activar
  sugerencias IA.
- Cualquier cambio real de motor queda bloqueado hasta documentar su contrato,
  compatibilidad y pruebas en una ADR dedicada.

# Checklist arquitectónica: Backend Pipeline

## Contrato unificado (aplica a toda esta checklist)

- Cobra es el **único lenguaje/interfaz pública**.
- Solo existen **3 backends internos oficiales**: `python`, `javascript`, `rust`.
- La decisión de backend es **interna** (no configurable por usuario final), salvo hints internos controlados.

Usar esta checklist antes de mergear nuevas features que afecten compile/transpile/runtime.

## Flujo oficial (obligatorio)

- [ ] La feature respeta el flujo `Frontend Cobra -> BackendPipeline -> Bindings`.
- [ ] No se introduce un nuevo entrypoint paralelo a `pcobra.cobra.build.backend_pipeline`.

## Contrato de llamadas internas

- [ ] CLI, imports y stdlib llaman únicamente a:
  - `backend_pipeline.resolve_backend_runtime(...)`
  - `backend_pipeline.build(...)`
  - `backend_pipeline.transpile(...)`
- [ ] No hay imports directos a registro de transpiladores oficiales desde CLI/imports/stdlib.
- [ ] No hay llamadas directas a `generate_code(...)` de transpiladores oficiales fuera de `backend_pipeline`.

## Validación y CI

- [ ] Se ejecutó el auditor `scripts/ci/audit_backend_pipeline_entrypoint.py`.
- [ ] Se ejecutó el auditor `scripts/ci/audit_public_backend_exposure_terms.py` para impedir exposiciones públicas de alias/backends retirados (`go`, `cpp`, `java`, `wasm`, `asm`, `py`, `js`, `node`, `golang`, `jvm`) en registros de transpiladores, choices de CLI/GUI y documentación de usuario no histórica.
- [ ] Cualquier mención a alias/backends retirados vive únicamente en documentos históricos explícitos, pruebas de rechazo o shims legacy autorizados.
- [ ] La documentación de arquitectura (`docs/architecture/overview.md`) sigue reflejando el flujo oficial.
- [ ] Si hubo excepciones temporales por migración, están justificadas y acotadas en ADR/ticket.

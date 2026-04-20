# Contrato de bindings Cobra (Python / JavaScript / Rust)

## Contrato unificado (aplica a toda esta guía)

- Cobra es el **único lenguaje/interfaz pública**.
- Solo existen **3 backends internos oficiales**: `python`, `javascript`, `rust`.
- La decisión de backend es **interna** (no configurable por usuario final), salvo hints internos controlados.

- **Estado:** Aprobado
- **Fecha:** 2026-04-14
- **Alcance:** CLI runners (`execute_cmd`) y futuros runners/runtime bridges

## Objetivo

Definir un contrato técnico único para evitar lógica ad-hoc en runners sobre cómo conectar Cobra con cada runtime soportado.

## Rutas oficiales de binding

### 1) Python: import bridge directo

- **Ruta contractual:** `python_direct_import`
- **Estrategia:** importación directa de módulos Python canónicos desde el proceso de ejecución Cobra.
- **Frontera de ejecución:** mismo proceso.
- **Contrato:** API Python estable + typing.

### 2) JavaScript: runtime bridge (proceso/VM controlada)

- **Ruta contractual:** `javascript_runtime_bridge`
- **Estrategia:** bridge hacia runtime JS dedicado (proceso o VM controlada).
- **Frontera de ejecución:** aislada respecto al proceso principal.
- **Contrato:** mensajes/IPC versionados.

### 3) Rust: bindings compilados / FFI con ABI estable

- **Ruta contractual:** `rust_compiled_ffi`
- **Estrategia:** bindings compilados sobre librería compartida.
- **Frontera de ejecución:** interfaz nativa FFI.
- **Contrato:** ABI estable y versionada.

## Módulo técnico

Se establece como fuente de verdad canónica:

- `bindings/contract.py`

Compatibilidad interna (`pcobra`) via re-export:

- `src/pcobra/cobra/bindings/contract.py`

El contrato expone:

- `BindingRoute` (enum de rutas),
- `BindingCapabilities` (tipo estructurado de capacidades),
- contratos concretos para `python`, `javascript`, `rust`,
- `resolve_binding(language)` para consumo uniforme desde runners.

## Consumo en runners

- `execute_cmd.py` consume `RuntimeManager` para:
  - resolver contrato + bridge,
  - validar seguridad por ruta y por comando (`run`/`test`),
  - validar ABI efectiva por backend (incluye ABI negociada por proyecto).
- `build/backend_pipeline.py` expone `resolve_backend_runtime(...)` y agrega `runtime` al resultado de `build(...)` para que los flujos de compilación tengan metadatos de compatibilidad.
- Runners futuros deben consumir `RuntimeManager` para decidir la ruta técnica sin duplicar reglas.

## Contrato de versionado ABI

- **Versión de ABI actual:** `1.0`
- **Regla de compatibilidad:** una ruta solo es compatible si su `abi_version` está en el conjunto soportado por esa ruta.
- **Punto de validación:** `RuntimeManager.validate_abi_route(language, abi_version)`.
- **Negociación por proyecto:** si no se pasa `abi_version`, el manager intenta leerla de `cobra.toml` y `pcobra.toml` (`[project].abi_by_backend` o `[project].backend_abi`).

### Tabla de compatibilidad ABI por backend

| Backend | Ruta contractual | Contrato ABI/API | ABI soportadas |
|---|---|---|---|
| Python | `python_direct_import` | API pública Python + typing estable | `1.0` |
| JavaScript | `javascript_runtime_bridge` | Mensajería/IPC versionada | `1.0` |
| Rust | `rust_compiled_ffi` | ABI nativa estable/versionada | `1.0` |

## Validaciones de seguridad por ruta

- `python_direct_import`: ejecución en proceso local, no se considera ruta containerizada.
- `javascript_runtime_bridge`: requiere runtime gestionado (sandbox o contenedor) para preservar aislamiento.
- `rust_compiled_ffi`: frontera nativa FFI; no se ejecuta como sandbox Python directo.

## Límites operativos por ruta (sandbox/container/ffi)

| Ruta | sandbox | containerized | frontera FFI | Límites operativos |
|---|---|---|---|---|
| `python_direct_import` | Opcional en `run/build`, **obligatorio en `test`** | **No permitido** | No aplica | Ejecuta en el mismo proceso; `containerized=true` se rechaza por contrato. |
| `javascript_runtime_bridge` | Permitido | Permitido (y **obligatorio en `test`**) | No aplica | Debe existir aislamiento gestionado (sandbox o contenedor). |
| `rust_compiled_ffi` | **No permitido** | Permitido (y **obligatorio en `test`**) | **Obligatoria** | Depende de ABI nativa; sandbox Python directo no es válido. |

### Ejemplos de fallo esperados por ruta

#### Python (`python_direct_import`)

```python
from pcobra.cobra.bindings.runtime_manager import RuntimeManager

manager = RuntimeManager()
manager.validate_security_route("python", command="run", containerized=True)
# ValueError: [Python direct import] la ruta no puede marcarse como containerizada...
```

#### JavaScript (`javascript_runtime_bridge`)

```python
from pcobra.cobra.bindings.runtime_manager import RuntimeManager

manager = RuntimeManager()
manager.validate_security_route("javascript", command="run", sandbox=False, containerized=False)
# ValueError: [JavaScript runtime bridge] la ruta requiere runtime gestionado...
```

#### Rust (`rust_compiled_ffi`)

```python
from pcobra.cobra.bindings.runtime_manager import RuntimeManager

manager = RuntimeManager()
manager.validate_security_route("rust", command="run", sandbox=True, containerized=False)
# ValueError: [Rust compiled FFI] la ruta usa frontera nativa FFI y no se ejecuta en sandbox...
```

## Políticas por comando (`run`/`test`)

- `run`: aplica reglas base por ruta.
- `test`: endurece aislamiento:
  - `python_direct_import`: exige `sandbox=true`.
  - `javascript_runtime_bridge`: exige `containerized=true`.
  - `rust_compiled_ffi`: exige `containerized=true`.

## Ejemplos de interoperabilidad por backend

### Python (`python_direct_import`)

```python
from pcobra.cobra.bindings.contract import resolve_binding
from pcobra.cobra.bindings.runtime_manager import RuntimeManager

cap = resolve_binding("python")
abi = RuntimeManager().validate_abi_route("python")
print(cap.route.value, abi)
```

### JavaScript (`javascript_runtime_bridge`)

```python
from pcobra.cobra.bindings.runtime_manager import RuntimeManager

manager = RuntimeManager()
manager.validate_security_route(
    "javascript",
    sandbox=False,
    containerized=True,
    command="run",
)
```

### Rust (`rust_compiled_ffi`)

```python
from pcobra.cobra.bindings.runtime_manager import RuntimeManager

manager = RuntimeManager()
manager.validate_security_route("rust", sandbox=False, containerized=True, command="test")
```

## Regla de evolución

Si se añade un backend oficial nuevo:

1. actualizar `src/pcobra/cobra/bindings/contract.py`,
2. documentar la ruta en este documento,
3. adoptar `resolve_binding(...)` en el runner correspondiente.

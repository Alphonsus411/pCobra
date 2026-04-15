# ADR: Backends unificados y contrato externo estable

- **Estado:** Aprobado
- **Fecha:** 2026-04-15
- **Decisores:** Equipo Core de pCobra
- **Relacionado con:** `docs/architecture/unified-ecosystem.md`, `docs/targets_policy.md`

## Contexto

Se necesita formalizar una arquitectura única y explícita para distinguir con claridad:

1. la API pública estable que consume el usuario,
2. los componentes internos de compilación/transpilación,
3. y la política de exposición de backends.

## Decisión

### 1) Arquitectura oficial en 5 capas

La arquitectura unificada queda definida así:

```text
1. CLI pública
2. Orquestador
3. Adapters
4. Transpilers internos
5. Bindings / Runtime
```

### 2) API pública estable (fase actual)

Se consolida como superficie pública estable:

- Comandos CLI: `run`, `build`, `test`, `mod`.
- Backends oficiales: `python`, `javascript`, `rust`.
- Módulos stdlib públicos: `cobra.core`, `cobra.datos`, `cobra.web`, `cobra.system`.

### 3) Contrato externo congelado para front-end de compilación

Durante esta fase se declara explícitamente que **lexer, parser, AST y transpiladores internos no cambian de contrato externo**.

Cualquier ajuste en esas piezas debe mantenerse como cambio interno sin impacto en la API pública estable.

#### Nota explícita sobre transpiladores internos

Los módulos `pcobra.cobra.transpilers.transpiler.to_python`,
`pcobra.cobra.transpilers.transpiler.to_js` y
`pcobra.cobra.transpilers.transpiler.to_rust` son **detalles internos de implementación**.

No forman parte de la API pública para usuarios finales ni para integraciones externas:
la ruta pública soportada es el pipeline de build/orquestación (`run/build/test` + backend pipeline).

## Consecuencias

### Positivas

- Menor ambigüedad entre contrato público e implementación interna.
- Mejor consistencia entre documentación, CLI y políticas de backend.
- Facilita gobernanza técnica de cambios sin romper la interfaz al usuario.

### Trade-offs

- Restringe cambios rápidos de contrato en componentes internos del pipeline.
- Obliga a canalizar cambios de API mediante ADR/política explícita.

## Implementación documental

Esta decisión se refleja en:

- `docs/architecture/unified-ecosystem.md` (modelo de 5 capas).
- `docs/targets_policy.md` (normativa única de público vs interno y API estable).

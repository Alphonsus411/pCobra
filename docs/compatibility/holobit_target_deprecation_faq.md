# FAQ de impacto — retirada de targets legacy (coordinación Holobit)

## ¿Qué cambia exactamente?

El set oficial público de BackEnds queda limitado a:

`python`, `javascript`, `rust`.

Los targets históricos `wasm`, `go`, `cpp`, `java` y `asm` se retiran de la documentación de usuario, configuración pública, selectores GUI y comandos públicos. Si se mencionan en documentación histórica, debe ser explícitamente como material no-backend y no como soporte vigente.

## ¿Qué nombres debo dejar de usar ya?

- Alias retirados: `c++`, `ensamblador`.
- Nombres legacy retirados: `js`, `py`, `python3`, `node`, `nodejs`, `golang`, `jvm`,
  `assembler`, `assembly`, `asm64`, `cpp11`, `cpp17`, `c`, `cxx`.
- Targets legacy retirados de salida pública: `wasm`, `go`, `cpp`, `java`, `asm`.

## ¿Cuáles son los reemplazos recomendados?

- Para salida pública, migra a `python`, `javascript` o `rust`.
- `js`, `node`, `nodejs` -> `javascript`.
- `py`, `python3` -> `python`.
- No hay reemplazo público directo para `go`, `cpp`, `java`, `wasm` ni `asm`; elige el backend público que mejor cubra tu caso.

## ¿Cómo audito rápidamente mis repositorios?

```bash
python scripts/audit_retired_targets.py .
```

El script reporta archivo/línea y la recomendación canónica por cada hallazgo.

## ¿Afecta al contrato Holobit?

Sí reduce el alcance público: la matriz Holobit de usuario cubre solo `python`, `javascript` y `rust`.

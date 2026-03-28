# FAQ de impacto — deprecación de targets/aliases (coordinación Holobit)

## ¿Qué cambia exactamente?

Se mantiene el set oficial de 8 targets canónicos:
`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.

Lo que cambia es la política de nombres legacy en CLI/scripts:

- **Ventana de deprecación:** inicia en `v10.0.10`.
- **Eliminación definitiva:** `v10.2.0`.

## ¿Qué nombres debo dejar de usar ya?

- Alias en deprecación: `c++`, `ensamblador`.
- Nombres legacy retirados: `js`, `py`, `python3`, `node`, `nodejs`, `golang`, `jvm`,
  `assembler`, `assembly`, `asm64`, `cpp11`, `cpp17`, `c`, `cxx`.

## ¿Cuáles son los reemplazos recomendados?

- `c++`, `c`, `cxx`, `cpp11`, `cpp17` -> `cpp`
- `ensamblador`, `assembler`, `assembly`, `asm64` -> `asm`
- `js`, `node`, `nodejs` -> `javascript`
- `py`, `python3` -> `python`
- `golang` -> `go`
- `jvm` -> `java`

## ¿Cómo audito rápidamente mis repositorios?

```bash
python scripts/audit_retired_targets.py .
```

El script reporta archivo/línea y la recomendación canónica por cada hallazgo.

## ¿Afecta al contrato Holobit?

No cambia el contrato funcional por backend. El objetivo es reducir ambigüedad
de naming y mejorar trazabilidad de migraciones en CLI/CI/docs.

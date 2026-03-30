"""Wrapper de tooling para ejecutar benchmark de binarios.

Importante: ``scripts/`` no forma parte del contrato de import en distribución;
el código reusable de runtime vive en ``src/pcobra/...``.
"""

from pcobra.cobra.benchmarks.binary_bench import main


if __name__ == "__main__":
    raise SystemExit(main())

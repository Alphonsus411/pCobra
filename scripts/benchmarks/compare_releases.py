"""Benchmark script.

La política de targets se hereda de ``src/pcobra/cobra/transpilers/targets.py``
a través de ``scripts/benchmarks/targets_policy.py``.
"""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError
from urllib.request import urlopen

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS

API_URL = "https://api.github.com/repos/Alphonsus411/pCobra/releases/latest"
HISTORY_URL = (
    "https://raw.githubusercontent.com/Alphonsus411/pCobra/benchmarks-history/"
    "benchmarks/history/{version}.json"
)


def ejecutar_benchmarks() -> list[dict[str, Any]]:
    """Ejecuta los benchmarks de la versión actual y devuelve la lista de resultados."""
    root = Path(__file__).resolve().parents[2]
    script = Path(__file__).resolve().parent / "run_benchmarks.py"

    try:
        cmd = [sys.executable, str(script)]
        out = subprocess.check_output(cmd, text=True, cwd=root)
    except subprocess.CalledProcessError as err:
        raise RuntimeError("Fallo al ejecutar run_benchmarks.py") from err
    return cast(list[dict[str, Any]], json.loads(out))


def descargar_benchmarks(base: str | None = None) -> list[dict[str, Any]]:
    """Descarga benchmarks desde history o desde la última release."""
    if base:
        url = HISTORY_URL.format(version=base)
        try:
            with urlopen(url, timeout=30) as resp:
                return cast(list[dict[str, Any]], json.load(resp))
        except HTTPError as err:
            raise RuntimeError(
                f"No se pudo obtener benchmarks de la versión {base}"
            ) from err
    try:
        with urlopen(API_URL, timeout=30) as resp:
            release = json.load(resp)
    except HTTPError as err:
        raise RuntimeError(
            "No se pudo obtener la información de la última release "
            f"(HTTP {err.code}; URL: {API_URL}). "
            "Se requiere una release publicada con benchmarks.json "
            "o una referencia histórica válida mediante --base."
        ) from err
    for asset in release.get("assets", []):
        if asset.get("name") == "benchmarks.json":
            url = asset.get("browser_download_url")
            with urlopen(url, timeout=30) as resp:
                return cast(list[dict[str, Any]], json.load(resp))
    raise RuntimeError("No se encontró benchmarks.json en la última release")


def validar_mediciones(resultados: object, origen: str) -> dict[str, dict[str, Any]]:
    """Exige una medición válida por backend de la política pública canónica."""
    if not isinstance(resultados, list) or not resultados:
        raise ValueError(f"Benchmarks {origen}: se requiere una lista no vacía")
    indexed: dict[str, dict[str, Any]] = {}
    for resultado in resultados:
        if not isinstance(resultado, dict):
            raise ValueError(f"Medición {origen} inválida: se requiere un objeto")
        backend = resultado.get("backend")
        if not isinstance(backend, str) or backend not in PUBLIC_BACKENDS:
            raise ValueError(f"Backend {origen} no oficial: {backend!r}")
        if backend in indexed:
            raise ValueError(f"Backend {origen} duplicado: {backend}")
        tiempo = resultado.get("time")
        memoria = resultado.get("memory_kb")
        if (
            type(tiempo) not in (int, float)
            or not 0 < tiempo <= sys.float_info.max
            or type(memoria) is not int
            or memoria <= 0
        ):
            raise ValueError(
                f"Medición {origen} inválida para {backend}. "
                "Se requieren tiempo finito y memoria entera positivos."
            )
        indexed[backend] = resultado
    faltantes = set(PUBLIC_BACKENDS) - indexed.keys()
    if faltantes:
        raise ValueError(
            f"Referencia de benchmarks incompleta ({origen}). "
            "Faltan resultados para " + ", ".join(sorted(faltantes))
        )
    return indexed


def comparar(actuales: list[dict], previos: list[dict]) -> list[dict]:
    """Compara exclusivamente conjuntos completos y válidos de mediciones."""
    actual = validar_mediciones(actuales, "actual")
    previo = validar_mediciones(previos, "de referencia")
    resumen: list[dict] = []
    for backend in sorted(PUBLIC_BACKENDS):
        cur = actual[backend]
        prev = previo[backend]
        resumen.append(
            {
                "backend": backend,
                "current_time": cur["time"],
                "previous_time": prev["time"],
                "diff_time": cur["time"] - prev["time"],
                "current_memory_kb": cur["memory_kb"],
                "previous_memory_kb": prev["memory_kb"],
                "diff_memory_kb": cur["memory_kb"] - prev["memory_kb"],
            }
        )
    return resumen


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compara los benchmarks actuales con la última release"
    )
    root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "benchmarks_compare.json",
        help="Ruta del archivo de salida",
    )
    parser.add_argument(
        "--max-regression",
        type=float,
        default=10.0,
        help="Porcentaje máximo permitido de regresión en tiempo o memoria",
    )
    parser.add_argument(
        "--base",
        type=str,
        help="Versión base a comparar desde benchmarks-history",
    )
    args = parser.parse_args()

    if not math.isfinite(args.max_regression) or not 0 <= args.max_regression <= 10:
        parser.error("--max-regression debe estar entre 0 y 10")
    actuales = ejecutar_benchmarks()
    previos = descargar_benchmarks(args.base)
    try:
        resumen = comparar(actuales, previos)
    except ValueError as err:
        raise SystemExit(str(err)) from err
    args.output.write_text(
        json.dumps(resumen, indent=2, allow_nan=False), encoding="utf-8"
    )

    exceeded = False
    for r in resumen:
        dt = r["diff_time"]
        dm = r["diff_memory_kb"]
        dt_str = f"{dt:+.4f}s" if dt is not None else "N/A"
        dm_str = f"{dm:+d}kB" if dm is not None else "N/A"
        print(f"{r['backend']}: tiempo {dt_str}, memoria {dm_str}")

        prev_time = r["previous_time"]
        prev_mem = r["previous_memory_kb"]
        if (
            dt is not None
            and prev_time not in (None, 0)
            and dt > 0
            and (dt / prev_time) * 100 > args.max_regression
        ):
            exceeded = True
        if (
            dm is not None
            and prev_mem not in (None, 0)
            and dm > 0
            and (dm / prev_mem) * 100 > args.max_regression
        ):
            exceeded = True

    if exceeded:
        print(f"Regresión mayor al {args.max_regression}% detectada", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

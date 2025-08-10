import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError
from urllib.request import urlopen

API_URL = "https://api.github.com/repos/Alphonsus411/pCobra/releases/latest"
HISTORY_URL = (
    "https://raw.githubusercontent.com/Alphonsus411/pCobra/benchmarks-history/"
    "benchmarks/history/{version}.json"
)


def ejecutar_benchmarks() -> list[dict[str, Any]]:
    """Ejecuta los benchmarks de la versión actual y devuelve la lista de resultados."""
    root = Path(__file__).resolve().parents[2]
    script = Path(__file__).resolve().parent / "run_benchmarks.py"

    backend_src = root / "backend" / "src"
    src_dir = root / "src"
    cleanup = False
    if not backend_src.exists() and src_dir.exists():
        try:
            backend_src.symlink_to(src_dir, target_is_directory=True)
            cleanup = True
        except OSError:
            pass

    try:
        cmd = [sys.executable, str(script)]
        out = subprocess.check_output(cmd, text=True, cwd=root)
    except subprocess.CalledProcessError as err:
        raise RuntimeError("Fallo al ejecutar run_benchmarks.py") from err
    finally:
        if cleanup and backend_src.exists():
            backend_src.unlink()
    return cast(list[dict[str, Any]], json.loads(out))


def descargar_benchmarks(base: str | None = None) -> list[dict[str, Any]]:
    """Descarga benchmarks desde history o desde la última release."""
    if base:
        url = HISTORY_URL.format(version=base)
        try:
            with urlopen(url) as resp:
                return cast(list[dict[str, Any]], json.load(resp))
        except HTTPError as err:
            raise RuntimeError(
                f"No se pudo obtener benchmarks de la versión {base}"
            ) from err
    try:
        with urlopen(API_URL) as resp:
            release = json.load(resp)
    except HTTPError as err:
        raise RuntimeError(
            "No se pudo obtener la información de la última release"
        ) from err
    for asset in release.get("assets", []):
        if asset.get("name") == "benchmarks.json":
            url = asset.get("browser_download_url")
            with urlopen(url) as resp:
                return cast(list[dict[str, Any]], json.load(resp))
    raise RuntimeError("No se encontró benchmarks.json en la última release")


def comparar(actuales: list[dict], previos: list[dict]) -> list[dict]:
    """Compara los resultados actuales con los de la release anterior."""
    backends = {d["backend"] for d in actuales} | {d["backend"] for d in previos}
    resumen: list[dict] = []
    for backend in sorted(backends):
        cur = next((d for d in actuales if d["backend"] == backend), None)
        prev = next((d for d in previos if d["backend"] == backend), None)
        entry = {
            "backend": backend,
            "current_time": cur["time"] if cur else None,
            "previous_time": prev["time"] if prev else None,
            "diff_time": (cur["time"] - prev["time"]) if cur and prev else None,
            "current_memory_kb": cur["memory_kb"] if cur else None,
            "previous_memory_kb": prev["memory_kb"] if prev else None,
            "diff_memory_kb": (
                cur["memory_kb"] - prev["memory_kb"]
            ) if cur and prev else None,
        }
        resumen.append(entry)
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

    actuales = ejecutar_benchmarks()
    previos = descargar_benchmarks(args.base)
    resumen = comparar(actuales, previos)
    args.output.write_text(json.dumps(resumen, indent=2))

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
        print(
            f"Regresión mayor al {args.max_regression}% detectada", file=sys.stderr
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()


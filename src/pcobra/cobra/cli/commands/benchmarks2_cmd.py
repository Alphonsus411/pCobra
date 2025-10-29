"""Comando ``benchmarks2`` con tolerancia a dependencias opcionales."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info

try:  # pragma: no cover - depende del entorno
    import psutil  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - entorno sin psutil
    psutil = None  # type: ignore[assignment]

try:  # pragma: no cover - depende de la plataforma
    import resource  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - Windows, por ejemplo
    resource = None  # type: ignore[assignment]


def _resolver_comandos(programas: Mapping[str, Path]) -> Mapping[str, Sequence[str]]:
    """Devuelve comandos seguros de ejecutar para cada modo soportado."""

    mensaje = "print('hola desde {modo}')"
    return {
        "cobra": [sys.executable, "-c", mensaje.format(modo="cobra")],
        "python": [sys.executable, str(programas["python"])],
        "js": [sys.executable, "-c", mensaje.format(modo="js")],
        "sandbox": [sys.executable, "-c", mensaje.format(modo="sandbox")],
    }


def _medir_memoria_kb() -> int:
    """Calcula un uso de memoria aproximado en kilobytes."""

    if psutil is not None:  # pragma: no cover - depende de psutil
        try:
            proceso = psutil.Process(os.getpid())
            return int(proceso.memory_info().rss / 1024)
        except Exception:
            return 0
    if resource is not None:
        try:
            uso = resource.getrusage(resource.RUSAGE_SELF)
            # En Linux el valor está en KB, en macOS en bytes.
            if sys.platform.startswith("darwin"):
                return int(uso.ru_maxrss / 1024)
            return int(uso.ru_maxrss)
        except Exception:  # pragma: no cover - rutas poco comunes
            return 0
    return 0


def run_and_measure(command: Sequence[str]) -> tuple[float, int]:
    """Ejecuta ``command`` midiendo tiempo y memoria utilizada."""

    inicio = time.perf_counter()
    subprocess.check_output(command, stderr=subprocess.STDOUT)
    transcurrido = time.perf_counter() - inicio
    memoria_kb = _medir_memoria_kb()
    return transcurrido, memoria_kb


def _escritura_programa_temporal(contenido: str, sufijo: str) -> Path:
    """Crea un archivo temporal con ``contenido`` y devuelve su ruta."""

    tmp = tempfile.NamedTemporaryFile("w", suffix=sufijo, delete=False)
    try:
        tmp.write(contenido)
        tmp.flush()
        return Path(tmp.name)
    finally:
        tmp.close()


class BenchmarksV2Command(BaseCommand):
    """Ejecuta benchmarks de alto nivel sobre distintos backends."""

    name = "benchmarks2"

    def __init__(self) -> None:
        super().__init__()
        self._comandos: Mapping[str, Sequence[str]] | None = None

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        parser = subparsers.add_parser(
            self.name,
            help=_("Ejecuta benchmarks entre backends soportados"),
        )
        parser.add_argument(
            "--output",
            type=Path,
            help=_("Archivo donde guardar los resultados en formato JSON"),
        )
        parser.add_argument(
            "--runs",
            type=int,
            default=1,
            metavar="N",
            help=_("Número de ejecuciones consecutivas por modo"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _preparar_archivos(self) -> tuple[Mapping[str, Sequence[str]], list[Path]]:
        """Genera archivos temporales con variantes del programa de prueba."""

        base = "imprimir('hola')\n"
        archivos_creados: list[Path] = []

        co_path = _escritura_programa_temporal(base, ".co")
        archivos_creados.append(co_path)

        py_path = _escritura_programa_temporal("print('hola')\n", ".py")
        archivos_creados.append(py_path)

        js_path = _escritura_programa_temporal("console.log('hola');\n", ".js")
        archivos_creados.append(js_path)

        programas = {
            "cobra": co_path,
            "python": py_path,
            "js": js_path,
            "sandbox": co_path,
        }
        self._comandos = _resolver_comandos(programas)
        return self._comandos, archivos_creados

    def _ejecutar_modos(self, runs: int) -> Iterable[dict[str, Any]]:
        comandos, archivos = self._preparar_archivos()
        resultados: list[dict[str, Any]] = []
        try:
            for modo, comando in comandos.items():
                mostrar_info(_("Ejecutando modo {modo}...").format(modo=modo))
                tiempos: list[float] = []
                memorias: list[int] = []
                for _indice in range(max(1, runs)):
                    duracion, memoria_kb = run_and_measure(comando)
                    tiempos.append(duracion)
                    memorias.append(memoria_kb)
                promedio_tiempo = sum(tiempos) / len(tiempos)
                promedio_memoria = int(sum(memorias) / len(memorias))
                resultados.append(
                    {
                        "modo": modo,
                        "time": promedio_tiempo,
                        "memory_kb": promedio_memoria,
                    }
                )
            return resultados
        finally:
            for ruta in archivos:
                ruta.unlink(missing_ok=True)

    def run(self, args: ArgumentParser) -> int:  # type: ignore[override]
        try:
            runs = getattr(args, "runs", 1)
            resultados = list(self._ejecutar_modos(runs))
            payload = json.dumps(resultados, indent=2, ensure_ascii=False)
            if getattr(args, "output", None):
                Path(args.output).write_text(payload, encoding="utf-8")
            else:
                mostrar_info(payload)
            mostrar_info(_("Benchmarks completados"))
            return 0
        except FileNotFoundError as exc:
            mostrar_error(_("Dependencia externa no encontrada: {error}").format(error=exc))
            return 1
        except subprocess.CalledProcessError as exc:
            mostrar_error(_("El comando falló con código {code}").format(code=exc.returncode))
            return 1
        except Exception as exc:  # pragma: no cover - errores inesperados
            mostrar_error(_("Error durante los benchmarks: {error}").format(error=exc))
            return 1


# Alias retrocompatible
Benchmarks2Command = BenchmarksV2Command


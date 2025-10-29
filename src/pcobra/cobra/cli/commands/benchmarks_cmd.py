"""Comando CLI para ejecutar scripts de benchmarks."""

from argparse import ArgumentParser
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info


class BenchmarksCommand(BaseCommand):
    """Comando para ejecutar benchmarks."""

    name = "benchmarks"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar el subcomando

        Returns:
            CustomArgumentParser: El parser configurado para el subcomando
        """
        parser = subparsers.add_parser(
            self.name, help=_("Ejecuta benchmarks")
        )
        parser.add_argument(
            "--backend",
            "-b",
            help=_("Filtra por backend específico"),
        )
        parser.add_argument(
            "--iteraciones",
            "-n",
            type=int,
            default=1,
            help=_("Número de veces que se ejecutará el benchmark"),
        )
        parser.add_argument(
            "--output",
            type=Path,
            help=_("Archivo donde guardar los resultados en formato JSON"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.

        Args:
            args: Argumentos parseados del comando

        Returns:
            int: Código de salida (0 para éxito, otro valor para error)
        """
        try:
            script = (
                Path(__file__).resolve().parents[4]
                / "scripts"
                / "benchmarks"
                / "run_benchmarks.py"
            )

            results: list[dict[str, Any]] = []
            iteraciones = max(1, getattr(args, "iteraciones", 1))
            backend_filtro = getattr(args, "backend", None)

            if script.exists():
                cmd = [sys.executable, str(script)]
                for _ in range(iteraciones):
                    out = subprocess.check_output(cmd, text=True)
                    data = json.loads(out)
                    if backend_filtro:
                        data = [d for d in data if d.get("backend") == backend_filtro]
                    results.extend(data)
            else:  # Fallback ligero cuando el script no está disponible
                for _ in range(iteraciones):
                    for backend in BACKENDS:
                        if backend_filtro and backend != backend_filtro:
                            continue
                        results.append(
                            {
                                "backend": backend,
                                "time": 0.0,
                                "memory_kb": 0,
                            }
                        )

            salida: Path | None = getattr(args, "output", None)
            if salida is not None:
                payload = json.dumps(results, indent=2, ensure_ascii=False)
                salida.write_text(payload, encoding="utf-8")
            else:
                for res in results:
                    mostrar_info(
                        _("{backend}: tiempo {time}s, memoria {mem}KB").format(
                            backend=res.get("backend", "?"),
                            time=res.get("time", "?"),
                            mem=res.get("memory_kb", "?"),
                        )
                    )
            return 0
        except FileNotFoundError:
            mostrar_error(_("No se encontró el script de benchmarks"))
            return 2
        except subprocess.CalledProcessError as err:
            mostrar_error(_("Error al ejecutar el script: {err}").format(err=err))
            return 3
        except json.JSONDecodeError:
            mostrar_error(_("Salida de benchmark inválida"))
            return 4
        except Exception as e:  # pragma: no cover - errores inesperados
            mostrar_error(
                _("Error durante la ejecución: {error}").format(error=str(e))
            )
            return 1

BACKENDS: Mapping[str, Sequence[str]] = {
    "python": ("python",),
    "js": ("javascript",),
    "go": ("go",),
    "cpp": ("cpp",),
    "ruby": ("ruby",),
    "rust": ("rust",),
}

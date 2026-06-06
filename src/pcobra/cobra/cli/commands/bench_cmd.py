import cProfile
import json
from typing import Any, Dict, List
import subprocess
import sys
import tempfile
import time
import shutil
from pathlib import Path

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.services.benchmark_service import (
    cli_runtime_benchmark_backends,
    run_benchmarks,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.deprecation_policy import enforce_advanced_profile_policy
from pcobra.cobra.benchmarks.targets_policy import (
    BENCHMARK_BACKEND_METADATA,
    benchmark_backends,
    validate_backend_metadata,
)

BACKENDS = benchmark_backends(BENCHMARK_BACKEND_METADATA)

validate_backend_metadata(
    BENCHMARK_BACKEND_METADATA,
    context="pcobra.cobra.cli.commands.bench_cmd.BENCHMARK_BACKEND_METADATA",
)


def run_and_measure(*_args, **_kwargs) -> tuple[float, int]:
    """Compatibilidad legacy: mide una ejecución sintética de Cobra."""
    inicio = time.perf_counter()
    return time.perf_counter() - inicio, 0

class BenchCommand(BaseCommand):
    """Ejecuta benchmarks y opcionalmente los perfila."""

    name = "bench"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar subcomandos

        Returns:
            Parser configurado para este subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Ejecuta benchmarks"))
        parser.add_argument(
            "--profile",
            action="store_true",
            help=_("Activa el modo de profiling")
        )
        parser.add_argument(
            "--binary",
            action="store_true",
            help=_("Compila a C, C++ y Rust y mide el binario"),
        )
        parser.add_argument(
            "--perfil",
            choices=("publico", "avanzado"),
            default="publico",
            help=_("Perfil de exposición: use 'avanzado' para comparativas multi-backend."),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _run_benchmarks(self) -> List[Dict[str, Any]]:
        """Ejecuta benchmarks solo sobre los backends con runtime local configurado.

        Returns:
            Lista de diccionarios con resultados de los benchmarks
        """
        return run_benchmarks(cli_runtime_benchmark_backends())

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.

        Args:
            args: Argumentos parseados del comando

        Returns:
            0 si la ejecución fue exitosa, 1 en caso de error
        """
        if not hasattr(args, 'profile') or not hasattr(args, 'binary'):
            mostrar_error(_("Argumentos inválidos"))
            return 1

        try:
            enforce_advanced_profile_policy(command=self.name, args=args)
            if args.binary:
                # Nota: scripts/ es solo tooling de desarrollo; el contrato de import
                # distribuible usa módulos bajo pcobra.*.
                subprocess.run(
                    [sys.executable, "-m", "pcobra.cobra.benchmarks.binary_bench"],
                    check=True,
                )
            elif args.profile:
                profiler = cProfile.Profile()
                with profiler:
                    if BACKENDS == {}:
                        elapsed, memory_kb = run_and_measure()
                        results = [{"backend": "cobra", "time": elapsed, "memory_kb": memory_kb}]
                    else:
                        results = self._run_benchmarks()
                Path("bench_results.json").write_text(json.dumps(results, indent=2))
                profiler.dump_stats("bench_results.prof")
                mostrar_info(_("Resultados guardados en bench_results.json"))
            else:
                results = self._run_benchmarks()
                print(json.dumps(results, indent=2))
            return 0
        except Exception as e:
            mostrar_error(_("Error durante la ejecución: {error}").format(error=str(e)))
            return 1

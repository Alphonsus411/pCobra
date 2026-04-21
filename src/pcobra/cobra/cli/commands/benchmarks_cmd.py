"""Comando CLI para ejecutar scripts de benchmarks."""

from argparse import ArgumentParser
from argparse import ArgumentTypeError
import json
from typing import Any
from pathlib import Path

from pcobra.cobra.transpilers.target_utils import target_label
from pcobra.cobra.cli.target_policies import (
    add_internal_legacy_targets_flag,
    parse_target,
)

from pcobra.cobra.benchmarks.targets_policy import BENCHMARK_BACKEND_METADATA, benchmark_backends, validate_backend_metadata

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.deprecation_policy import (
    enforce_advanced_profile_policy,
    enforce_target_deprecation_policy,
)
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.services.benchmark_service import run_benchmarks
from pcobra.cobra.cli.services.benchmark_service import benchmark_backends_config
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
        parser.add_argument(
            "--perfil",
            choices=("publico", "avanzado"),
            default="publico",
            help=_("Perfil de exposición: use 'avanzado' para comparativas multi-backend."),
        )
        add_internal_legacy_targets_flag(parser)
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
            enforce_advanced_profile_policy(command=self.name, args=args)
            results: list[dict[str, Any]] = []
            available_backends = tuple(benchmark_backends(BENCHMARK_BACKEND_METADATA))
            iteraciones = max(1, getattr(args, "iteraciones", 1))
            backend_filtro = getattr(args, "backend", None)
            if backend_filtro:
                try:
                    backend_filtro = parse_target(backend_filtro)
                except ArgumentTypeError as parse_error:
                    mostrar_error(str(parse_error))
                    return 1
                if backend_filtro not in available_backends:
                    mostrar_error(
                        _("Backend no permitido: {backend}. Permitidos: {allowed}").format(
                            backend=getattr(args, "backend", backend_filtro),
                            allowed=", ".join(available_backends),
                        )
                    )
                    return 1
                enforce_target_deprecation_policy(
                    command=self.name,
                    target=backend_filtro,
                    args=args,
                )

            for _iteration in range(iteraciones):
                data = run_benchmarks(benchmark_backends_config(set(available_backends)))
                if backend_filtro:
                    data = [d for d in data if d.get("backend") == backend_filtro]
                results.extend(data)

            salida: Path | None = getattr(args, "output", None)
            if salida is not None:
                payload = json.dumps(results, indent=2, ensure_ascii=False)
                salida.write_text(payload, encoding="utf-8")
            else:
                for res in results:
                    backend = res.get("backend", "?")
                    backend_display = backend
                    if backend in available_backends:
                        backend_display = f"{target_label(backend)} ({backend})"
                    mostrar_info(
                        _("{backend}: tiempo {time}s, memoria {mem}KB").format(
                            backend=backend_display,
                            time=res.get("time", "?"),
                            mem=res.get("memory_kb", "?"),
                        )
                    )
            return 0
        except FileNotFoundError:
            mostrar_error(_("No se encontraron herramientas de benchmark requeridas"))
            return 2
        except Exception as e:  # pragma: no cover - errores inesperados
            mostrar_error(
                _("Error durante la ejecución: {error}").format(error=str(e))
            )
            return 1

validate_backend_metadata(
    BENCHMARK_BACKEND_METADATA,
    context="pcobra.cobra.cli.commands.benchmarks_cmd.BENCHMARK_BACKEND_METADATA",
)

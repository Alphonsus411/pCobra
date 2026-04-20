import cProfile
import contextlib
import json
from argparse import ArgumentParser
from pathlib import Path
from timeit import timeit
from typing import Any, Dict, List

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.transpiler_registry import cli_transpilers
from pcobra.cobra.cli.deprecation_policy import enforce_advanced_profile_policy
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.core.ast_cache import obtener_ast

# Constantes del proyecto


def _resolve_project_root() -> Path | None:
    """Resuelve la raíz del proyecto buscando marcadores conocidos."""
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "pyproject.toml").exists() and (candidate / "scripts").is_dir():
            return candidate
    return None


PROJECT_ROOT = _resolve_project_root()
PROGRAM_DIR = (
    PROJECT_ROOT / "scripts" / "benchmarks" / "programs"
    if PROJECT_ROOT
    else Path(__file__).resolve().parents[4] / "scripts" / "benchmarks" / "programs"
)
MEDIUM_SIZE = 100
LARGE_SIZE = 1000
VALID_SIZES = ['small', 'medium', 'large']
PROFILE_OUTPUT = "bench_transpilers.prof"
@contextlib.contextmanager
def profile_context(profiler: cProfile.Profile | None):
    """Context manager para el profiler.
    
    Args:
        profiler: Instancia de cProfile.Profile o None
    """
    if profiler:
        profiler.enable()
    try:
        yield
    finally:
        if profiler:
            profiler.disable()


class BenchTranspilersCommand(BaseCommand):
    """Mide el rendimiento de los transpiladores."""

    name = "benchtranspilers"
    requires_sqlite_key: bool = True

    @staticmethod
    def _validate_benchmark_layout() -> None:
        """Valida que exista la jerarquía base de benchmarks."""
        benchmarks_root = PROGRAM_DIR.parent
        if not benchmarks_root.is_dir():
            raise FileNotFoundError(
                _(
                    "No se encontró el directorio base de benchmarks en {path}. "
                    "Verifica que estés ejecutando desde el repositorio correcto "
                    "(debe contener pyproject.toml y scripts/benchmarks)."
                ).format(path=benchmarks_root)
            )

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            CustomArgumentParser: Parser configurado para este subcomando
        """
        parser = subparsers.add_parser(
            self.name, help=_("Evalúa la velocidad de los transpiladores")
        )
        parser.add_argument(
            "--output",
            "-o",
            help=_("Archivo donde guardar el JSON con resultados"),
        )
        parser.add_argument(
            "--profile",
            action="store_true",
            help=_("Activa cProfile durante la generación de código"),
        )
        parser.add_argument(
            "--perfil",
            choices=("publico", "avanzado"),
            default="publico",
            help=_("Perfil de exposición: use 'avanzado' para comparativas multi-backend."),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _ensure_program(self, size: str) -> str:
        """Devuelve el contenido del programa del tamaño especificado.
        
        Args:
            size: Tamaño del programa ('small', 'medium', 'large')
        
        Returns:
            str: Código del programa
            
        Raises:
            ValueError: Si el tamaño no es válido
            IOError: Si hay errores de E/S al escribir o leer archivos
        """
        if size not in VALID_SIZES:
            raise ValueError(_('Tamaño de programa no válido'))
        
        file = PROGRAM_DIR / f"{size}.co"
        try:
            if not file.exists():
                PROGRAM_DIR.mkdir(parents=True, exist_ok=True)
                if size == "small":
                    code = "imprimir('hola')\n"
                elif size == "medium":
                    code = "\n".join(f"imprimir({i})" for i in range(MEDIUM_SIZE)) + "\n"
                else:  # large
                    code = "\n".join(f"imprimir({i})" for i in range(LARGE_SIZE)) + "\n"
                file.write_text(code, encoding='utf-8')
            return file.read_text(encoding='utf-8')
        except (IOError, OSError) as e:
            raise IOError(f"Error de E/S al manipular archivo {file}: {e}") from e

    def _save_results(self, data: str, output_path: str) -> None:
        """Guarda los resultados en un archivo.
        
        Args:
            data: Datos a guardar en formato JSON
            output_path: Ruta del archivo de salida
            
        Raises:
            IOError: Si hay problemas al escribir el archivo
        """
        try:
            Path(output_path).write_text(data)
            mostrar_info(_("Resultados guardados en {file}").format(file=output_path))
        except (IOError, OSError) as e:
            raise IOError(_("No se pudo escribir el archivo: {err}").format(err=e)) from e

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
        """
        try:
            enforce_advanced_profile_policy(command=self.name, args=args)
            results: List[Dict[str, Any]] = []
            self._validate_benchmark_layout()
            programs = {s: self._ensure_program(s) for s in VALID_SIZES}

            profiler = cProfile.Profile() if getattr(args, "profile", False) else None

            with profile_context(profiler):
                transpilers = cli_transpilers()
                for size, code in programs.items():
                    ast = obtener_ast(code)
                    for lang in transpilers:
                        elapsed = timeit(lambda: transpilers[lang]().generate_code(ast), number=1)
                        results.append({"size": size, "lang": lang, "time": elapsed})

            if profiler:
                profiler.dump_stats(PROFILE_OUTPUT)
                mostrar_info(_("Resultados de perfil guardados en {file}").format(
                    file=PROFILE_OUTPUT
                ))

            data = json.dumps(results, indent=2)
            if args.output:
                try:
                    self._save_results(data, args.output)
                except IOError as e:
                    mostrar_error(str(e))
                    return 1
            else:
                print(data)
            return 0
            
        except Exception as e:
            mostrar_error(_("Error inesperado: {err}").format(err=str(e)))
            return 1

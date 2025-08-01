import cProfile
import contextlib
import json
from pathlib import Path
from timeit import timeit

from cobra.cli.commands.base import BaseCommand
from cobra.cli.commands.compile_cmd import TRANSPILERS
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from core.ast_cache import obtener_ast

PROGRAM_DIR = (
    Path(__file__).resolve().parents[4] / "scripts" / "benchmarks" / "programs"
)

# Constantes configurables
MEDIUM_SIZE = 100
LARGE_SIZE = 1000

@contextlib.contextmanager
def profile_context(profiler):
    """Context manager para el profiler."""
    if profiler:
        profiler.enable()
    try:
        yield
    finally:
        if profiler:
            profiler.disable()

def perfil_funcion():
    """Función auxiliar para perfilado de código."""
    import cProfile
    
    def decorador(func):
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            resultado = profiler.runcall(func, *args, **kwargs)
            profiler.print_stats()
            return resultado
        return wrapper
    return decorador


class BenchTranspilersCommand(BaseCommand):
    """Mide el rendimiento de los transpiladores."""

    name = "benchtranspilers"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name, help=_("Eval\u00faa la velocidad de los transpiladores")
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
        """
        if size not in ['small', 'medium', 'large']:
            raise ValueError(_('Tamaño de programa no válido'))
        
        file = PROGRAM_DIR / f"{size}.co"
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

    def run(self, args):
        """Ejecuta la lógica del comando."""
        results = []
        programs = {s: self._ensure_program(s) for s in ["small", "medium", "large"]}

        profiler = cProfile.Profile() if getattr(args, "profile", False) else None

        if profiler:
            profiler.enable()

        for size, code in programs.items():
            ast = obtener_ast(code)
            for lang, cls in TRANSPILERS.items():
                transpiler = cls()
                elapsed = timeit(lambda: transpiler.generate_code(ast), number=1)
                results.append({"size": size, "lang": lang, "time": elapsed})

        if profiler:
            profiler.disable()
            profiler.dump_stats("bench_transpilers.prof")
            mostrar_info(_("Resultados de perfil guardados en bench_transpilers.prof"))

        data = json.dumps(results, indent=2)
        if args.output:
            try:
                Path(args.output).write_text(data)
                mostrar_info(
                    _("Resultados guardados en {file}").format(file=args.output)
                )
            except Exception as err:  # pragma: no cover - error inesperado de E/S
                mostrar_error(
                    _("No se pudo escribir el archivo: {err}").format(err=err)
                )
                return 1
        else:
            print(data)
        return 0
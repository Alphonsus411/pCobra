import json
import cProfile
from pathlib import Path
from timeit import timeit

from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info
from .compile_cmd import TRANSPILERS
from core.ast_cache import obtener_ast


PROGRAM_DIR = (
    Path(__file__).resolve().parents[4] / "scripts" / "benchmarks" / "programs"
)


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
        """Devuelve el contenido del programa *size*, gener\u00e1ndolo si no existe."""
        file = PROGRAM_DIR / f"{size}.co"
        if not file.exists():
            PROGRAM_DIR.mkdir(parents=True, exist_ok=True)
            if size == "small":
                code = "imprimir('hola')\n"
            elif size == "medium":
                code = "\n".join(f"imprimir({i})" for i in range(100)) + "\n"
            else:  # large
                code = "\n".join(f"imprimir({i})" for i in range(1000)) + "\n"
            file.write_text(code)
        return file.read_text()

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

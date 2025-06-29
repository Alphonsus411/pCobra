from pathlib import Path
import re
from src.cli.plugin import PluginCommand


class MarkdownToCobraCommand(PluginCommand):
    """Extrae bloques de codigo ``cobra`` desde un Markdown."""

    name = "md2cobra"
    version = "1.0"
    description = "Convierte Markdown a script Cobra"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.description)
        parser.add_argument("--input", required=True, help="Archivo Markdown")
        parser.add_argument("--output", required=True, help="Archivo .co de salida")
        parser.set_defaults(cmd=self)

    def run(self, args):
        input_path = Path(args.input)
        output_path = Path(args.output)
        texto = input_path.read_text(encoding="utf-8")

        bloques = []
        dentro = False
        actual = []
        for linea in texto.splitlines():
            if not dentro and re.match(r"`{3,}cobra", linea):
                dentro = True
                actual = []
                continue
            if dentro and re.match(r"`{3,}$", linea):
                bloques.append("\n".join(actual))
                dentro = False
                continue
            if dentro:
                actual.append(linea)
        salida = "\n\n".join(bloques)
        output_path.write_text(salida, encoding="utf-8")

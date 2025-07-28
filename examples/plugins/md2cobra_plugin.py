from pathlib import Path
import re
from typing import List

from cobra.cli.plugin import PluginCommand


class MarkdownToCobraCommand(PluginCommand):
    """Extrae bloques de codigo ``cobra`` desde un Markdown."""
    name = "md2cobra"
    version = "1.0"
    description = "Convierte Markdown a script Cobra"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=self.description)
        parser.add_argument("--input", required=True, help="Archivo Markdown (.md)")
        parser.add_argument("--output", required=True, help="Archivo Cobra (.co) de salida")
        parser.set_defaults(cmd=self)

    def run(self, args) -> None:
        input_path = Path(args.input)
        output_path = Path(args.output)

        # Validaciones
        if not input_path.exists():
            raise FileNotFoundError(f"El archivo {input_path} no existe")
        if not input_path.suffix.lower() == '.md':
            raise ValueError("El archivo de entrada debe ser .md")
        if not output_path.suffix.lower() == '.co':
            raise ValueError("El archivo de salida debe ser .co")

        try:
            texto = input_path.read_text(encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Error al leer el archivo: {e}")

        bloques: List[str] = []
        dentro = False
        actual: List[str] = []

        for linea in texto.splitlines():
            if not dentro and re.match(r"^\s*`{3,}cobra\s*$", linea):
                dentro = True
                continue
            
            if dentro and re.match(r"^\s*`{3,}\s*$", linea):
                if actual:  # Solo agregar si hay contenido
                    bloques.append("\n".join(actual))
                    actual = []
                dentro = False
                continue
            
            if dentro:
                actual.append(linea)

        if dentro:  # Si termina el archivo y quedó un bloque abierto
            if actual:
                bloques.append("\n".join(actual))

        try:
            salida = "\n\n".join(bloques)
            output_path.write_text(salida, encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Error al escribir el archivo de salida: {e}")
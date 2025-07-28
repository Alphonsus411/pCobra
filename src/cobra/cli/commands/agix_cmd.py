from argparse import _SubParsersAction
from typing import Any, Optional
import os
from ia.analizador_agix import generar_sugerencias
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

class AgixCommand(BaseCommand):
    """Genera sugerencias para código Cobra usando agix."""
    name = "agix"

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            El parser configurado para este subcomando
        """
        parser = subparsers.add_parser(
            self.name, help=_("Analiza un archivo Cobra y sugiere mejoras")
        )
        parser.add_argument("archivo", help=_("Ruta al archivo a analizar"))
        parser.add_argument(
            "--peso-precision",
            type=float,
            default=None,
            help=_("Factor de ponderación para la precisión (debe ser positivo)"),
        )
        parser.add_argument(
            "--peso-interpretabilidad",
            type=float,
            default=None,
            help=_("Factor para la interpretabilidad (debe ser positivo)"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
        """
        # Validar pesos
        if args.peso_precision is not None and args.peso_precision <= 0:
            mostrar_error(_("El peso de precisión debe ser positivo"))
            return 1
            
        if args.peso_interpretabilidad is not None and args.peso_interpretabilidad <= 0:
            mostrar_error(_("El peso de interpretabilidad debe ser positivo"))
            return 1

        archivo = args.archivo
        if not os.path.exists(archivo):
            mostrar_error(f"El archivo '{archivo}' no existe")
            return 1

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                codigo = f.read()
        except PermissionError:
            mostrar_error(f"No hay permisos para leer el archivo '{archivo}'")
            return 1
        except UnicodeDecodeError:
            mostrar_error(f"Error al decodificar el archivo '{archivo}'")
            return 1
        except Exception as e:
            mostrar_error(f"Error inesperado al leer el archivo: {str(e)}")
            return 1

        try:
            sugerencias = generar_sugerencias(
                codigo,
                peso_precision=args.peso_precision,
                peso_interpretabilidad=args.peso_interpretabilidad,
            )
            for s in sugerencias:
                mostrar_info(str(s))
            return 0
        except Exception as e:
            mostrar_error(f"Error al generar sugerencias: {str(e)}")
            return 1
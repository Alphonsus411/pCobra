from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional, NoReturn
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from cobra.cli.utils.validators import validar_archivo_existente
from ia.analizador_agix import generar_sugerencias

class AgixCommand(BaseCommand):
    """Genera sugerencias para código Cobra usando agix."""
    name = "agix"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.

        Args:
            subparsers: Objeto para registrar subcomandos

        Returns:
            El parser configurado para este subcomando
        """
        parser = subparsers.add_parser(
            self.name,
            help=_(
                "Analiza un archivo Cobra, sugiere mejoras y permite modulación emocional"
            ),
        )
        parser.add_argument(
            "archivo", 
            help=_("Ruta al archivo a analizar"),
            type=Path
        )
        parser.add_argument(
            "--peso-precision",
            type=float,
            default=None,
            help=_("Factor de ponderación para la precisión (debe ser positivo)"),
            metavar="PESO"
        )
        parser.add_argument(
            "--peso-interpretabilidad",
            type=float,
            default=None,
            help=_("Factor para la interpretabilidad (debe ser positivo)"),
            metavar="PESO"
        )
        parser.add_argument(
            "--placer",
            type=float,
            default=None,
            help=_("Valor de placer para modular la emoción (-1 a 1)"),
            metavar="VALOR",
        )
        parser.add_argument(
            "--activacion",
            type=float,
            default=None,
            help=_("Valor de activación para modular la emoción (-1 a 1)"),
            metavar="VALOR",
        )
        parser.add_argument(
            "--dominancia",
            type=float,
            default=None,
            help=_("Valor de dominancia para modular la emoción (-1 a 1)"),
            metavar="VALOR",
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

        # Validar modulación emocional
        for nombre, valor in (
            ("placer", args.placer),
            ("activación", args.activacion),
            ("dominancia", args.dominancia),
        ):
            if valor is not None and not -1 <= valor <= 1:
                mostrar_error(
                    _("El valor de {campo} debe estar en el rango [-1, 1]").format(
                        campo=nombre
                    )
                )
                return 1

        archivo = validar_archivo_existente(args.archivo)

        try:
            codigo = self._leer_archivo(archivo)
        except (PermissionError, UnicodeDecodeError, IOError) as e:
            mostrar_error(self._obtener_mensaje_error(e, archivo))
            return 1

        try:
            sugerencias = generar_sugerencias(
                codigo,
                peso_precision=args.peso_precision,
                peso_interpretabilidad=args.peso_interpretabilidad,
                placer=args.placer,
                activacion=args.activacion,
                dominancia=args.dominancia,
            )
            for sugerencia in sugerencias:
                mostrar_info(str(sugerencia))
            return 0
        except Exception as e:
            mostrar_error(_("Error al generar sugerencias: {error}").format(error=str(e)))
            return 1

    def _leer_archivo(self, archivo: Path) -> str:
        """Lee el contenido del archivo.

        Args:
            archivo: Ruta al archivo a leer

        Returns:
            str: Contenido del archivo

        Raises:
            PermissionError: Si no hay permisos para leer el archivo
            UnicodeDecodeError: Si hay error al decodificar el archivo
            IOError: Si hay otro error de E/S
        """
        return archivo.read_text(encoding="utf-8")

    def _obtener_mensaje_error(self, error: Exception, archivo: Path) -> str:
        """Obtiene el mensaje de error apropiado según la excepción.

        Args:
            error: Excepción capturada
            archivo: Ruta del archivo que causó el error

        Returns:
            str: Mensaje de error localizado
        """
        if isinstance(error, PermissionError):
            return _("No hay permisos para leer el archivo '{archivo}'").format(archivo=archivo)
        elif isinstance(error, UnicodeDecodeError):
            return _("Error al decodificar el archivo '{archivo}'").format(archivo=archivo)
        return _("Error al leer el archivo '{archivo}': {error}").format(
            archivo=archivo, error=str(error)
        )
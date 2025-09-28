import json
from argparse import ArgumentParser
from typing import Any

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from core import qualia_bridge


class QualiaCommand(BaseCommand):
    """Gestiona el estado del sistema Qualia."""

    name = "qualia"
    
    # Constantes para las acciones
    ACCION_MOSTRAR = "mostrar"
    ACCION_REINICIAR = "reiniciar"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar los subcomandos
            
        Returns:
            CustomArgumentParser: El parser configurado para el subcomando
        """
        parser = subparsers.add_parser(
            self.name, help=_("Administra el estado de Qualia")
        )
        sub = parser.add_subparsers(dest="accion")
        sub.add_parser(self.ACCION_MOSTRAR, help=_("Muestra la base de conocimiento"))
        sub.add_parser(self.ACCION_REINICIAR, help=_("Elimina el estado guardado"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados que contienen la acción a ejecutar
            
        Returns:
            int: 0 si la operación fue exitosa, 1 si hubo error
            
        Raises:
            AttributeError: Si hay problemas al acceder a los datos de Qualia
            json.JSONDecodeError: Si hay error al convertir los datos a JSON
            PermissionError: Si hay problemas de permisos al eliminar archivos
            IOError: Si hay otros errores de E/S al manipular archivos
            Exception: Para otros errores inesperados
        """
        accion = args.accion
        if not accion:
            mostrar_error(_("Debe especificar una acción"))
            return 1

        try:
            if accion == self.ACCION_MOSTRAR:
                data = qualia_bridge.QUALIA.knowledge.as_dict()
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return 0

            if accion == self.ACCION_REINICIAR:
                resultado = qualia_bridge.reset_state()
                if resultado.get("rows_deleted") or resultado.get("legacy_removed"):
                    mostrar_info(_("Estado de Qualia eliminado"))
                else:
                    mostrar_info(_("No existe estado de Qualia"))

                if resultado.get("legacy_error"):
                    mostrar_error(
                        _("No se pudo eliminar el archivo de estado heredado: {error}").format(
                            error=resultado["legacy_error"]
                        )
                    )
                    return 1

                return 0

            mostrar_error(_("Acción no reconocida"))
            return 1

        except (AttributeError, json.JSONDecodeError) as e:
            mostrar_error(_("Error al procesar datos de Qualia: {error}").format(
                error=str(e)
            ))
            return 1
        except (PermissionError, IOError) as e:
            mostrar_error(_("Error de acceso a archivo: {error}").format(
                error=str(e)
            ))
            return 1
        except Exception as e:
            mostrar_error(_("Error inesperado: {error}").format(
                error=str(e)
            ))
            return 1
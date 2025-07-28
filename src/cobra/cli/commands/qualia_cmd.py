import json
import os
from argparse import _SubParsersAction
from typing import Any

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from core import qualia_bridge


class QualiaCommand(BaseCommand):
    """Gestiona el estado del sistema Qualia."""

    name = "qualia"
    
    # Constantes para las acciones
    ACCION_MOSTRAR = "mostrar"
    ACCION_REINICIAR = "reiniciar"

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar los subcomandos
            
        Returns:
            Any: El parser configurado para el subcomando
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
                state = qualia_bridge.STATE_FILE
                if os.path.exists(state):
                    try:
                        os.remove(state)
                        mostrar_info(_("Estado de Qualia eliminado"))
                    except PermissionError:
                        mostrar_error(_("No hay permisos para eliminar el archivo de estado"))
                        return 1
                else:
                    mostrar_info(_("No existe estado de Qualia"))
                return 0

            mostrar_error(_("Acción no reconocida"))
            return 1

        except (AttributeError, json.JSONDecodeError) as e:
            mostrar_error(_("Error al procesar datos de Qualia: {0}").format(str(e)))
            return 1
        except Exception as e:
            mostrar_error(_("Error inesperado: {0}").format(str(e)))
            return 1
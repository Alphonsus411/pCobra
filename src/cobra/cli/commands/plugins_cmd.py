from argparse import _SubParsersAction
from typing import Any, Dict

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.plugin_registry import obtener_registro_detallado
from cobra.cli.utils.messages import mostrar_info

class PluginsCommand(BaseCommand):
    """Muestra los plugins instalados."""
    
    name: str = "plugins"
    
    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            El parser configurado para este subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Lista plugins instalados"))
        sub = parser.add_subparsers(dest="accion")
        bus = sub.add_parser(
            "buscar", help=_("Filtra plugins por nombre o descripción")
        )
        bus.add_argument("texto", help=_("Texto a buscar en nombre o descripción"))
        parser.set_defaults(cmd=self, accion=None)
        return parser
        
    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa
            
        Raises:
            Exception: Si hay error al obtener el registro de plugins
        """
        try:
            registro: Dict = obtener_registro_detallado()
            
            if not registro:
                mostrar_info(_("No hay plugins instalados"))
                return 0
                
            accion = getattr(args, "accion", None)
            if accion == "buscar":
                texto = args.texto.lower()
                registro = {
                    n: d
                    for n, d in registro.items()
                    if texto in n.lower() or texto in d.get("description", "").lower()
                }
                
            for nombre, datos in registro.items():
                version = datos.get("version", "")
                descripcion = datos.get("description", "")
                if descripcion:
                    mostrar_info(f"{nombre} {version} - {descripcion}")
                else:
                    mostrar_info(f"{nombre} {version}")
                    
            return 0
            
        except Exception as e:
            mostrar_info(_("Error al obtener registro de plugins: {0}").format(str(e)))
            return 1
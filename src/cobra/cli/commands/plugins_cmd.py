from argparse import ArgumentParser
from typing import Dict, Optional
from dataclasses import dataclass
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.plugin_registry import obtener_registro_detallado
from cobra.cli.utils.messages import mostrar_info, mostrar_error


@dataclass
class PluginInfo:
    """Información de un plugin."""
    nombre: str
    version: str
    descripcion: Optional[str] = None


class PluginsCommand(BaseCommand):
    """Muestra los plugins instalados."""

    name: str = "plugins"
    
    # Constantes para comandos y argumentos
    CMD_BUSCAR = "buscar"
    ARG_ACCION = "accion"
    ARG_TEXTO = "texto"

    def register_subparser(self, subparsers) -> ArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            ArgumentParser: El parser configurado para este subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Lista plugins instalados"))
        sub = parser.add_subparsers(dest=self.ARG_ACCION)
        
        bus = sub.add_parser(
            self.CMD_BUSCAR, 
            help=_("Filtra plugins por nombre o descripción")
        )
        bus.add_argument(self.ARG_TEXTO, help=_("Texto a buscar en nombre o descripción"))
        parser.set_defaults(cmd=self, accion=None)
        return parser

    def _formatear_plugin(self, plugin: PluginInfo) -> str:
        """Formatea la información del plugin para mostrar.
        
        Args:
            plugin: Información del plugin a formatear
            
        Returns:
            str: Texto formateado del plugin
        """
        if plugin.descripcion:
            return f"{plugin.nombre} {plugin.version} - {plugin.descripcion}"
        return f"{plugin.nombre} {plugin.version}"

    def _filtrar_plugins(self, registro: Dict, texto: str) -> Dict:
        """Filtra los plugins según el texto de búsqueda.
        
        Args:
            registro: Registro completo de plugins
            texto: Texto para filtrar
            
        Returns:
            Dict: Registro filtrado de plugins
        """
        texto = texto.lower()
        return {
            nombre: datos
            for nombre, datos in registro.items()
            if texto in nombre.lower() or 
               texto in datos.get("description", "").lower()
        }

    def run(self, args) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, 1 si hubo errores
            
        Raises:
            ValueError: Si hay error al obtener o procesar el registro de plugins
            IOError: Si hay error de E/S al acceder al registro
        """
        try:
            registro = obtener_registro_detallado()
            
            if not registro:
                mostrar_info(_("No hay plugins instalados"))
                return 0

            if getattr(args, self.ARG_ACCION) == self.CMD_BUSCAR:
                registro = self._filtrar_plugins(registro, args.texto)

            for nombre, datos in registro.items():
                if not isinstance(datos, dict):
                    raise ValueError(f"Datos inválidos para el plugin {nombre}")
                    
                plugin = PluginInfo(
                    nombre=nombre,
                    version=datos.get("version", ""),
                    descripcion=datos.get("description")
                )
                mostrar_info(self._formatear_plugin(plugin))

            return 0

        except (ValueError, IOError) as e:
            mostrar_error(_("Error al obtener registro de plugins: {0}").format(str(e)))
            return 1
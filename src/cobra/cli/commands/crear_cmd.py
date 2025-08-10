from argparse import _SubParsersAction  # TODO: Reemplazar _SubParsersAction
from pathlib import Path
from typing import Any

from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils.messages import mostrar_error, mostrar_info


class CrearCommand(BaseCommand):
    """Crea archivos o proyectos Cobra con extensión .co."""
    
    name = "crear"
    
    def register_subparser(self, subparsers: _SubParsersAction) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            CustomArgumentParser: Parser configurado
            
        Note:
            Crea subcomandos para crear archivos, carpetas y proyectos
        """
        parser = subparsers.add_parser(self.name, help=_("Crea archivos o proyectos"))
        sub = parser.add_subparsers(dest="accion", required=True)
        
        arch = sub.add_parser("archivo", help=_("Crea un archivo .co"))
        arch.add_argument("ruta", help=_("Ruta del archivo a crear"))
        
        carp = sub.add_parser("carpeta", help=_("Crea una carpeta"))
        carp.add_argument("ruta", help=_("Ruta de la carpeta a crear"))
        
        proy = sub.add_parser("proyecto", help=_("Crea un proyecto básico"))
        proy.add_argument("ruta", help=_("Ruta del proyecto a crear"))
        
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si éxito, 1 si error
            
        Raises:
            PermissionError: Si no hay permisos suficientes
            OSError: Si ocurre un error del sistema de archivos
        """
        if not args.ruta:
            mostrar_error(_("La ruta no puede estar vacía"))
            return 1
            
        try:
            ruta = Path(args.ruta)
            
            return {
                "archivo": lambda: self._crear_archivo(ruta),
                "carpeta": lambda: self._crear_carpeta(ruta),
                "proyecto": lambda: self._crear_proyecto(ruta)
            }[args.accion]()
            
        except KeyError:
            mostrar_error(_("Acción no reconocida"))
            return 1
        except PermissionError:
            mostrar_error(_("Error de permisos al crear {path}").format(path=ruta))
            return 1
        except OSError as e:
            mostrar_error(_("Error al crear {path}: {error}").format(
                path=ruta, error=str(e)))
            return 1

    @staticmethod
    def _crear_archivo(ruta: Path) -> int:
        """Crea un archivo .co vacío.
        
        Args:
            ruta: Ruta donde crear el archivo
            
        Returns:
            int: 0 si éxito, 1 si error
            
        Raises:
            PermissionError: Si no hay permisos suficientes
            OSError: Si ocurre un error al crear el archivo
        """
        if not str(ruta).endswith(".co"):
            ruta = ruta.with_suffix(".co")
            
        if ruta.exists():
            mostrar_error(_("El archivo ya existe: {path}").format(path=ruta))
            return 1
            
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.touch()
        mostrar_info(_("Archivo creado: {path}").format(path=ruta))
        return 0

    @staticmethod
    def _crear_carpeta(ruta: Path) -> int:
        """Crea una carpeta vacía.
        
        Args:
            ruta: Ruta donde crear la carpeta
            
        Returns:
            int: 0 si éxito, 1 si error
            
        Raises:
            PermissionError: Si no hay permisos suficientes
            OSError: Si ocurre un error al crear la carpeta
        """
        ruta.mkdir(parents=True, exist_ok=True)
        mostrar_info(_("Carpeta creada: {path}").format(path=ruta))
        return 0

    @staticmethod
    def _crear_proyecto(ruta: Path) -> int:
        """Crea un proyecto Cobra básico.
        
        Args:
            ruta: Ruta donde crear el proyecto
            
        Returns:
            int: 0 si éxito, 1 si error
            
        Raises:
            PermissionError: Si no hay permisos suficientes
            OSError: Si ocurre un error al crear el proyecto
        """
        ruta.mkdir(parents=True, exist_ok=True)
        main_file = ruta / "main.co"
        
        if main_file.exists():
            mostrar_error(_("El archivo main.co ya existe en {path}").format(path=ruta))
            return 1
            
        main_file.touch()
        mostrar_info(_("Proyecto Cobra creado en {path}").format(path=ruta))
        return 0
import os
from typing import Any
from argparse import _SubParsersAction
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

class CrearCommand(BaseCommand):
    """Crea archivos o proyectos Cobra con extensión .co."""
    
    name = "crear"
    
    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            Parser configurado
        """
        parser = subparsers.add_parser(self.name, help=_("Crea archivos o proyectos"))
        sub = parser.add_subparsers(dest="accion")
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
            0 si éxito, 1 si error
        """
        if not args.ruta:
            mostrar_error(_("La ruta no puede estar vacía"))
            return 1
            
        accion = args.accion
        try:
            if accion == "archivo":
                return self._crear_archivo(args.ruta)
            elif accion == "carpeta":
                return self._crear_carpeta(args.ruta)
            elif accion == "proyecto":
                return self._crear_proyecto(args.ruta)
            else:
                mostrar_error(_("Acción no reconocida"))
                return 1
        except PermissionError:
            mostrar_error(_("Error de permisos al crear {path}").format(path=args.ruta))
            return 1
        except OSError as e:
            mostrar_error(_("Error al crear {path}: {error}").format(
                path=args.ruta, error=str(e)))
            return 1

    @staticmethod
    def _crear_archivo(ruta: str) -> int:
        """Crea un archivo .co vacío.
        
        Args:
            ruta: Ruta donde crear el archivo
            
        Returns:
            0 si éxito, 1 si error
        """
        if not ruta.endswith(".co"):
            ruta += ".co"
        if os.path.exists(ruta):
            mostrar_error(_("El archivo ya existe: {path}").format(path=ruta))
            return 1
            
        os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
        with open(ruta, "w", encoding="utf-8"):
            pass
        mostrar_info(_("Archivo creado: {path}").format(path=ruta))
        return 0

    @staticmethod
    def _crear_carpeta(ruta: str) -> int:
        """Crea una carpeta vacía.
        
        Args:
            ruta: Ruta donde crear la carpeta
            
        Returns:
            0 si éxito
        """
        os.makedirs(ruta, exist_ok=True)
        mostrar_info(_("Carpeta creada: {path}").format(path=ruta))
        return 0

    @staticmethod
    def _crear_proyecto(ruta: str) -> int:
        """Crea un proyecto Cobra básico.
        
        Args:
            ruta: Ruta donde crear el proyecto
            
        Returns:
            0 si éxito
        """
        os.makedirs(ruta, exist_ok=True)
        main = os.path.join(ruta, "main.co")
        if os.path.exists(main):
            mostrar_error(_("El archivo main.co ya existe en {path}").format(path=ruta))
            return 1
            
        with open(main, "w", encoding="utf-8"):
            pass
        mostrar_info(_("Proyecto Cobra creado en {path}").format(path=ruta))
        return 0
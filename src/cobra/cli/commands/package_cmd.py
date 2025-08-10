import logging
import zipfile
from argparse import _SubParsersAction, Namespace  # TODO: Evitar uso de API privada
from pathlib import Path
from typing import List

from cobra.cli.commands import modules_cmd
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.argument_parser import CustomArgumentParser
from cobra.cli.utils.messages import mostrar_error, mostrar_info

# Constantes
MAX_ZIP_SIZE = 1024 * 1024 * 50  # 50MB
MAX_FILES = 100
ALLOWED_EXTENSIONS = {".co"}

class PaqueteCommand(BaseCommand):
    """Crea e instala paquetes Cobra."""
    name = "paquete"

    def register_subparser(self, subparsers: _SubParsersAction) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            CustomArgumentParser: Parser configurado para este subcomando
        """
        parser = subparsers.add_parser(self.name, help=_("Gestiona paquetes Cobra"))
        sub = parser.add_subparsers(dest="accion", required=True)
        
        crear = sub.add_parser("crear", help=_("Crea un paquete"))
        crear.add_argument("fuente", help=_("Carpeta con archivos .co"), type=Path)
        crear.add_argument("paquete", help=_("Archivo de paquete"), type=Path)
        crear.add_argument("--nombre", default="paquete", help=_("Nombre"))
        crear.add_argument("--version", default="0.1", help=_("Version"))
        
        inst = sub.add_parser("instalar", help=_("Instala un paquete"))
        inst.add_argument("paquete", help=_("Archivo de paquete"), type=Path)
        
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Namespace) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si exitoso, 1 si hay error
        """
        try:
            if args.accion == "crear":
                return self._crear(args.fuente, args.paquete, args.nombre, args.version)
            elif args.accion == "instalar":
                return self._instalar(args.paquete)
            else:
                mostrar_error(_("Acción de paquete no reconocida"))
                return 1
        except Exception as e:
            logging.error(f"Error no manejado: {str(e)}", exc_info=True)
            mostrar_error(_("Error inesperado: {error}").format(error=str(e)))
            return 1

    @staticmethod
    def _validar_zip(path: Path) -> None:
        """Valida el tamaño y contenido del archivo ZIP.
        
        Args:
            path: Ruta al archivo ZIP
            
        Raises:
            ValueError: Si el archivo excede los límites permitidos
        """
        if path.stat().st_size > MAX_ZIP_SIZE:
            raise ValueError(_("El archivo excede el tamaño máximo permitido ({size} MB)").format(
                size=MAX_ZIP_SIZE//1024//1024))

    @staticmethod
    def _validar_modulos(mods: List[Path]) -> None:
        """Valida la lista de módulos.
        
        Args:
            mods: Lista de rutas a módulos
            
        Raises:
            ValueError: Si no hay módulos o hay demasiados
        """
        if len(mods) > MAX_FILES:
            raise ValueError(_("Demasiados archivos en el paquete (máximo {max})").format(max=MAX_FILES))
        if not mods:
            raise ValueError(_("No se encontraron módulos"))

    @staticmethod
    def _crear(src: Path, pkg: Path, nombre: str, version: str) -> int:
        """Crea un nuevo paquete.
        
        Args:
            src: Ruta a la carpeta fuente
            pkg: Ruta al archivo de paquete a crear
            nombre: Nombre del paquete
            version: Versión del paquete
            
        Returns:
            int: 0 si exitoso, 1 si hay error
        """
        try:
            if not src.is_dir():
                mostrar_error(_("Directorio inválido"))
                return 1

            if pkg.exists():
                mostrar_error(_("El archivo de paquete ya existe"))
                return 1

            mods = [f for f in src.iterdir() if f.suffix in ALLOWED_EXTENSIONS]
            PaqueteCommand._validar_modulos(mods)

            mod_list = ", ".join(f'"{m.name}"' for m in mods)
            contenido = (
                f'[paquete]\nnombre = "{nombre}"\nversion = "{version}"\n\n'
                f"[modulos]\narchivos = [{mod_list}]\n"
            )

            with zipfile.ZipFile(pkg, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for m in mods:
                    zf.write(m, arcname=m.name)
                zf.writestr("cobra.pkg", contenido)

            mostrar_info(_("Paquete creado en {dest}").format(dest=pkg))
            return 0

        except ValueError as e:
            mostrar_error(str(e))
            return 1
        except OSError as e:
            mostrar_error(_("Error de E/S al crear paquete: {error}").format(error=str(e)))
            return 1
        except zipfile.BadZipFile as e:
            mostrar_error(_("Error en archivo ZIP: {error}").format(error=str(e)))
            return 1

    @staticmethod
    def _instalar(pkg: Path) -> int:
        """Instala un paquete.
        
        Args:
            pkg: Ruta al archivo de paquete
            
        Returns:
            int: 0 si exitoso, 1 si hay error
        """
        try:
            if not pkg.exists():
                mostrar_error(_("Paquete no encontrado"))
                return 1

            PaqueteCommand._validar_zip(pkg)
            modules_dir = Path(modules_cmd.MODULES_PATH)
            modules_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(pkg) as zf:
                file_list = [name for name in zf.namelist() if name.endswith(".co")]
                PaqueteCommand._validar_modulos(file_list)

                for name in file_list:
                    # Validar y normalizar ruta
                    try:
                        safe_path = Path(name).resolve().relative_to(modules_dir)
                    except (ValueError, RuntimeError):
                        mostrar_error(_("Nombre de archivo no válido en el paquete"))
                        return 1

                    dest = modules_dir / safe_path
                    if dest.exists() and dest.is_symlink():
                        mostrar_error(
                            _("El destino {dest} es un enlace simbólico").format(dest=dest)
                        )
                        return 1

                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(name) as src, open(dest, "wb") as out:
                        out.write(src.read())

            mostrar_info(
                _("Paquete instalado en {dest}").format(dest=modules_cmd.MODULES_PATH)
            )
            return 0

        except ValueError as e:
            mostrar_error(str(e))
            return 1
        except OSError as e:
            mostrar_error(_("Error de E/S al instalar paquete: {error}").format(error=str(e)))
            return 1
        except zipfile.BadZipFile as e:
            mostrar_error(_("Error en archivo ZIP: {error}").format(error=str(e)))
            return 1
import os
import zipfile
from pathlib import Path
from typing import Any
from argparse import _SubParsersAction

from cobra.cli.commands import modules_cmd
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

class PaqueteCommand(BaseCommand):
    """Crea e instala paquetes Cobra."""
    name = "paquete"

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Gestiona paquetes Cobra"))
        sub = parser.add_subparsers(dest="accion")
        crear = sub.add_parser("crear", help=_("Crea un paquete"))
        crear.add_argument("fuente", help=_("Carpeta con archivos .co"))
        crear.add_argument("paquete", help=_("Archivo de paquete"))
        crear.add_argument("--nombre", default="paquete", help=_("Nombre"))
        crear.add_argument("--version", default="0.1", help=_("Version"))
        inst = sub.add_parser("instalar", help=_("Instala un paquete"))
        inst.add_argument("paquete", help=_("Archivo de paquete"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""
        accion = args.accion
        if accion == "crear":
            return self._crear(args.fuente, args.paquete, args.nombre, args.version)
        elif accion == "instalar":
            return self._instalar(args.paquete)
        else:
            mostrar_error(_("Accion de paquete no reconocida"))
            return 1

    @staticmethod
    def _crear(src: str, pkg: str, nombre: str, version: str) -> int:
        try:
            src_path = Path(src)
            if not src_path.is_dir():
                mostrar_error(_("Directorio invalido"))
                return 1

            pkg_path = Path(pkg)
            if pkg_path.exists():
                mostrar_error(_("El archivo de paquete ya existe"))
                return 1

            mods = [f for f in src_path.iterdir() if f.suffix == ".co"]
            if not mods:
                mostrar_error(_("No se encontraron modulos"))
                return 1

            mod_list = ", ".join(f'"{m.name}"' for m in mods)
            contenido = (
                f'[paquete]\nnombre = "{nombre}"\nversion = "{version}"\n\n'
                f"[modulos]\narchivos = [{mod_list}]\n"
            )

            with zipfile.ZipFile(pkg_path, "w") as zf:
                for m in mods:
                    zf.write(m, arcname=m.name)
                zf.writestr("cobra.pkg", contenido)

            mostrar_info(_("Paquete creado en {dest}").format(dest=pkg))
            return 0
        except (OSError, zipfile.BadZipFile) as e:
            mostrar_error(f"Error al crear paquete: {str(e)}")
            return 1

    @staticmethod
    def _instalar(pkg: str) -> int:
        try:
            pkg_path = Path(pkg)
            if not pkg_path.exists():
                mostrar_error(_("Paquete no encontrado"))
                return 1

            modules_dir = Path(modules_cmd.MODULES_PATH)
            modules_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(pkg_path) as zf:
                for name in zf.namelist():
                    if not name.endswith(".co"):
                        continue
                        
                    dest = modules_dir / Path(name).name
                    if dest.exists() and dest.is_symlink():
                        mostrar_error(
                            _("El destino {dest} es un enlace simbólico").format(dest=dest)
                        )
                        return 1

                    # Validar nombre de archivo
                    if ".." in name or name.startswith("/"):
                        mostrar_error(_("Nombre de archivo no válido en el paquete"))
                        return 1

                    with zf.open(name) as src, open(dest, "wb") as out:
                        out.write(src.read())

            mostrar_info(
                _("Paquete instalado en {dest}").format(dest=modules_cmd.MODULES_PATH)
            )
            return 0
        except (OSError, zipfile.BadZipFile) as e:
            mostrar_error(f"Error al instalar paquete: {str(e)}")
            return 1
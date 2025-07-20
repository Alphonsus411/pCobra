import os
import zipfile
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info
from . import modules_cmd


class PaqueteCommand(BaseCommand):
    """Crea e instala paquetes Cobra."""

    name = "paquete"

    def register_subparser(self, subparsers):
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

    def run(self, args):
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
    def _crear(src, pkg, nombre, version):
        if not os.path.isdir(src):
            mostrar_error(_("Directorio invalido"))
            return 1
        mods = [f for f in os.listdir(src) if f.endswith(".co")]
        if not mods:
            mostrar_error(_("No se encontraron modulos"))
            return 1
        mod_list = ", ".join(f'"{m}"' for m in mods)
        contenido = (
            f'[paquete]\nnombre = "{nombre}"\nversion = "{version}"\n\n'
            f"[modulos]\narchivos = [{mod_list}]\n"
        )
        with zipfile.ZipFile(pkg, "w") as zf:
            for m in mods:
                zf.write(os.path.join(src, m), arcname=m)
            zf.writestr("cobra.pkg", contenido)
        mostrar_info(_("Paquete creado en {dest}").format(dest=pkg))
        return 0

    @staticmethod
    def _instalar(pkg):
        if not os.path.exists(pkg):
            mostrar_error(_("Paquete no encontrado"))
            return 1
        os.makedirs(modules_cmd.MODULES_PATH, exist_ok=True)
        with zipfile.ZipFile(pkg) as zf:
            for name in zf.namelist():
                if name.endswith(".co"):
                    dest = os.path.join(
                        modules_cmd.MODULES_PATH, os.path.basename(name)
                    )
                    with zf.open(name) as src, open(dest, "wb") as out:
                        out.write(src.read())
        mostrar_info(
            _("Paquete instalado en {dest}").format(dest=modules_cmd.MODULES_PATH)
        )
        return 0

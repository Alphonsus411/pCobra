import os
import shutil
from .base import BaseCommand

MODULES_PATH = os.path.join(os.path.dirname(__file__), "..", "modules")
os.makedirs(MODULES_PATH, exist_ok=True)


class ModulesCommand(BaseCommand):
    """Gestiona los módulos instalados."""

    name = "modulos"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Gestiona módulos instalados")
        mod_sub = parser.add_subparsers(dest="accion")
        mod_sub.add_parser("listar", help="Lista módulos")
        inst = mod_sub.add_parser("instalar", help="Instala un módulo")
        inst.add_argument("ruta")
        rem = mod_sub.add_parser("remover", help="Elimina un módulo")
        rem.add_argument("nombre")
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        accion = args.accion
        if accion == "listar":
            return self._listar_modulos()
        elif accion == "instalar":
            return self._instalar_modulo(args.ruta)
        elif accion == "remover":
            return self._remover_modulo(args.nombre)
        else:
            print("Acción de módulos no reconocida")
            return 1

    @staticmethod
    def _listar_modulos():
        mods = [f for f in os.listdir(MODULES_PATH) if f.endswith(".co")]
        if not mods:
            print("No hay módulos instalados")
        else:
            for m in mods:
                print(m)
        return 0

    @staticmethod
    def _instalar_modulo(ruta):
        if not os.path.exists(ruta):
            print(f"No se encontró el módulo {ruta}")
            return 1
        destino = os.path.join(MODULES_PATH, os.path.basename(ruta))
        shutil.copy(ruta, destino)
        print(f"Módulo instalado en {destino}")
        return 0

    @staticmethod
    def _remover_modulo(nombre):
        archivo = os.path.join(MODULES_PATH, nombre)
        if os.path.exists(archivo):
            os.remove(archivo)
            print(f"Módulo {nombre} eliminado")
            return 0
        else:
            print(f"El módulo {nombre} no existe")
            return 1

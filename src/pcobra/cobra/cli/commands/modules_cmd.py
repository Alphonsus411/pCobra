from typing import Any
from pathlib import Path

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.services import mod_service as _mod_service
from pcobra.cobra.cli.services.contracts import ModRequest
from pcobra.cobra.cli.services.mod_service import (
    LOCK_KEY,
    MODULE_EXTENSION,
    ModService,
    buscar_modulo,
    cargar_lock,
    actualizar_lock,
    instalar_modulo,
    listar_modulos,
    remover_modulo,
    obtener_version,
    obtener_version_lock,
    validar_nombre_modulo,
    validar_ruta,
    yaml,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.module_paths import modules_path, user_config_dir
from pcobra.cobra.cli.utils.messages import mostrar_error

_cobrahub_module = __import__("pcobra.cobra.cli.cobrahub_client", fromlist=["CobraHubClient"])
_CobraHubClient = _cobrahub_module.CobraHubClient
client = _CobraHubClient.__new__(_CobraHubClient)
client.base_url = "https://cobrahub.example.com/api"
client.session = None
MODULES_PATH = modules_path()
LOCK_FILE = user_config_dir() / "module_map.toml"
MODULE_MAP_PATH = str(LOCK_FILE)


def _sync_service_state() -> None:
    """Sincroniza reexportaciones históricas antes de delegar al servicio."""

    _mod_service.MODULES_PATH = MODULES_PATH
    _mod_service.LOCK_FILE = Path(LOCK_FILE)
    _mod_service.MODULE_MAP_PATH = MODULE_MAP_PATH
    _mod_service.yaml = yaml
    _mod_service._client = client
    _mod_service.mostrar_error = mostrar_error


class ModulesCommand(BaseCommand):
    """Adaptador legacy de `modulos` hacia ModService."""

    name = "modulos"

    def __init__(self) -> None:
        super().__init__()
        self._service = ModService()

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        parser = subparsers.add_parser(self.name, help=_("Gestiona módulos instalados"))
        mod_sub = parser.add_subparsers(dest="accion")
        mod_sub.add_parser("listar", help=_("Lista módulos"))
        inst = mod_sub.add_parser("instalar", help=_("Instala un módulo"))
        inst.add_argument("ruta", help=_("Ruta al archivo del módulo"))
        rem = mod_sub.add_parser("remover", help=_("Elimina un módulo"))
        rem.add_argument("nombre", help=_("Nombre del módulo a eliminar"))
        pub = mod_sub.add_parser("publicar", help=_("Publica un módulo en CobraHub"))
        pub.add_argument("ruta", help=_("Ruta al archivo del módulo"))
        bus = mod_sub.add_parser("buscar", help=_("Descarga un módulo desde CobraHub"))
        bus.add_argument("nombre", help=_("Nombre del módulo a buscar"))
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        _sync_service_state()
        request = ModRequest(
            accion=getattr(args, "accion", ""),
            ruta=getattr(args, "ruta", None),
            nombre=getattr(args, "nombre", None),
        )
        return self._service.run(request)

    @staticmethod
    def _instalar_modulo(ruta: str) -> int:
        """Conserva el adaptador histórico delegando en ``mod_service``."""

        previous_error_handler = _mod_service.mostrar_error
        try:
            _sync_service_state()
            return instalar_modulo(ruta)
        finally:
            _mod_service.mostrar_error = previous_error_handler

    @staticmethod
    def _remover_modulo(nombre: str) -> int:
        """Conserva el adaptador histórico delegando en ``mod_service``."""

        previous_error_handler = _mod_service.mostrar_error
        try:
            _sync_service_state()
            return remover_modulo(nombre)
        finally:
            _mod_service.mostrar_error = previous_error_handler

from argparse import Namespace, SUPPRESS
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.services.cobrahub_service import CobraHubService
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info

# Compatibilidad para instrumentación que parcheaba este nombre en el módulo.
# El alias apunta al contrato de servicio y no atraviesa la fachada histórica.
CobraHubPackages = CobraHubService


class HubCommand(BaseCommand):
    """Publica, busca e instala paquetes en CobraHub."""

    name = "hub"
    public_v2_hidden = True

    @staticmethod
    def _ocultar_accion_subparser(subparsers: Any, name: str) -> None:
        """Evita que un subparser compatible oculto aparezca en la ayuda."""
        choices_actions = getattr(subparsers, "_choices_actions", None)
        if choices_actions is not None:
            choices_actions[:] = [
                action
                for action in choices_actions
                if getattr(action, "dest", None) != name
            ]

    def register_subparser(
        self, subparsers: Any, hidden: bool = False
    ) -> CustomArgumentParser:
        parser_help = SUPPRESS if hidden else _("Gestiona paquetes en CobraHub")
        parser = subparsers.add_parser(self.name, help=parser_help)
        if hidden:
            self._ocultar_accion_subparser(subparsers, self.name)
        sub = parser.add_subparsers(dest="accion", required=True)
        pub = sub.add_parser("publicar", help=_("Publica un paquete .co"))
        pub.add_argument("paquete", type=Path)
        buscar = sub.add_parser("buscar", help=_("Busca paquetes"))
        buscar.add_argument("consulta")
        inst = sub.add_parser("instalar", help=_("Instala un paquete"))
        inst.add_argument("nombre")
        inst.add_argument("--version")
        inst.add_argument("--destino", type=Path)
        cache = sub.add_parser("cache", help=_("Gestiona la caché local de paquetes"))
        cache_sub = cache.add_subparsers(dest="cache_accion", required=True)
        cache_sub.add_parser("listar", help=_("Lista paquetes cacheados"))
        limpiar = cache_sub.add_parser("limpiar", help=_("Limpia paquetes cacheados"))
        limpiar.add_argument("nombre", nargs="?")
        cache_sub.add_parser("validar", help=_("Valida paquetes cacheados"))
        parser.set_defaults(cmd=self)
        return parser

    def register_hidden_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra el comando como compatibilidad pública v2 oculta."""
        return self.register_subparser(subparsers, hidden=True)

    def run(self, args: Namespace) -> int:
        service = CobraHubService()
        if args.accion == "publicar":
            return 0 if service.publicar_paquete(str(args.paquete)) else 1
        if args.accion == "buscar":
            results = service.buscar_paquetes(args.consulta)
            for item in results:
                nombre = item.get("name", item.get("nombre", "paquete"))
                mostrar_info(f"{nombre} {item.get('version', '')}".strip())
            return 0
        if args.accion == "instalar":
            destino = str(args.destino) if args.destino else None
            return (
                0
                if service.instalar_paquete(args.nombre, destino, args.version)
                else 1
            )
        if args.accion == "cache":
            return self._run_cache(args, service)
        mostrar_error(_("Acción de hub no reconocida"))
        return 1

    def _run_cache(self, args: Namespace, service: CobraHubService) -> int:
        """Ejecuta las acciones locales de caché sin contactar con CobraHub."""
        if args.cache_accion == "listar":
            for path in service.listar_cache():
                mostrar_info(str(path))
            return 0
        if args.cache_accion == "limpiar":
            try:
                borrados = service.limpiar_cache(args.nombre)
            except ValueError as exc:
                mostrar_error(str(exc))
                return 1
            mostrar_info(
                _("Paquetes eliminados de caché: {total}").format(total=borrados)
            )
            return 0
        if args.cache_accion == "validar":
            resultados = service.validar_cache()
            for path, ok, error in resultados:
                estado = _("válido") if ok else _("inválido")
                detalle = f": {error}" if error else ""
                mostrar_info(f"{path} {estado}{detalle}")
            return 0 if all(ok for _, ok, _ in resultados) else 1
        mostrar_error(_("Acción de caché no reconocida"))
        return 1

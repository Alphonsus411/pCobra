from argparse import Namespace
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.services.command_factory import CommandFactory
from pcobra.cobra.cli.services.contracts import ModRequest, RunRequest, TestRequest
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.public_command_policy import PROFILE_DEVELOPMENT, resolve_command_profile
from pcobra.cobra.cli.utils import messages


LEGACY_GROUP_MIGRATION_HINTS: dict[str, str] = {
    "ejecutar": "cobra run <archivo.co>",
    "compilar": "cobra build <archivo.co>",
    "verificar": "cobra test <archivo.co>",
    "modulos": "cobra mod <list|install|remove|publish|search>",
}


class LegacyCommandGroupV2(BaseCommand):
    """Grupo de compatibilidad para comandos legacy en UI v2."""

    name = "legacy"

    def __init__(self) -> None:
        super().__init__()
        self._command_factory = CommandFactory()
        self._execute = self._command_factory.create("ejecutar")
        self._compile = self._command_factory.create("compilar")
        self._verify = self._command_factory.create("verificar")
        self._modules = self._command_factory.create("modulos")

    def register_subparser(self, subparsers: Any):
        parser = subparsers.add_parser(self.name, help=_("Legacy compatibility command group"))
        legacy_sub = parser.add_subparsers(dest="legacy_command")

        ejecutar = legacy_sub.add_parser("ejecutar", help=_("Legacy ejecutar"))
        ejecutar.add_argument("archivo")
        ejecutar.add_argument("--debug", action="store_true", default=False)
        ejecutar.add_argument("--sandbox", action="store_true")
        ejecutar.add_argument("--contenedor")

        compilar = legacy_sub.add_parser("compilar", help=_("Legacy compilar"))
        compilar.add_argument("archivo")
        compilar.add_argument("--tipo")
        compilar.add_argument("--tipos")

        verificar = legacy_sub.add_parser("verificar", help=_("Legacy verificar"))
        verificar.add_argument("archivo")
        verificar.add_argument("--lenguajes", "-l", required=True)

        modulos = legacy_sub.add_parser("modulos", help=_("Legacy modulos"))
        modulos_sub = modulos.add_subparsers(dest="accion")
        modulos_sub.add_parser("listar")
        inst = modulos_sub.add_parser("instalar")
        inst.add_argument("ruta")
        rem = modulos_sub.add_parser("remover")
        rem.add_argument("nombre")
        pub = modulos_sub.add_parser("publicar")
        pub.add_argument("ruta")
        bus = modulos_sub.add_parser("buscar")
        bus.add_argument("nombre")

        parser.set_defaults(cmd=self)
        return parser

    def run(self, args: Any) -> int:
        command = getattr(args, "legacy_command", None)
        if command in LEGACY_GROUP_MIGRATION_HINTS:
            messages.mostrar_advertencia(
                _(
                    "Comando legacy '{legacy}' en grupo 'legacy'. "
                    "Esta ruta es solo para perfil development y será retirada. "
                    "Migra ahora a interfaz pública: {hint}."
                ).format(legacy=command, hint=LEGACY_GROUP_MIGRATION_HINTS[command])
            )
        if resolve_command_profile() != PROFILE_DEVELOPMENT:
            messages.mostrar_error(
                _(
                    "El grupo 'legacy' está restringido a development. "
                    "Use comandos públicos: cobra run/build/test/mod/repl."
                ),
                registrar_log=False,
            )
            return 1
        if command == "ejecutar":
            return self._execute.run(
                RunRequest(
                    archivo=args.archivo,
                    debug=getattr(args, "debug", False),
                    sandbox=getattr(args, "sandbox", False),
                    contenedor=getattr(args, "contenedor", None),
                    formatear=getattr(args, "formatear", False),
                    modo=getattr(args, "modo", "mixto"),
                )
            )
        if command == "compilar":
            return self._compile.run(
                Namespace(
                    archivo=args.archivo,
                    tipo=getattr(args, "tipo", None),
                    backend=getattr(args, "tipo", None),
                    tipos=getattr(args, "tipos", None),
                    modo=getattr(args, "modo", "mixto"),
                )
            )
        if command == "verificar":
            return self._verify.run(
                TestRequest(
                    archivo=args.archivo,
                    lenguajes=getattr(args, "lenguajes", ""),
                    modo=getattr(args, "modo", "mixto"),
                )
            )
        if command == "modulos":
            return self._modules.run(
                ModRequest(
                    accion=getattr(args, "accion", None),
                    ruta=getattr(args, "ruta", None),
                    nombre=getattr(args, "nombre", None),
                )
            )
        return 1

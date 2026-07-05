from argparse import Namespace, SUPPRESS
import shutil
import stat
import sys
import zipfile
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands import modules_cmd
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.packaging import (
    construir_paquete,
    crear_paquete,
    es_paquete_cobra,
    extraer_paquete,
    inspeccionar_paquete,
    validar_paquete,
    verificar_integridad,
)


class PaqueteCommand(BaseCommand):
    """Gestiona paquetes Cobra .co sin modificar la sintaxis del lenguaje."""

    name = "paquete"
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
        parser_help = SUPPRESS if hidden else _("Gestiona paquetes Cobra .co")
        parser = subparsers.add_parser(self.name, help=parser_help)
        if hidden:
            self._ocultar_accion_subparser(subparsers, self.name)
        sub = parser.add_subparsers(dest="accion", required=True)

        crear = sub.add_parser("crear", help=_("Crea la estructura de un paquete"))
        crear.add_argument("fuente", type=Path, help=_("Directorio del paquete"))
        crear.add_argument(
            "paquete", nargs="?", type=Path, help=_("Alias legacy: salida .co opcional")
        )
        crear.add_argument("--nombre", default=None, help=_("Nombre del paquete"))
        crear.add_argument("--version", default="0.1.0", help=_("Versión"))

        validar = sub.add_parser("validar", help=_("Valida un paquete .co"))
        validar.add_argument("paquete", type=Path)

        construir = sub.add_parser("construir", help=_("Construye un paquete .co"))
        construir.add_argument("fuente", type=Path)
        construir.add_argument("salida", nargs="?", type=Path)
        construir.add_argument("--nombre", default=None)
        construir.add_argument("--version", default=None)

        inspeccionar = sub.add_parser(
            "inspeccionar", help=_("Inspecciona el contenido de un paquete")
        )
        inspeccionar.add_argument("paquete", type=Path)

        verificar = sub.add_parser(
            "verificar",
            aliases=["integridad"],
            help=_("Verifica la integridad de un paquete .co"),
            description=_(
                "Verifica la integridad SHA-256 de un paquete .co; "
                "integridad es un alias legacy equivalente."
            ),
        )
        verificar.add_argument("paquete", type=Path)

        extraer = sub.add_parser("extraer", help=_("Extrae un paquete .co"))
        extraer.add_argument("paquete", type=Path)
        extraer.add_argument("destino", type=Path)

        inst = sub.add_parser(
            "instalar", help=_("Alias legacy de extraer a ~/.cobra/packages")
        )
        inst.add_argument("paquete", type=Path)
        inst.add_argument(
            "--destino", type=Path, default=Path.home() / ".cobra" / "packages"
        )

        parser.set_defaults(cmd=self)
        return parser

    def register_hidden_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra el comando como compatibilidad pública v2 oculta."""
        return self.register_subparser(subparsers, hidden=True)

    @staticmethod
    def _normalizar_nombre_legacy(nombre: str) -> Path:
        ruta = Path(nombre.replace("\\", "/"))
        if ruta.is_absolute() or ".." in ruta.parts or not ruta.parts:
            raise ValueError(_("Ruta insegura en paquete: {ruta}").format(ruta=nombre))
        if ruta.as_posix() in {"", "."}:
            raise ValueError(_("Ruta inválida en paquete: {ruta}").format(ruta=nombre))
        return ruta

    @staticmethod
    def _rechazar_symlinks_existentes(destino: Path, objetivo: Path) -> None:
        relativo = objetivo.relative_to(destino)
        candidatos = [destino]
        candidatos.extend(
            destino / parte for parte in relativo.parents if parte != Path(".")
        )
        candidatos.append(objetivo)
        for candidato in candidatos:
            if candidato.is_symlink():
                raise ValueError(
                    _(
                        "No se permite escribir sobre symlinks existentes: {ruta}"
                    ).format(ruta=candidato)
                )

    @staticmethod
    def _instalar(paquete: Path) -> int:
        """Instala paquetes Cobra modernos o ZIP legacy en el directorio de módulos.

        Este adaptador conserva el flujo histórico usado por tests y llamadas
        directas: instala siempre en ``modules_cmd.MODULES_PATH`` y devuelve un
        código de salida en vez de propagar excepciones.
        """
        try:
            destino = Path(modules_cmd.MODULES_PATH).resolve()
            if es_paquete_cobra(paquete):
                extraer_paquete(paquete, destino)
                mostrar_info(_("Paquete instalado en {dest}").format(dest=destino))
                return 0

            if not zipfile.is_zipfile(paquete):
                raise ValueError(
                    _("No es un paquete Cobra ni un ZIP legacy válido: {pkg}").format(
                        pkg=paquete
                    )
                )

            destino.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(paquete) as zf:
                for info in zf.infolist():
                    nombre = info.filename
                    relativo = PaqueteCommand._normalizar_nombre_legacy(nombre)
                    objetivo_sin_resolver = destino / relativo
                    PaqueteCommand._rechazar_symlinks_existentes(
                        destino, objetivo_sin_resolver
                    )
                    objetivo = objetivo_sin_resolver.resolve()
                    objetivo.relative_to(destino)
                    modo = info.external_attr >> 16
                    if stat.S_IFMT(modo) == stat.S_IFLNK:
                        raise ValueError(
                            _(
                                "No se permite extraer symlinks desde paquetes legacy: {ruta}"
                            ).format(ruta=nombre)
                        )
                    if info.is_dir():
                        objetivo.mkdir(parents=True, exist_ok=True)
                    else:
                        objetivo.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info) as src, objetivo.open("wb") as out:
                            shutil.copyfileobj(src, out)
            mostrar_info(_("Paquete instalado en {dest}").format(dest=destino))
            return 0
        except Exception as exc:
            error_fn = mostrar_error
            alias_module = sys.modules.get("cobra.cli.commands.package_cmd")
            if alias_module is not None:
                error_fn = getattr(alias_module, "mostrar_error", error_fn)
            error_fn(_("Error instalando paquete: {error}").format(error=str(exc)))
            return 1

    def run(self, args: Namespace) -> int:
        try:
            if args.accion == "crear":
                nombre = args.nombre or args.fuente.name
                manifest = crear_paquete(
                    args.fuente, nombre=nombre, version=args.version
                )
                if args.paquete:
                    destino = construir_paquete(
                        args.fuente, args.paquete, nombre=nombre, version=args.version
                    )
                    mostrar_info(_("Paquete creado en {dest}").format(dest=destino))
                else:
                    mostrar_info(
                        _("Estructura de paquete creada: {manifest}").format(
                            manifest=manifest
                        )
                    )
                return 0
            if args.accion == "validar":
                if not es_paquete_cobra(args.paquete):
                    raise ValueError(
                        "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                    )
                validar_paquete(args.paquete)
                mostrar_info(_("Paquete válido: {pkg}").format(pkg=args.paquete))
                return 0
            if args.accion == "construir":
                destino = construir_paquete(
                    args.fuente, args.salida, nombre=args.nombre, version=args.version
                )
                mostrar_info(_("Paquete construido en {dest}").format(dest=destino))
                return 0
            if args.accion == "inspeccionar":
                if not es_paquete_cobra(args.paquete):
                    raise ValueError(
                        "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                    )
                info = inspeccionar_paquete(args.paquete)
                mostrar_info(
                    _("Paquete: {name} {version}").format(
                        name=info.manifest.get("name"),
                        version=info.manifest.get("version"),
                    )
                )
                for file in info.files:
                    mostrar_info(f" - {file}")
                mostrar_info(_("SHA256: {checksum}").format(checksum=info.checksum))
                return 0
            if args.accion in {"verificar", "integridad"}:
                if not es_paquete_cobra(args.paquete):
                    raise ValueError(
                        "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                    )
                if verificar_integridad(args.paquete):
                    mostrar_info(_("Integridad válida: {pkg}").format(pkg=args.paquete))
                    return 0
                mostrar_error(_("Integridad inválida: {pkg}").format(pkg=args.paquete))
                return 1
            if args.accion == "extraer":
                if not es_paquete_cobra(args.paquete):
                    raise ValueError(
                        "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                    )
                destino = extraer_paquete(args.paquete, args.destino)
                mostrar_info(_("Paquete extraído en {dest}").format(dest=destino))
                return 0
            if args.accion == "instalar":
                if not es_paquete_cobra(args.paquete):
                    raise ValueError(
                        "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                    )
                destino = extraer_paquete(args.paquete, args.destino)
                mostrar_info(_("Paquete instalado en {dest}").format(dest=destino))
                return 0
            mostrar_error(_("Acción de paquete no reconocida"))
            return 1
        except Exception as exc:
            mostrar_error(
                _("Error gestionando paquete: {error}").format(error=str(exc))
            )
            return 1

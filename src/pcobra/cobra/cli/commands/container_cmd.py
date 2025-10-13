import os
import re
import subprocess
from pathlib import Path
from typing import Any
from argparse import ArgumentParser

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info

def validar_tag(valor: str) -> str:
    """Valida que el tag tenga un formato válido para Docker."""
    if not re.match(r"^[a-zA-Z0-9_.-]+$", valor):
        raise ValueError(_("El tag debe contener solo letras, números, guiones y puntos"))
    return valor

class ContainerCommand(BaseCommand):
    """Construye la imagen Docker del proyecto."""
    name = "contenedor"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Construye la imagen Docker"))
        parser.add_argument(
            "--tag",
            default="cobra",
            help=_("Nombre de la imagen"),
            type=validar_tag
        )
        parser.set_defaults(cmd=self)
        return parser

    def _encontrar_raiz_proyecto(self) -> Path:
        """Encuentra la raíz del proyecto de forma segura."""
        ruta = Path(__file__).resolve()
        while ruta.parent != ruta:
            if (ruta / "cobra.toml").exists():
                return ruta
            ruta = ruta.parent
        raise ValueError(_("No se pudo encontrar la raíz del proyecto"))

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando."""
        try:
            raiz = self._encontrar_raiz_proyecto()
            
            # Verificar que Docker está instalado
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            
            subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    args.tag,
                    str(raiz)
                ],
                check=True,
                timeout=600  # 10 minutos máximo
            )
            mostrar_info(_("Imagen Docker creada exitosamente"))
            return 0
            
        except FileNotFoundError:
            mostrar_error(
                _("Docker no está instalado. Por favor instala Docker desde docker.com")
            )
            return 1
        except subprocess.CalledProcessError as e:
            mostrar_error(_("Error construyendo la imagen Docker: {err}").format(
                err=e.stderr.decode() if e.stderr else str(e))
            )
            return 1
        except subprocess.TimeoutExpired:
            mostrar_error(_("Tiempo de espera agotado (10 minutos) al construir la imagen"))
            return 1
        except (PermissionError, OSError) as e:
            mostrar_error(_("Error de acceso: {err}").format(err=str(e)))
            return 1
        except ValueError as e:
            mostrar_error(str(e))
            return 1

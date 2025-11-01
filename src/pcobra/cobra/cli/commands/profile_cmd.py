# -*- coding: utf-8 -*-
"""Comando para perfilar la ejecución de programas Cobra."""

import cProfile
import io
import logging
import os
import pstats
import shutil
import subprocess
import tempfile
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional, Any

from pcobra.cobra.core import Lexer
from pcobra.cobra.core import Parser
from pcobra.cobra.transpilers import module_map
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.sandbox import validar_dependencias
from pcobra.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import (
    normalizar_validadores_extra,
    validar_archivo_existente,
)


class ProfileCommand(BaseCommand):
    """Ejecuta un script Cobra con cProfile."""

    name: str = "profile"
    logger = logging.getLogger(__name__)

    def _limpiar_archivo_temporal(self, archivo: str) -> None:
        """Limpia un archivo temporal si existe."""
        try:
            Path(archivo).unlink(missing_ok=True)
        except OSError as e:
            self.logger.warning(f"Error al eliminar archivo temporal {archivo}: {e}")

    def _obtener_argumento(self, args: Namespace, nombre: str, default: Optional[any] = None) -> any:
        """Obtiene un argumento del namespace de argumentos con valor por defecto."""
        return getattr(args, nombre, default)

    def _mostrar_error_herramienta_no_encontrada(self, herramienta: str) -> int:
        """Muestra un mensaje de error para una herramienta no encontrada."""
        msg = _(
            "Herramienta {tool} no encontrada. "
            "Instálala con 'pip install {tool}'"
        ).format(tool=herramienta)
        mostrar_error(msg)
        return 1

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Perfila un programa"))
        parser.add_argument("archivo")
        parser.add_argument(
            "--output",
            "-o",
            help=_("Archivo .prof para guardar los resultados"),
        )
        parser.add_argument(
            "--ui",
            help=_("Herramienta de visualización del perfil (por ejemplo, snakeviz)"),
        )
        parser.add_argument(
            "--analysis",
            action="store_true",
            help=_("Perfila las fases de análisis (lexer y parser)"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _validar_directorio_salida(self, ruta: str) -> bool:
        """Valida que el directorio de salida exista y tenga permisos de escritura."""
        dir_salida = Path(ruta).parent
        try:
            dir_salida.mkdir(parents=True, exist_ok=True)
            return os.access(dir_salida, os.W_OK)
        except OSError:
            return False

    def run(self, args: Namespace) -> int:
        """Ejecuta la lógica del comando."""
        archivo: str = args.archivo
        output: Optional[str] = self._obtener_argumento(args, "output")
        ui: Optional[str] = self._obtener_argumento(args, "ui")
        depurar: bool = self._obtener_argumento(args, "depurar", False)
        formatear: bool = bool(self._obtener_argumento(args, "formatear", False))
        seguro: bool = self._obtener_argumento(args, "seguro", True)
        raw_extra_validators = self._obtener_argumento(args, "extra_validators")
        try:
            extra_validators = normalizar_validadores_extra(raw_extra_validators)
        except TypeError:
            mostrar_error(_("Los validadores extra deben ser una ruta o lista de rutas"))
            return 1
        analysis: bool = self._obtener_argumento(args, "analysis", False)

        validar_archivo_existente(archivo)

        if output and not self._validar_directorio_salida(output):
            mostrar_error(f"No se puede escribir en el directorio de salida para '{output}'")
            return 1

        try:
            validar_dependencias("python", module_map.get_toml_map())
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1

        if formatear:
            ExecuteCommand._formatear_codigo(archivo)  # type: ignore[attr-defined]

        self.logger.setLevel(logging.DEBUG if depurar else logging.ERROR)

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                codigo = f.read()
        except (IOError, UnicodeDecodeError) as e:
            mostrar_error(f"Error leyendo el archivo: {e}")
            return 1

        try:
            tokens = Lexer(codigo).tokenizar(profile=analysis)
            ast = Parser(tokens).parsear(profile=analysis)
        except Exception as e:
            mostrar_error(f"Error en análisis sintáctico: {e}")
            return 1

        if seguro:
            try:
                validador = construir_cadena(
                    InterpretadorCobra._cargar_validadores(extra_validators)
                    if isinstance(extra_validators, str)
                    else extra_validators
                )
                for nodo in ast:
                    nodo.aceptar(validador)
            except PrimitivaPeligrosaError as pe:
                self.logger.error(f"Primitiva peligrosa: {pe}")
                mostrar_error(str(pe))
                return 1

        profiler = cProfile.Profile()
        tmp_file: Optional[str] = None

        try:
            profiler.enable()
            InterpretadorCobra(
                safe_mode=seguro, extra_validators=extra_validators
            ).ejecutar_ast(ast)
            profiler.disable()
            
            stats_file = output
            if ui:
                if shutil.which(ui) is None:
                    return self._mostrar_error_herramienta_no_encontrada(ui)
                
                if not stats_file:
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".prof", delete=False) as tmp:
                        tmp_file = tmp.name
                        stats_file = tmp_file
                
                profiler.dump_stats(stats_file)
                try:
                    subprocess.run([ui, stats_file], check=True)
                except subprocess.CalledProcessError as e:
                    mostrar_error(f"Error ejecutando {ui}: {e}")
                    return 1
                except FileNotFoundError:
                    return self._mostrar_error_herramienta_no_encontrada(ui)
            else:
                if stats_file:
                    profiler.dump_stats(stats_file)
                    msg = _("Resultados de perfil guardados en {file}").format(
                        file=stats_file
                    )
                    mostrar_info(msg)
                else:
                    s = io.StringIO()
                    stats = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
                    stats.print_stats(10)
                    print(s.getvalue())
            return 0
            
        except (RuntimeError, ValueError, TypeError) as e:
            self.logger.error(f"Error de ejecución: {e}")
            mostrar_error(f"Error de ejecución: {e}")
            return 1
        except Exception as e:
            self.logger.critical(f"Error inesperado: {e}", exc_info=True)
            mostrar_error(_("Ha ocurrido un error inesperado"))
            return 1
        finally:
            if tmp_file:
                self._limpiar_archivo_temporal(tmp_file)
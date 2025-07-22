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

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cobra.transpilers import module_map
from core.interpreter import InterpretadorCobra
from core.sandbox import validar_dependencias
from core.semantic_validators import PrimitivaPeligrosaError, construir_cadena

from src.cli.commands.base import BaseCommand
from src.cli.commands.execute_cmd import ExecuteCommand
from src.cli.i18n import _
from src.cli.utils.messages import mostrar_error, mostrar_info


class ProfileCommand(BaseCommand):
    """Ejecuta un script Cobra con cProfile."""

    name = "profile"

    def register_subparser(self, subparsers):
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

    def run(self, args):
        """Ejecuta la lógica del comando."""
        archivo = args.archivo
        output = getattr(args, "output", None)
        ui = getattr(args, "ui", None)
        depurar = getattr(args, "depurar", False)
        formatear = getattr(args, "formatear", False)
        seguro = getattr(args, "seguro", False)
        extra_validators = getattr(args, "validadores_extra", None)
        analysis = getattr(args, "analysis", False)

        if not os.path.exists(archivo):
            mostrar_error(f"El archivo '{archivo}' no existe")
            return 1

        try:
            validar_dependencias("python", module_map.get_toml_map())
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1
        if formatear:
            ExecuteCommand._formatear_codigo(archivo)  # type: ignore[attr-defined]
        if depurar:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.ERROR)

        with open(archivo, "r", encoding="utf-8") as f:
            codigo = f.read()

        tokens = Lexer(codigo).tokenizar(profile=analysis)
        ast = Parser(tokens).parsear(profile=analysis)
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
                logging.error(f"Primitiva peligrosa: {pe}")
                mostrar_error(str(pe))
                return 1

        profiler = cProfile.Profile()
        try:
            profiler.enable()
            InterpretadorCobra(
                safe_mode=seguro, extra_validators=extra_validators
            ).ejecutar_ast(ast)
            profiler.disable()
            stats_file = output
            if ui:
                if shutil.which(ui) is None:
                    msg = _(
                        "Herramienta {tool} no encontrada. "
                        "Instálala con 'pip install {tool}'"
                    ).format(tool=ui)
                    mostrar_error(msg)
                    return 1
                if not stats_file:
                    tmp = tempfile.NamedTemporaryFile(suffix=".prof", delete=False)
                    stats_file = tmp.name
                profiler.dump_stats(stats_file)
                try:
                    subprocess.run([ui, stats_file], check=False)
                except FileNotFoundError:
                    msg = _(
                        "Herramienta {tool} no encontrada. "
                        "Instálala con 'pip install {tool}'"
                    ).format(tool=ui)
                    mostrar_error(msg)
                    return 1
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
        except Exception as e:
            logging.error(f"Error ejecutando el script: {e}")
            mostrar_error(f"Error ejecutando el script: {e}")
            return 1

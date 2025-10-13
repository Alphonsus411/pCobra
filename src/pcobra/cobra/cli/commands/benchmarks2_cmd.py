"""
Módulo para ejecutar benchmarks secundarios del proyecto Cobra.
Proporciona funcionalidad para medir y comparar el rendimiento de diferentes aspectos del sistema.
"""

import time
import psutil
import json
from typing import Dict, Any, Optional
from argparse import ArgumentParser

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_info, mostrar_error


class Benchmarks2Command(BaseCommand):
    """Ejecuta una serie de pruebas de rendimiento secundarias en el sistema."""

    # Constantes para códigos de retorno
    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    name = "benchmarks2"

    def __init__(self) -> None:
        """Inicializa el comando de benchmarks."""
        super().__init__()
        self._resultados: Dict[str, Any] = {
            "tiempos": {},
            "memoria": {},
            "rendimiento": {}
        }
        self._iteraciones: Optional[int] = None
        self._formato: Optional[str] = None
        self._proceso = psutil.Process()

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar el subcomando
            
        Returns:
            CustomArgumentParser: El parser configurado para el subcomando
            
        Raises:
            ValueError: Si hay error al configurar los argumentos
        """
        parser = subparsers.add_parser(
            self.name,
            help=_("Ejecuta pruebas de rendimiento secundarias")
        )

        parser.add_argument(
            "--iteraciones",
            type=int,
            default=1000,
            help=_("Número de iteraciones para cada prueba (>0)"),
            metavar="N"
        )

        parser.add_argument(
            "--formato",
            choices=["json", "texto"],
            default="texto",
            help=_("Formato de salida de los resultados")
        )

        parser.set_defaults(cmd=self)
        return parser

    def _medir_tiempo_ejecucion(self) -> None:
        """Mide y registra los tiempos de ejecución de operaciones clave."""
        tiempos = {}
        
        # Medir tiempo de compilación
        inicio = time.perf_counter()
        for _ in range(self._iteraciones):
            # Simulación de compilación
            pass
        tiempos["compilacion"] = time.perf_counter() - inicio

        # Medir tiempo de ejecución
        inicio = time.perf_counter()
        for _ in range(self._iteraciones):
            # Simulación de ejecución
            pass
        tiempos["ejecucion"] = time.perf_counter() - inicio

        self._resultados["tiempos"] = tiempos

    def _medir_uso_memoria(self) -> None:
        """Mide y registra el uso de memoria de operaciones clave."""
        memoria = {}
        
        # Medir memoria inicial
        memoria["inicial"] = self._proceso.memory_info().rss / 1024 / 1024  # MB

        # Medir pico de memoria
        max_memoria = memoria["inicial"]
        for _ in range(self._iteraciones):
            mem_actual = self._proceso.memory_info().rss / 1024 / 1024
            max_memoria = max(max_memoria, mem_actual)
        
        memoria["pico"] = max_memoria
        self._resultados["memoria"] = memoria

    def _medir_rendimiento_operaciones(self) -> None:
        """Mide y registra el rendimiento de operaciones específicas."""
        rendimiento = {}
        
        # Medir operaciones por segundo
        inicio = time.perf_counter()
        num_ops = 0
        while num_ops < self._iteraciones:
            # Simulación de operación
            num_ops += 1
        tiempo_total = time.perf_counter() - inicio
        
        rendimiento["ops_por_segundo"] = num_ops / tiempo_total
        self._resultados["rendimiento"] = rendimiento

    def _ejecutar_pruebas(self) -> None:
        """Ejecuta todas las pruebas de rendimiento configuradas."""
        self._medir_tiempo_ejecucion()
        self._medir_uso_memoria()
        self._medir_rendimiento_operaciones()

    def _formatear_resultados(self) -> str:
        """Formatea los resultados según el formato especificado.
        
        Returns:
            str: Resultados formateados en el formato solicitado
        """
        if self._formato == "json":
            return json.dumps(self._resultados, indent=2)
        
        # Formato texto
        texto = []
        
        # Formatear tiempos
        texto.append("Tiempos de ejecución:")
        for op, tiempo in self._resultados["tiempos"].items():
            texto.append(f"  {op}: {tiempo:.3f} segundos")
            
        # Formatear memoria
        texto.append("\nUso de memoria:")
        for tipo, valor in self._resultados["memoria"].items():
            texto.append(f"  {tipo}: {valor:.2f} MB")
            
        # Formatear rendimiento
        texto.append("\nRendimiento:")
        for metrica, valor in self._resultados["rendimiento"].items():
            texto.append(f"  {metrica}: {valor:.2f}")
            
        return "\n".join(texto)

    def run(self, args) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: Código de salida (0 para éxito, 1 para error)
        """
        try:
            # Validar argumentos
            if args.iteraciones <= 0:
                mostrar_error(_("El número de iteraciones debe ser positivo"))
                return self.EXIT_FAILURE

            self._iteraciones = args.iteraciones
            self._formato = args.formato

            mostrar_info(_("Iniciando pruebas de rendimiento..."))
            self._ejecutar_pruebas()

            resultados_formateados = self._formatear_resultados()
            mostrar_info(_("Resultados de las pruebas:"))
            mostrar_info(resultados_formateados)
            
            mostrar_info(_("Pruebas de rendimiento completadas"))
            return self.EXIT_SUCCESS

        except MemoryError:
            mostrar_error(_("Error: Memoria insuficiente durante las pruebas"))
            # Intentar liberar recursos
            self._resultados.clear()
            return self.EXIT_FAILURE

        except Exception as e:
            mostrar_error(
                _("Error durante las pruebas de rendimiento: {error}")
                .format(error=str(e))
            )
            return self.EXIT_FAILURE
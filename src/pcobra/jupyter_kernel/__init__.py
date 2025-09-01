"""Kernel de Jupyter que permite ejecutar código Cobra en notebooks."""

import sys
import io
import os
import contextlib
from importlib.metadata import PackageNotFoundError, version
from ipykernel.kernelbase import Kernel
from pcobra.cobra.core import Lexer, Parser
from pcobra.cobra.core.utils import PALABRAS_RESERVADAS
from core.interpreter import InterpretadorCobra
from core.qualia_bridge import get_suggestions
from core.sandbox import ejecutar_en_sandbox


def _get_version() -> str:
    """Obtiene la versión instalada del paquete."""
    try:
        return version("cobra-lenguaje")
    except PackageNotFoundError:
        return "10.0.9"


__version__ = _get_version()


def install(user=True):
    """Instala el kernel de Cobra para Jupyter."""
    from jupyter_client.kernelspec import install as jupyter_install

    return jupyter_install(user=user, kernel_name="cobra", display_name="Cobra")


class CobraKernel(Kernel):
    implementation = "Cobra"
    implementation_version = __version__
    language = "cobra"
    language_version = __version__
    language_info = {
        "name": "cobra",
        "mimetype": "text/plain",
        "file_extension": ".co",
    }
    banner = "Cobra kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interpreter = InterpretadorCobra()
        self.use_python = os.getenv("COBRA_JUPYTER_PYTHON", "").lower() in {
            "1",
            "true",
            "yes",
        }
        self._warned_python = False

    def do_execute(
        self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        if code.strip() == "%sugerencias":
            texto = "\n".join(get_suggestions())
            if not silent:
                self.send_response(
                    self.iopub_socket, "stream", {"name": "stdout", "text": texto}
                )
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }

        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                tokens = Lexer(code).tokenizar()
                ast = Parser(tokens).parsear()
                if self.use_python:
                    from pcobra.cobra.transpilers.transpiler.to_python import (
                        TranspiladorPython,
                    )

                    py_code = TranspiladorPython().generate_code(ast)
                    if not self._warned_python and not silent:
                        self.send_response(
                            self.iopub_socket,
                            "stream",
                            {
                                "name": "stderr",
                                "text": (
                                    "Advertencia: se ejecutará código Python; esto puede ser inseguro.\n"
                                ),
                            },
                        )
                        self._warned_python = True
                    try:
                        output = ejecutar_en_sandbox(
                            py_code, timeout=5, memoria_mb=64
                        )
                        error = ""
                        result = None
                    except TimeoutError:
                        output = ""
                        error = (
                            "Error: la ejecución de Python excedió el tiempo límite de 5 segundos"
                        )
                        result = None
                    except MemoryError:
                        output = ""
                        error = (
                            "Error: la ejecución de Python excedió el límite de memoria"
                        )
                        result = None
                    except Exception as exc:
                        output = ""
                        error = f"Error al ejecutar código Python: {exc}"
                        result = None
                else:
                    result = self.interpreter.ejecutar_ast(ast)
                    output = stdout.getvalue()
                    error = ""

            if not silent:
                if output:
                    self.send_response(
                        self.iopub_socket, "stream", {"name": "stdout", "text": output}
                    )
                if error:
                    self.send_response(
                        self.iopub_socket, "stream", {"name": "stderr", "text": error}
                    )
                if result is not None and not output and not error:
                    self.send_response(
                        self.iopub_socket,
                        "execute_result",
                        {
                            "execution_count": self.execution_count,
                            "data": {"text/plain": str(result)},
                            "metadata": {},
                        },
                    )
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }
        except Exception as e:
            if not silent:
                self.send_response(
                    self.iopub_socket, "stream", {"name": "stderr", "text": f"{e}\n"}
                )
            return {
                "status": "error",
                "execution_count": self.execution_count,
                "ename": e.__class__.__name__,
                "evalue": str(e),
                "traceback": [],
            }

    def do_complete(self, code, cursor_pos):
        prefix = code[:cursor_pos].split()[-1]
        matches = [w for w in PALABRAS_RESERVADAS if w.startswith(prefix)]
        matches += [
            n
            for n in self.interpreter.variables.keys()
            if isinstance(n, str) and n.startswith(prefix)
        ]
        start = cursor_pos - len(prefix)
        return {
            "matches": matches,
            "cursor_start": start,
            "cursor_end": cursor_pos,
            "metadata": {},
            "status": "ok",
        }


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install()


if __name__ == "__main__":
    main()

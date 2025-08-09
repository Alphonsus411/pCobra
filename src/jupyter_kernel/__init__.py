"""Kernel de Jupyter que permite ejecutar código Cobra en notebooks."""

import sys
import io
import os
import subprocess
import contextlib
from importlib.metadata import PackageNotFoundError, version
from ipykernel.kernelbase import Kernel
from cobra.core import Lexer
from cobra.core import Parser
from cobra.core.utils import PALABRAS_RESERVADAS
from core.interpreter import InterpretadorCobra
from core.qualia_bridge import get_suggestions


def _get_version() -> str:
    """Obtiene la versión instalada del paquete."""
    try:
        return version("cobra-lenguaje")
    except PackageNotFoundError:
        return "10.0.6"


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
                    from cobra.transpilers.transpiler.to_python import (
                        TranspiladorPython,
                    )

                    py_code = TranspiladorPython().generate_code(ast)
                    proc = subprocess.run(
                        [sys.executable, "-"],
                        input=py_code,
                        capture_output=True,
                        text=True,
                    )
                    output = proc.stdout
                    error = proc.stderr
                    if proc.returncode != 0 and not error:
                        error = (
                            f"Error al ejecutar código Python (código de retorno {proc.returncode})"
                        )
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

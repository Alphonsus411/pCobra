"""Kernel de Jupyter que permite ejecutar código Cobra en notebooks."""

import sys
import io
import os
import contextlib
import importlib
from importlib.metadata import PackageNotFoundError, version
from ipykernel.kernelbase import Kernel


def _importar_modulo_runtime(
    canonical: str,
    *,
    legacy: str | None = None,
    atributos_requeridos: tuple[str, ...] = (),
):
    """Importa un módulo runtime priorizando namespace canónico y valida atributos."""

    try:
        modulo = importlib.import_module(canonical)
    except ModuleNotFoundError as canon_exc:
        if legacy is None:
            raise
        try:
            modulo = importlib.import_module(legacy)
        except ModuleNotFoundError:
            raise canon_exc

    faltantes = [attr for attr in atributos_requeridos if not hasattr(modulo, attr)]
    if faltantes:
        raise ImportError(
            f"El módulo '{modulo.__name__}' no expone atributos requeridos: {', '.join(faltantes)}"
        )
    return modulo


def _resolver_dependencias_kernel() -> dict[str, object]:
    """Resuelve dependencias del kernel con prioridad en imports canónicos."""

    core_mod = _importar_modulo_runtime(
        "pcobra.cobra.core",
        legacy="cobra.core",
        atributos_requeridos=("Lexer", "Parser"),
    )
    core_utils_mod = _importar_modulo_runtime(
        "pcobra.cobra.core.utils",
        legacy="cobra.core.utils",
        atributos_requeridos=("PALABRAS_RESERVADAS",),
    )
    interpreter_mod = _importar_modulo_runtime(
        "pcobra.core.interpreter",
        legacy="core.interpreter",
        atributos_requeridos=("InterpretadorCobra",),
    )
    qualia_mod = _importar_modulo_runtime(
        "pcobra.core.qualia_bridge",
        legacy="core.qualia_bridge",
        atributos_requeridos=("get_suggestions",),
    )
    sandbox_mod = _importar_modulo_runtime(
        "pcobra.core.sandbox",
        legacy="core.sandbox",
        atributos_requeridos=("ejecutar_en_sandbox",),
    )
    return {
        "Lexer": core_mod.Lexer,
        "Parser": core_mod.Parser,
        "PALABRAS_RESERVADAS": core_utils_mod.PALABRAS_RESERVADAS,
        "InterpretadorCobra": interpreter_mod.InterpretadorCobra,
        "get_suggestions": qualia_mod.get_suggestions,
        "sandbox": sandbox_mod,
    }


def _get_version() -> str:
    """Obtiene la versión instalada del paquete."""
    try:
        return version("pcobra")
    except PackageNotFoundError:
        return "10.0.12"


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
        deps = _resolver_dependencias_kernel()
        self._lexer_cls = deps["Lexer"]
        self._parser_cls = deps["Parser"]
        self._palabras_reservadas = deps["PALABRAS_RESERVADAS"]
        self._get_suggestions = deps["get_suggestions"]
        self._sandbox = deps["sandbox"]
        self.interpreter = deps["InterpretadorCobra"]()
        if not hasattr(self, "execution_count"):
            self.execution_count = 0
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
            texto = "\n".join(self._get_suggestions())
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
                tokens = self._lexer_cls(code).tokenizar()
                ast = self._parser_cls(tokens).parsear()
                python_error: Exception | None = None
                if self.use_python:
                    try:
                        from pcobra.cobra.transpilers.transpiler.to_python import (
                            TranspiladorPython,
                        )

                        py_code = TranspiladorPython().generate_code(ast)
                    except (ImportError, ModuleNotFoundError) as exc:
                        python_error = exc
                    else:
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
                            output = self._sandbox.ejecutar_en_sandbox(
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
                            if isinstance(exc, ModuleNotFoundError):
                                python_error = exc
                            else:
                                output = ""
                                error = f"Error al ejecutar código Python: {exc}"
                                result = None
                if not self.use_python or python_error is not None:
                    if python_error is not None and not silent:
                        self.send_response(
                            self.iopub_socket,
                            "stream",
                            {
                                "name": "stderr",
                                "text": (
                                    "Advertencia: modo Python no disponible, se usa el intérprete nativo.\n"
                                ),
                            },
                        )
                    result = self.interpreter.ejecutar_ast(ast)
                    output = stdout.getvalue()
                    error = ""
                    if python_error is not None and not output and result is None:
                        try:
                            output = self._sandbox.ejecutar_en_sandbox(
                                "# Python fallback deshabilitado",
                                timeout=5,
                                memoria_mb=64,
                            )
                        except Exception:
                            output = ""

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
        matches = [w for w in self._palabras_reservadas if w.startswith(prefix)]
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

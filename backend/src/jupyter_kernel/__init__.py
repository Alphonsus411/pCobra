import sys
import io
import contextlib
from ipykernel.kernelbase import Kernel
from src.cobra.lexico.lexer import Lexer
from src.cobra.parser.parser import Parser, PALABRAS_RESERVADAS
from src.core.interpreter import InterpretadorCobra
from src.core.qualia_bridge import get_suggestions


def install(user=True):
    """Instala el kernel de Cobra para Jupyter."""
    from ipykernel.kernelspec import install as ipy_install
    return ipy_install(user=user, kernel_name="cobra", display_name="Cobra")


class CobraKernel(Kernel):
    implementation = "Cobra"
    implementation_version = "2.3"
    language = "cobra"
    language_version = "2.3"
    language_info = {
        "name": "cobra",
        "mimetype": "text/plain",
        "file_extension": ".co",
    }
    banner = "Cobra kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interpreter = InterpretadorCobra()

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        if code.strip() == "%sugerencias":
            texto = "\n".join(get_suggestions())
            if not silent:
                self.send_response(self.iopub_socket, "stream", {"name": "stdout", "text": texto})
            return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                tokens = Lexer(code).tokenizar()
                ast = Parser(tokens).parsear()
                result = self.interpreter.ejecutar_ast(ast)
            output = stdout.getvalue()
            if not silent:
                if output:
                    self.send_response(self.iopub_socket, "stream", {"name": "stdout", "text": output})
                if result is not None and not output:
                    self.send_response(self.iopub_socket, "execute_result", {
                        "execution_count": self.execution_count,
                        "data": {"text/plain": str(result)},
                        "metadata": {},
                    })
            return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
        except Exception as e:
            if not silent:
                self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": f"{e}\n"})
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
        matches += [n for n in self.interpreter.variables.keys() if isinstance(n, str) and n.startswith(prefix)]
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

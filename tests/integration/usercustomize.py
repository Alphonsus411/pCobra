import os
import subprocess
from subprocess import CompletedProcess

if os.environ.get("PEXPECT_TESTING"):
    def fake_run(cmd, *args, **kwargs):
        print(f"FAKE_RUN {cmd[0]}")
        return CompletedProcess(cmd, 0)
    subprocess.run = fake_run
    try:
        import core.sandbox as sandbox

        def fake_sandbox(code: str) -> None:
            print("hola")

        sandbox.ejecutar_en_sandbox = fake_sandbox
    except Exception:
        pass

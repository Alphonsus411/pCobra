import json
import os
import sys

import pcobra.jupyter_kernel as jupyter_kernel
from pcobra.jupyter_kernel import __main__ as jupyter_kernel_main


def test_main_instala_kernelspec_cobra(monkeypatch):
    llamada = {}

    class KernelSpecManagerDoble:
        def install_kernel_spec(self, source_dir, *, kernel_name, user):
            llamada["source_dir"] = source_dir
            llamada["kernel_name"] = kernel_name
            llamada["user"] = user
            with open(f"{source_dir}/kernel.json", encoding="utf-8") as spec_file:
                llamada["kernel_json"] = json.load(spec_file)

    monkeypatch.setattr(jupyter_kernel, "KernelSpecManager", KernelSpecManagerDoble)
    monkeypatch.setattr(sys, "argv", ["pcobra.jupyter_kernel", "install"])

    assert jupyter_kernel_main.main() == 0
    assert llamada["kernel_name"] == "cobra"
    assert llamada["user"] is True
    assert llamada["kernel_json"]["display_name"] == "Cobra"
    assert llamada["kernel_json"]["argv"][-2:] == ["-f", "{connection_file}"]
    assert not os.path.exists(llamada["source_dir"])

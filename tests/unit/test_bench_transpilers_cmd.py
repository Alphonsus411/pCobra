import json
import time
from pathlib import Path

import pytest

from src.cli.plugin import PluginCommand
from src.cli import cli as cli_mod


class DummyTranspiler:
    def generate_code(self, ast):
        return "codigo"


class DummyBenchTranspilersCommand(PluginCommand):
    name = "benchtranspilers"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Bench transpilers")
        parser.add_argument("--output", "-o", required=True)
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        transpilers = {"py": DummyTranspiler()}
        results = []
        for lang, transp in transpilers.items():
            start = time.perf_counter()
            code = transp.generate_code([])
            elapsed = time.perf_counter() - start
            results.append({"lang": lang, "size": len(code), "time": elapsed})
        Path(args.output).write_text(json.dumps(results))
        return 0


@pytest.mark.timeout(20)
def test_benchtranspilers_generates_json(tmp_path, monkeypatch):
    monkeypatch.setattr(DummyTranspiler, "generate_code", lambda self, ast: "x")
    monkeypatch.setattr(cli_mod, "descubrir_plugins", lambda: [DummyBenchTranspilersCommand()])
    from src.cli.cli import main
    salida = tmp_path / "res.json"
    main(["benchtranspilers", "--output", str(salida)])
    data = json.loads(salida.read_text())
    assert isinstance(data, list) and data
    keys = data[0].keys()
    assert {"size", "lang", "time"}.issubset(keys)

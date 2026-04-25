from pathlib import Path

import pcobra.cli as cli


def test_bootstrap_path_usa_alias_cobra_si_no_existe_pcobra(monkeypatch):
    repo_root = Path(cli.__file__).resolve().parents[2]
    scripts_bin = str(repo_root / "scripts" / "bin")
    base_path = "/tmp/bin-a:/tmp/bin-b"

    monkeypatch.setenv("PATH", base_path)
    monkeypatch.delenv("PCOBRA_CLI_BOOTSTRAP_PATH", raising=False)
    monkeypatch.setenv("COBRA_CLI_BOOTSTRAP_PATH", "1")

    cli._bootstrap_dev_path_si_opt_in()

    assert cli.os.environ["PATH"].split(cli.os.pathsep)[0] == scripts_bin


def test_bootstrap_path_prioriza_pcobra_sobre_alias(monkeypatch):
    base_path = "/tmp/bin-a:/tmp/bin-b"

    monkeypatch.setenv("PATH", base_path)
    monkeypatch.setenv("PCOBRA_CLI_BOOTSTRAP_PATH", "0")
    monkeypatch.setenv("COBRA_CLI_BOOTSTRAP_PATH", "1")

    cli._bootstrap_dev_path_si_opt_in()

    assert cli.os.environ["PATH"] == base_path

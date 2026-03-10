from pcobra.cobra.cli.commands.bench_cmd import BACKENDS as BENCH_BACKENDS
from pcobra.cobra.cli.commands.benchmarks_cmd import BACKENDS as BENCHMARKS_BACKENDS
from pcobra.cobra.cli.commands.compile_cmd import LANG_CHOICES
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import EXTENSIONES_POR_LENGUAJE
from pcobra.cobra.transpilers.common.utils import STANDARD_IMPORTS
from pcobra.cobra.transpilers.reverse.policy import REVERSE_SCOPE_LANGUAGES
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def test_cli_y_transpilers_no_exponen_targets_fuera_de_whitelist_oficial():
    oficiales = set(OFFICIAL_TARGETS)

    assert set(LANG_CHOICES).issubset(oficiales)
    assert set(STANDARD_IMPORTS.keys()).issubset(oficiales)
    assert set(BENCH_BACKENDS.keys()).issubset(oficiales)
    assert set(BENCHMARKS_BACKENDS.keys()).issubset(oficiales)


def test_mapa_reverse_extensions_esta_alineado_con_scope_reverse():
    assert set(EXTENSIONES_POR_LENGUAJE.keys()) == set(REVERSE_SCOPE_LANGUAGES)

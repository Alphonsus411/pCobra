from scripts.benchmarks.targets_policy import (
    BENCHMARK_BACKEND_METADATA,
    executable_benchmark_backends,
)


def test_executable_benchmark_backends_por_defecto_solo_runtime_oficial():
    assert executable_benchmark_backends(BENCHMARK_BACKEND_METADATA) == (
        "python",
        "rust",
        "javascript",
        "cpp",
    )


def test_executable_benchmark_backends_best_effort_explicito_agrega_go_java_sin_transpilation_only():
    assert executable_benchmark_backends(
        BENCHMARK_BACKEND_METADATA,
        include_experimental=True,
    ) == (
        "python",
        "rust",
        "javascript",
        "go",
        "cpp",
        "java",
    )

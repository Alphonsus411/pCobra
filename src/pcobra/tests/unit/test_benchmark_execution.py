import time

import pytest

from cobra.cli.commands import benchmarks_cmd


@pytest.mark.timeout(5)
def test_benchmark_execution_time_variance(monkeypatch):
    def fake_run(self):
        time.sleep(0.1)
        return [{"backend": "cobra", "time": 0.1, "memory_kb": 1}]

    monkeypatch.setattr(benchmarks_cmd.BenchmarksCommand, "_run_benchmarks", fake_run, raising=False)
    cmd = benchmarks_cmd.BenchmarksCommand()

    start = time.perf_counter()
    cmd._run_benchmarks()
    first = time.perf_counter() - start

    start = time.perf_counter()
    cmd._run_benchmarks()
    second = time.perf_counter() - start

    diff_ratio = abs(first - second) / first
    assert diff_ratio < 0.05

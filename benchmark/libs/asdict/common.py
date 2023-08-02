from dataclasses import asdict

import pyperf

from benchmark.common import AbstractBenchmark
from benchmark.libs.mashumaro.common import Issue


class Benchmark(AbstractBenchmark):
    LIBRARY = "asdict"

    def warmup(self, data) -> None:
        asdict(Issue.from_dict(data))

    def run_dumper(self, data) -> pyperf.Benchmark:
        obj = Issue.from_dict(data)
        return self._bench_dumper_func(asdict, obj)

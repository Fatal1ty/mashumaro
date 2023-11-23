from dataclasses import asdict

import pyperf

from benchmark.common import AbstractBenchmark
from benchmark.libs.mashumaro.common import BasicDecoder, DefaultDialect, Issue


class Benchmark(AbstractBenchmark):
    LIBRARY = "asdict"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.decoder = BasicDecoder(Issue, default_dialect=DefaultDialect)

    def warmup(self, data) -> None:
        asdict(self.decoder.decode(data))

    def run_dumper(self, data) -> pyperf.Benchmark:
        obj = self.decoder.decode(data)
        return self._bench_dumper_func(asdict, obj)

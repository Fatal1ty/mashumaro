import json
import pathlib
from abc import ABC
from typing import Any, Dict, Literal, Type

import pyperf


def load_data():
    with open(pathlib.Path(__file__).parent / "data" / "issue.json") as f:
        return json.load(f)


class AbstractBenchmark(ABC):
    LIBRARY: str

    def __init__(self, runner: pyperf.Runner) -> None:
        self.runner = runner

    def warmup(self, data: Dict[str, Any]) -> None:
        pass

    def run_loader(self, data: Dict[str, Any]) -> pyperf.Benchmark:
        pass

    def run_dumper(self, data: Dict[str, Any]) -> pyperf.Benchmark:
        pass

    def _bench_loader_func(self, func, *args, **kwargs) -> pyperf.Benchmark:
        return self.runner.bench_func(
            self.get_name("load"), func, *args, **kwargs
        )

    def _bench_dumper_func(self, func, *args, **kwargs) -> pyperf.Benchmark:
        return self.runner.bench_func(
            self.get_name("dump"), func, *args, **kwargs
        )

    def get_name(self, bench_type: Literal["dump", "load"]) -> str:
        return f"{self.LIBRARY}[{bench_type}]"


class BenchmarkRunner:
    def __init__(self, benchmark_cls: Type[AbstractBenchmark]) -> None:
        self._runner = pyperf.Runner()
        self._benchmark = benchmark_cls(self._runner)
        self._data = load_data()

    def run(self, benchmark_type: str) -> None:
        self._benchmark.warmup(self._data)
        if benchmark_type == "load":
            self._benchmark.run_loader(self._data)
        elif benchmark_type == "dump":
            self._benchmark.run_dumper(self._data)
        else:
            raise ValueError(f"Unknown benchmark_type: {benchmark_type}")

from benchmark.common import BenchmarkRunner
from benchmark.libs.dataclasses_json.common import Benchmark

BenchmarkRunner(Benchmark).run("load")

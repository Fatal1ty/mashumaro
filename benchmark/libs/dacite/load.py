from benchmark.common import BenchmarkRunner
from benchmark.libs.dacite.common import Benchmark

BenchmarkRunner(Benchmark).run("load")

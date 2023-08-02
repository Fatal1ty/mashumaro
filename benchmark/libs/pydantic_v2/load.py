from benchmark.common import BenchmarkRunner
from benchmark.libs.pydantic_v2.common import Benchmark

BenchmarkRunner(Benchmark).run("load")

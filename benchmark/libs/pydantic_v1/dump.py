from benchmark.common import BenchmarkRunner
from benchmark.libs.pydantic_v1.common import Benchmark

BenchmarkRunner(Benchmark).run("dump")

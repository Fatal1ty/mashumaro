import json
from pathlib import Path

from pyperf import Benchmark


def create_spec(benchmark_type: str) -> None:
    data_dir = Path(Path.cwd() / "benchmark" / "data")
    with open(data_dir / "spec_template.json") as f:
        spec = json.load(f)
    if benchmark_type == "load":
        spec["title"]["text"] = "Creating GitHub Issue object from dict"
    elif benchmark_type == "dump":
        spec["title"]["text"] = "Converting GitHub Issue object to dict"
    values = spec["data"]["values"]

    for file in Path(Path.cwd() / "benchmark" / "data" / "results").glob(
        f"{benchmark_type}_*.json"
    ):
        benchmark: Benchmark = Benchmark.load(str(file))
        library_name = benchmark.get_name()[:-6]
        values.append(
            {
                "library": library_name,
                "time": benchmark.mean(),
                "timeFormat": benchmark.format_value(benchmark.mean()),
            }
        )
    values.sort(key=lambda v: v["time"])

    with open(data_dir / f"spec_{benchmark_type}.json", "w") as f:
        json.dump(spec, f)


if __name__ == "__main__":
    create_spec("load")
    create_spec("dump")

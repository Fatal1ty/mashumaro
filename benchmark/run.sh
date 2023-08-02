#!/bin/bash

set -e
export PYTHONPATH=$PYTHONPATH:.
rm -rf benchmark/data/results
mkdir -p benchmark/data/results

for library_name in mashumaro cattrs pydantic_v2 pydantic_v1 marshmallow dataclasses_json dacite asdict; do
    if [ -f "benchmark/libs/$library_name/load.py" ]; then
        python benchmark/libs/$library_name/load.py -o benchmark/data/results/load_$library_name.json
    fi
    if [ -f "benchmark/libs/$library_name/dump.py" ]; then
        python benchmark/libs/$library_name/dump.py -o benchmark/data/results/dump_$library_name.json
    fi
done

python benchmark/create_chart_specs.py
echo "You can now render chart specs with https://vega.github.io/editor/
  * benchmark/data/spec_load.json
  * benchmark/data/spec_dump.json"

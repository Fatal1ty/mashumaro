default: build lint

build:
    pip install -r requirements-dev.txt
    pip install -e .

lint:
    ruff check mashumaro
    black --check mashumaro
    mypy mashumaro
    codespell mashumaro tests README.md .github/*.md

format:
    black mashumaro

test:
    pytest -n auto tests

test-with-coverage:
    pytest --cov . tests

benchmark:
    ./benchmark/run.sh

clean:
    rm -rf benchmark/data/results
    rm -f benchmark/data/spec_dump.json
    rm -f benchmark/data/spec_load.json

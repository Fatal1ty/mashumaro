default: build lint

build:
    pip install -r requirements-dev.txt
    pip install -e .

lint:
    ruff mashumaro
    black --check mashumaro
    mypy mashumaro
    codespell mashumaro tests README.md .github/*.md

format:
    black mashumaro

test:
    pytest tests

test-with-coverage:
    pytest --cov . tests

benchmark:
    ./benchmark/run.sh

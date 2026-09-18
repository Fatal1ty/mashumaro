default: build lint

build:
    pip install -r requirements-dev.txt
    pip install -e .

lint:
    ruff check mashumaro
    black --check mashumaro tests
    mypy mashumaro
    codespell mashumaro tests README.md .github/*.md

format:
    black mashumaro tests
    isort mashumaro tests

test:
    pytest tests

test-fast:
    pytest tests -n auto

test-with-coverage:
    pytest --cov . tests

benchmark:
    ./benchmark/run.sh

[arg("serve", long, value="true", help="Start the preview server after building")]
[continue]
docs serve="false":
    @python web/build.py
    @if [ "{{ serve }}" = "true" ]; then python -m http.server --bind 127.0.0.1 --directory web/dist 8000; fi

[continue]
docs-serve:
    @python -m http.server --bind 127.0.0.1 --directory web/dist 8000

clean:
    rm -rf benchmark/data/results
    rm -f benchmark/data/spec_dump.json
    rm -f benchmark/data/spec_load.json

import os
import sys
import timeit

import matplotlib.pyplot as plt
import termtables as tt
from pytablewriter import HtmlTableWriter

sys.path.append(os.getcwd())

REPETITIONS = 5
NUMBER = 100
SHOW_PLOT = False
SHOW_HTML_TABLE = False
SAVE_PLOT = False

print("Run mashumaro_from_dict")
mashumaro_from_dict = min(
    timeit.repeat(
        "MASHUMAROClass.from_dict(sample)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.mashumaro_setup import MASHUMAROClass;"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run mashumaro_to_dict")
mashumaro_to_dict = min(
    timeit.repeat(
        "obj.to_dict()",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.mashumaro_setup import MASHUMAROClass;"
            "obj = MASHUMAROClass.from_dict(sample);"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run cattrs_from_dict")
cattrs_from_dict = min(
    timeit.repeat(
        "converter.structure(sample, CATTRClass)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.cattr_setup import CATTRClass, converter;"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run cattrs_to_dict")
cattrs_to_dict = min(
    timeit.repeat(
        "converter.unstructure(obj)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.cattr_setup import CATTRClass, converter;"
            "obj = converter.structure(sample, CATTRClass);"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run pydantic_from_dict")
pydantic_from_dict = min(
    timeit.repeat(
        "PYDANTICClass(**sample)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.pydantic_setup import PYDANTICClass;"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run pydantic_to_dict")
pydantic_to_dict = min(
    timeit.repeat(
        "obj.dict()",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.pydantic_setup import PYDANTICClass;"
            "obj = PYDANTICClass(**sample);"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run dacite_from_dict")
dacite_from_dict = min(
    timeit.repeat(
        "from_dict(DACITEClass, sample, config)",
        setup=(
            "from benchmark.sample import sample_2 as sample;"
            "from benchmark.dacite_setup import DACITEClass;"
            "from dacite import from_dict, Config;"
            "config = Config(check_types=False);"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run dataclasses_to_dict")
dataclasses_to_dict = min(
    timeit.repeat(
        "asdict(obj)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.mashumaro_setup import MASHUMAROClass;"
            "obj = MASHUMAROClass.from_dict(sample);"
            "from dataclasses import asdict"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run marshmallow_from_dict")
marshmallow_from_dict = min(
    timeit.repeat(
        "schema.load(sample, unknown='EXCLUDE')",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.marshmallow_setup import MARSHMALLOWClass;"
            "schema = MARSHMALLOWClass();"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)
print("Run marshmallow_to_dict")
marshmallow_to_dict = min(
    timeit.repeat(
        "schema.dump(obj)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.marshmallow_setup import MARSHMALLOWClass;"
            "schema = MARSHMALLOWClass();"
            "obj = schema.load(sample, unknown='EXCLUDE');"
        ),
        repeat=REPETITIONS,
        number=NUMBER,
    )
)


# Print table

slowdown = {
    "cattrs": [
        f"{round(cattrs_from_dict / mashumaro_from_dict, 2)}x",
        f"{round(cattrs_to_dict / mashumaro_to_dict, 2)}x",
    ],
    "pydantic": [
        f"{round(pydantic_from_dict / mashumaro_from_dict, 2)}x",
        f"{round(pydantic_to_dict / mashumaro_to_dict, 2)}x",
    ],
    "marshmallow": [
        f"{round(marshmallow_from_dict / mashumaro_from_dict, 2)}x",
        f"{round(marshmallow_to_dict / mashumaro_to_dict, 2)}x",
    ],
    "dataclasses": [
        "—",
        f"{round(dataclasses_to_dict / mashumaro_to_dict, 2)}x",
    ],
    "dacite": [f"{round(dacite_from_dict / mashumaro_from_dict, 2)}x", "—"],
}

header = [
    "Framework",
    "From dict",
    "To dict",
    "Slowdown factor (from dict / to dict)",
]
data = [
    ["mashumaro", mashumaro_from_dict, mashumaro_to_dict, "1x"],
    [
        "cattrs",
        cattrs_from_dict,
        cattrs_to_dict,
        " / ".join(slowdown["cattrs"]),
    ],
    [
        "pydantic",
        pydantic_from_dict,
        pydantic_to_dict,
        " / ".join(slowdown["pydantic"]),
    ],
    [
        "marshmallow",
        marshmallow_from_dict,
        marshmallow_to_dict,
        " / ".join(slowdown["marshmallow"]),
    ],
    [
        "dataclasses",
        "—",
        dataclasses_to_dict,
        " / ".join(slowdown["dataclasses"]),
    ],
    ["dacite", dacite_from_dict, "—", " / ".join(slowdown["dacite"])],
]
tt.print(data, header=header)

writer = HtmlTableWriter(
    table_name="Comp",
    headers=[
        "Framework",
        "From dict time",
        "Slowdown factor",
        "To dict time",
        "Slowdown factor",
    ],
    value_matrix=[
        ["mashumaro", mashumaro_from_dict, "1x", mashumaro_to_dict, "1x"],
        [
            "cattrs",
            cattrs_from_dict,
            slowdown["cattrs"][0],
            cattrs_to_dict,
            slowdown["cattrs"][1],
        ],
        [
            "pydantic",
            pydantic_from_dict,
            slowdown["pydantic"][0],
            pydantic_to_dict,
            slowdown["pydantic"][1],
        ],
        [
            "marshmallow",
            marshmallow_from_dict,
            slowdown["marshmallow"][0],
            marshmallow_to_dict,
            slowdown["marshmallow"][1],
        ],
        [
            "dataclasses",
            "—",
            slowdown["dataclasses"][0],
            dataclasses_to_dict,
            slowdown["dataclasses"][1],
        ],
        [
            "dacite",
            dacite_from_dict,
            slowdown["dacite"][0],
            "—",
            slowdown["dacite"][1],
        ],
    ],
)
if SHOW_HTML_TABLE:
    writer.write_table()

# Deserialization plot

fig, ax = plt.subplots()
ax.set_title("Load from dict")
ax.set_ylabel(f"Elapsed time for {NUMBER} repetitions in seconds")

y = [
    mashumaro_from_dict,
    cattrs_from_dict,
    pydantic_from_dict,
    dacite_from_dict,
    marshmallow_from_dict,
]
x = list(range(1, len(y) + 1))
labels = ["mashumaro", "cattrs", "pydantic", "dacite", "marshmallow"]

bar = plt.bar(x, height=y, tick_label=labels, label="a")
plt.title = "Load time"
if SHOW_PLOT:
    plt.show()
if SAVE_PLOT:
    fig.savefig("./load.png")

# Serialization plot

fig, ax = plt.subplots()
ax.set_title("Dump to dict")
ax.set_ylabel(f"Elapsed time for {NUMBER} repetitions in seconds")

y = [
    mashumaro_to_dict,
    cattrs_to_dict,
    pydantic_to_dict,
    dataclasses_to_dict,
    marshmallow_to_dict,
]
x = list(range(1, len(y) + 1))
labels = ["mashumaro", "cattrs", "pydantic", "dataclasses", "marshmallow"]

bar = plt.bar(x, height=y, tick_label=labels, label="a")
plt.title = "Dump time"
if SHOW_PLOT:
    plt.show()
if SAVE_PLOT:
    fig.savefig("./dump.png")

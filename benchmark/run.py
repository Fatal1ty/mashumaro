import timeit

import matplotlib.pyplot as plt
import termtables as tt
from pytablewriter import HtmlTableWriter

REPETITIONS = 1000


mashumaro_from_dict = min(
    timeit.repeat(
        "MASHUMAROClass.from_dict(sample)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.mashumaro_setup import MASHUMAROClass;"
        ),
        number=REPETITIONS,
    )
)
mashumaro_to_dict = min(
    timeit.repeat(
        "obj.to_dict()",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.mashumaro_setup import MASHUMAROClass;"
            "obj = MASHUMAROClass.from_dict(sample);"
        ),
        number=REPETITIONS,
    )
)
cattrs_from_dict = min(
    timeit.repeat(
        "converter.structure(sample, CATTRClass)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.cattr_setup import CATTRClass, converter;"
        ),
        number=REPETITIONS,
    )
)
cattrs_to_dict = min(
    timeit.repeat(
        "converter.unstructure(obj)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.cattr_setup import CATTRClass, converter;"
            "obj = converter.structure(sample, CATTRClass);"
        ),
        number=REPETITIONS,
    )
)
pydantic_from_dict = min(
    timeit.repeat(
        "PYDANTICClass(**sample)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.pydantic_setup import PYDANTICClass;"
        ),
        number=REPETITIONS,
    )
)
pydantic_to_dict = min(
    timeit.repeat(
        "obj.dict()",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.pydantic_setup import PYDANTICClass;"
            "obj = PYDANTICClass(**sample);"
        ),
        number=REPETITIONS,
    )
)
dacite_from_dict = min(
    timeit.repeat(
        "from_dict(DACITEClass, sample, Config(check_types=False))",
        setup=(
            "from benchmark.sample import sample_2 as sample;"
            "from benchmark.dacite_setup import DACITEClass;"
            "from dacite import from_dict, Config"
        ),
        number=REPETITIONS,
    )
)
dataclasses_to_dict = min(
    timeit.repeat(
        "asdict(obj)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.mashumaro_setup import MASHUMAROClass;"
            "obj = MASHUMAROClass.from_dict(sample);"
            "from dataclasses import asdict"
        ),
        number=REPETITIONS,
    )
)
marshmallow_from_dict = min(
    timeit.repeat(
        "schema.load(sample, unknown='EXCLUDE')",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.marshmallow_setup import MARSHMALLOWClass;"
            "schema = MARSHMALLOWClass();"
        ),
        number=REPETITIONS,
    )
)
marshmallow_to_dict = min(
    timeit.repeat(
        "schema.dump(obj)",
        setup=(
            "from benchmark.sample import sample_1 as sample;"
            "from benchmark.marshmallow_setup import MARSHMALLOWClass;"
            "schema = MARSHMALLOWClass();"
            "obj = schema.load(sample, unknown='EXCLUDE');"
        ),
        number=REPETITIONS,
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
writer.write_table()

# Deserialization plot

fig, ax = plt.subplots()
ax.set_title("Load from dict")
ax.set_ylabel(f"Elapsed time for {REPETITIONS} repetitions in seconds")

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
plt.show()
# fig.savefig("charts/load.png")

# Serialization plot

fig, ax = plt.subplots()
ax.set_title("Dump to dict")
ax.set_ylabel(f"Elapsed time for {REPETITIONS} repetitions in seconds")

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
plt.show()
# fig.savefig("charts/dump.png")

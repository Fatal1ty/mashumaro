from mashumaro.meta.macros import PY_37_MIN


if not PY_37_MIN:
    collect_ignore = ["test_pep_563.py"]

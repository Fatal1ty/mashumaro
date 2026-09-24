from typing import ChainMap, Deque, List, Mapping, Set, Tuple


def same_types(first, second):
    if isinstance(first, (List, Deque, Tuple)):
        return all(same_types(*x) for x in zip(first, second))
    elif isinstance(first, ChainMap):
        return all(same_types(*x) for x in zip(first.maps, second.maps))
    elif isinstance(first, Mapping):
        return all(
            same_types(*x) for x in zip(first.keys(), second.keys())
        ) and all(same_types(*x) for x in zip(first.values(), second.values()))
    elif isinstance(first, Set):
        return all(same_types(*x) for x in zip(sorted(first), sorted(second)))
    else:
        return type(first) is type(second)

from typing import ChainMap, Deque, List, Mapping, Set, Tuple


def same_types(first, second):
    if isinstance(first, (List, Deque, Tuple)):
        return all(map(lambda x: same_types(*x), zip(first, second)))
    elif isinstance(first, ChainMap):
        return all(map(lambda x: same_types(*x), zip(first.maps, second.maps)))
    elif isinstance(first, Mapping):
        return all(
            map(lambda x: same_types(*x), zip(first.keys(), second.keys()))
        ) and all(
            map(lambda x: same_types(*x), zip(first.values(), second.values()))
        )
    elif isinstance(first, Set):
        return all(
            map(lambda x: same_types(*x), zip(sorted(first), sorted(second)))
        )
    else:
        return type(first) is type(second)

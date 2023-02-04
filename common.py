def is_iterable(obj):
    return isinstance(obj, (tuple, list))


def reverse(obj):
    return tuple(reversed(obj))


def apply_to_seq_or_one(seq, func):
    if is_iterable(seq):
        return [func(element) for element in seq]
    else:
        return func(seq)


def exec_on_seq_or_one(seq, func):
    if is_iterable(seq):
        for element in seq:
            func(element)
    else:
        func(seq)


class LockedMap:
    def __init__(self, check_duplicates=True) -> None:
        self.map = {}
        self.is_locked = False
        self.check_duplicates = check_duplicates

    def lock(self):
        self.is_locked = True
        self.all = tuple(self.map.keys())

    def get(self, key):
        return self.map[key]

    def put(self, key, val):
        if self.is_locked:
            if key not in self.map:
                raise KeyError(key)

        elif self.check_duplicates:
            if key in self.map:
                raise KeyError(f'Duplicate key: {key}')

        self.map[key] = val

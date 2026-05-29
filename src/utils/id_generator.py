from itertools import count


class IdGenerator:
    """Послідовний генератор рядкових ідентифікаторів з префіксом."""

    def __init__(self, prefix):
        self._prefix = prefix
        self._counter = count(1)

    def next_id(self):
        return "{}-{:05d}".format(self._prefix, next(self._counter))

    def reset(self):
        self._counter = count(1)

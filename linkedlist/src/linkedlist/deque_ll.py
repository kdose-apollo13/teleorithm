"""
    | teleorithm |
    
    lean on the builtins
    blows away hilarious implementation based on lists
"""
from collections import deque

from klab.lab import measure


class LinkedList:
    def __init__(self):
        self._deque = deque()

    def append(self, value):
        self._deque.append(value)

    def insert(self, value):
        self._deque.appendleft(value)

    def sort(self):
        self._deque = deque(sorted(self._deque))

    def iterate_keys(self):
        for item in self._deque:
            yield item

    def search_key(self, key):
        for item in self._deque:
            if item == key:
                return item
        else:
            return None

    def delete_key(self, key):
        try:
            self._deque.remove(key)
        except ValueError:
            pass

    def pop(self):
        try:
            return self._deque.pop()
        except IndexError:
            return None

    def pop_left(self):
        try:
            return self._deque.popleft()
        except IndexError:
            return None


if __name__ == "__main__":
    ll = LinkedList()
    n = 1_000
    for letter in 'abcdefghij' * (n // 10):
        # ll.append(letter)
        ll.insert(letter)


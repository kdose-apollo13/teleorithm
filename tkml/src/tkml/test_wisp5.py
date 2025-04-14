from collections import deque
from itertools import islice, pairwise


# from itertools docs
def consume(iterator, n=None):
   "Advance the iterator n-steps ahead. If n is None, consume entirely."
   # Use functions that consume iterators at C speed.
   if n is None:
       # feed the entire iterator into a zero-length deque
       collections.deque(iterator, maxlen=0)
   else:
       # advance to the empty slice starting at position n
       next(islice(iterator, n, n), None)


def last(leaves):
    if (qty := len(leaves)) > 0:
        it = iter(leaves)
        consume(it, qty - 1)
        return list(it)[0]
    else:
        return None

def first(leaves):
    if (qty := len(leaves)) > 0:
        it = iter(leaves)
        return next(it)
    else:
        return None
    

def nexx(focused, leaves):
    for l, m in pairwise(leaves):
        if l is focused:
            return m
    else:
        return None

def prev(focused, leaves):
    for l, m in pairwise(leaves):
        if m is focused:
            return l
    else:
        return None


if __name__ == '__main__':
    l = [0, 1, 2]
    f = 0
    print(nexx(f, l))
    print(prev(f, l))
    print(last(l))
    print(first(l))


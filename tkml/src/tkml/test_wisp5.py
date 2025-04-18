from itertools import islice, pairwise


def last(leaves):
    """
        leaves
            : list[T]

        returns
            -> T
    """
    if (qty := len(leaves)) > 0:
        # see itertools docs -> consume
        it = iter(leaves)
        n = qty - 1
        next(islice(it, n, n), None)
        return next(it)
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
    l = [0, 1, 2, 3]
    assert first(l) == 0
    assert last(l) == 3
    assert nexx(0, l) == 1
    assert nexx(1, l) == 2
    assert prev(3, l) == 2
    assert prev(2, l) == 1



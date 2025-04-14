"""

Kramerica Linked List -> kll v0.1

source:
'Introduction to Algorithms - 2nd Edition' p204-212
-Cormen, Leiserson, Rivest, Stein

"""

def new_kll(size):
    new = {
        'nexx': None,
        'prev': None,
        'keys': None,
        'free': None
    }
    _init(new, size)
    return new


def _init(ll, size):
    ll['nexx'] = [0] * (size + 1)
    ll['prev'] = [0] * (size + 1)
    ll['keys'] = [None] * (size + 1)
    ll['free'] = list(range(size, 0, -1))


def _free_index(ll):
    free = ll['free']

    try:
        x = free.pop()
    except IndexError:
        raise Exception('List Full!')
    else:
        return x


def insert(o, kll):
    """
        Insert object at start of list.
    """
    prev = kll['prev']
    nexx = kll['nexx']
    keys = kll['keys']
    nil = 0

    x = _free_index(kll)
    
    # nil <-----> H
    # nil <- X -> H
    prev[x] = nil
    nexx[x] = nexx[nil]
    
    # nil -> X <- H
    prev[nexx[nil]] = x
    nexx[nil] = x  # must do last

    keys[x] = o


def append(o, kll):
    """
        Append object to end of list.
    """
    prev = kll['prev']
    nexx = kll['nexx']
    keys = kll['keys']
    nil = 0

    x = _free_index(kll)

    # T <-----> nil
    # T <- X -> nil
    prev[x] = prev[nil]
    nexx[x] = nil

    # T -> X <- nil
    nexx[prev[nil]] = x
    prev[nil] = x  # must do last

    keys[x] = o


def delete(x, kll):
    """
        Delete index x from list.
    """
    prev = kll['prev']
    nexx = kll['nexx']
    keys = kll['keys']
    free = kll['free']

    # P <-> X <-> N
    # P --------> N
    nexx[prev[x]] = nexx[x]
    
    # P <-------- N
    prev[nexx[x]] = prev[x]

    keys[x] = None
    free.append(x)
    

def iterate_x(ll):
    nexx = ll['nexx']
    nil = 0

    x = nexx[nil]
    while x != nil:
        yield x
        x = nexx[x]


def iterate_keys(ll):
    keys = ll['keys']

    for x in iterate_x(ll):
        yield keys[x]


def reverse_x(ll):
    prev = ll['prev']
    nil = 0

    x = prev[nil]
    while x != nil:
        yield x
        x = prev[x]


def reverse_keys(ll):
    keys = ll['keys']

    for x in reverse_x(ll):
        yield keys[x]


def search(target_key, ll):
    keys = ll['keys']

    for x in iterate_x(ll):
        if keys[x] == target_key:
            return x

        
def sort(ll, **kwargs):
    """
        Sort in place. Smaller elements will be at start of list.

        assumes key objects implement __lt__
    """
    keys = list(iterate_keys(ll))
    keys.sort(**kwargs)

    _init(ll, len(keys))
    for key in reversed(keys):
        insert(key, ll)


def pop_left(ll):
    nexx = ll['nexx']
    keys = ll['keys']
    nil = 0

    x = nexx[nil]
    o = keys[x]
    delete(x, ll)
    return o


def pop(ll):
    prev = ll['prev']
    keys = ll['keys']
    nil = 0

    x = prev[nil]
    o = keys[x]
    delete(x, ll)
    return o


def nexx(from_key, ll):
    keys = ll['keys']

    for x in iterate_x(ll):
        if keys[x] == from_key:
            x = ll['nexx'][x]
            return keys[x]

def prev(from_key, ll):
    keys = ll['keys']

    for x in iterate_x(ll):
        if keys[x] == from_key:
            x = ll['prev'][x]
            return keys[x]

def first(ll):
    keys = ll['keys']
    it = iterate_x(ll)
    x = next(it)
    return keys[x]

def last(ll):
    keys = ll['keys']
    it = iterate_x(ll)
    x = next(reversed(list(it)))
    return keys[x]
    

if __name__ == '__main__':
    from pprint import pprint
    ll = new_kll(3)
    insert('one', ll)
    append('two', ll)
    pprint(ll)
    n = nexx('one', ll)
    n = prev('two', ll)
    # print(first(ll))
    # print(last(ll))




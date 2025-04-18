"""
    | teleorithm |

    -> avoids overhead of python class mechanics
    -> divides concept of node over list indices
    
    trounces naive class impl
    trounced by deque

    local references to the list (eg) next = ll['next']
    are more legible for logic - and faster ->
    ~ 16 % less time, TODO: check bytecode for clues
    TODO: and make it easy to view/compare bytecodes
    
    from this tome ->
    ---------------------------------------------------
    'Introduction to Algorithms - 2nd Edition' p204-212
    -Cormen, Leiserson, Rivest, Stein
    ---------------------------------------------------
"""

def new_ll(size):
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
        x = ll['free'].pop()
    except IndexError:
        raise Exception('List Full!')
    else:
        return x


def insert(o, ll):
    """
        Insert object at start of list.
    """
    prev = ll['prev']
    nexx = ll['nexx']
    keys = ll['keys']
    nil = 0

    x = _free_index(ll)
    
    # nil <-----> H
    # nil <- X -> H
    prev[x] = nil
    nexx[x] = nexx[nil]
    
    # nil -> X <- H
    prev[nexx[nil]] = x
    nexx[nil] = x  # must do last

    keys[x] = o


def append(o, ll):
    """
        Append object to end of list.
    """
    prev = ll['prev']
    nexx = ll['nexx']
    keys = ll['keys']
    nil = 0

    x = _free_index(ll)

    # T <-----> nil
    # T <- X -> nil
    prev[x] = prev[nil]
    nexx[x] = nil

    # T -> X <- nil
    nexx[prev[nil]] = x
    prev[nil] = x  # must do last

    keys[x] = o


def _delete(x, ll):
    """
        Delete index x from list.
    """
    prev = ll['prev']
    nexx = ll['nexx']
    keys = ll['keys']
    free = ll['free']

    # P <-> X <-> N
    # P --------> N
    nexx[prev[x]] = nexx[x]
    
    # P <-------- N
    prev[nexx[x]] = prev[x]

    keys[x] = None
    free.append(x)
    

def delete_key(key, ll):
    """
        Delete key from list.
    """
    target_x = search(key, ll)
    if target_x:
        _delete(target_x, ll)


def _iterate_x(ll):
    nil = 0
    x = ll['nexx'][nil]
    while x != nil:
        yield x
        x = ll['nexx'][x]


def iterate_keys(ll):
    for x in _iterate_x(ll):
        yield ll['keys'][x]


def _reverse_x(ll):
    nil = 0
    x = ll['prev'][nil]
    while x != nil:
        yield x
        x = ll['prev'][x]


def reverse_keys(ll):
    for x in reverse_x(ll):
        yield ll['keys'][x]


def search(target_key, ll):
    for x in _iterate_x(ll):
        if ll['keys'][x] == target_key:
            return x
    else:
        return None

        
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
    nil = 0
    x = ll['nexx'][nil]
    o = ll['keys'][x]
    _delete(x, ll)
    return o


def pop(ll):
    nil = 0
    x = ll['prev'][nil]
    o = ll['keys'][x]
    _delete(x, ll)
    return o

if __name__ == '__main__':
    from pprint import pprint

    ll = new_ll(10)
    for letter in 'abcdefghij':
        append(letter, ll)

    print(*_iterate_x(ll))

    pprint(ll)
    delete_key('c', ll)
    delete_key('g', ll)
    pprint(ll)


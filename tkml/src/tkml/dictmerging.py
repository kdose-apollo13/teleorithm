from klab.lab import measure


def merge_dicts(a, b):
    """
    Return new dict merging a and b deeply.
    Values in b overwrite those in a.
    Neither a nor b is mutated.
    """
    result = {}
    for key in set(a) | set(b):
        in_a = key in a
        in_b = key in b
        if in_a and in_b:
            va, vb = a[key], b[key]
            # recurse if both dicts
            if isinstance(va, dict) and isinstance(vb, dict):
                result[key] = merge_dicts(va, vb)
            else:
                result[key] = vb
        elif in_b:
            vb = b[key]
            result[key] = merge_dicts({}, vb) if isinstance(vb, dict) else vb
        else:
            va = a[key]
            result[key] = merge_dicts({}, va) if isinstance(va, dict) else va
    return result


def deep_merge(dict1, dict2):
    """
    Recursively merges dict2 into a copy of dict1.
    Values from dict2 override values from dict1.
    Nested dictionaries are merged recursively.
    """
    merged_dict = dict1.copy()
    for key, value2 in dict2.items():
        value1 = merged_dict.get(key)
        if isinstance(value1, dict) and isinstance(value2, dict):
            merged_dict[key] = deep_merge(value1, value2)
        else:
            merged_dict[key] = value2
    return merged_dict

if __name__ == '__main__':
    S = {'a': {'aa': 1, 'bb': 2}, 'b': {'cc': 3, 'dd': 4}}
    T = {'a': {'aa': 5         }, 'b': {         'dd': 8}}
    r1 = deep_merge(S, T)

    S = {'a': {'aa': 1, 'bb': 2}, 'b': {'cc': 3, 'dd': 4}}
    T = {'a': {'aa': 5         }, 'b': {         'dd': 8}}
    r2 = merge_dicts(S, T)

    S = {}
    for i in range(10):
        S[i] = {}
        for j in range(10):
            S[i][j] = (i, j)
    T = {}
    for i in range(10):
        T[i] = {}
        for j in range(10):
            T[i][j] = (i, j + 3)

    with measure():
        r1 = deep_merge(S, T)

    with measure():
        r2 = merge_dicts(S, T)

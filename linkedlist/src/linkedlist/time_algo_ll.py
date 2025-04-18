from klab.lab import measure

from functools import partial

from linkedlist.algo_ll import (
    new_ll, insert, append, delete_key,
    iterate_keys, reverse_keys,
    search, sort, pop, pop_left
)


n = 1_000_000
print(f'n = {n}')

# n 1_000_000 -> 40 ms, 76 MiB
with measure():
    ll = new_ll(n)

# n 1_000_000 -> 440 ms, 77 MiB
with measure():
    for letter in 'abcdefghij' * (n // 10):
        insert(letter, ll)
    
# n 1_000_000 -> 460 ms, 77 MiB
# with measure():
#     for letter in 'abcdefghij' * (n // 10):
#         append(letter, ll)


# n 1_000_000 -> 800 ms
# with measure():
#     for letter in 'abcdefghij' * (n // 10):
#         delete_key(letter, ll)

# n 1_000_000 -> 500 ms, 74 MiB
# with measure():
#     for _ in range(n):
#         k = pop_left(ll)

# n 1_000_000 -> 500 ms, 74 MiB
# with measure():
#     for _ in range(n):
#         k = pop(ll)

# n 1_000_000 -> 640 ms, 82 MiB
# with measure():
#     s = sort(ll)

# n 1_000_000 -> 1 ms -> whenever key is found
# with measure():
#     x = search('j', ll)
#     print(x)

# print(ll)



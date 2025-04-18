from klab.lab import measure

from functools import partial

from linkedlist.deque_ll import LinkedList


n = 1_000_000
print(f'n = {n}')

# trivial
ll = LinkedList()

# i7-2600k -> 150 ms, 21 MiB
with measure():
    for letter in 'abcdefghij' * (n // 10):
        ll.insert(letter)

# i7-2600k -> 150 ms, 30 MiB
# with measure():
#     for letter in 'abcdefghij' * (n // 10):
#         ll.append(letter)

# i7-2600k -> 200 ms, 36 MiB
# with measure():
#     keys = list(ll.iterate_keys())
#     for k in keys:
#         ll.delete_key(k)

# i7-2600k -> 150 ms, 20 MiB
# with measure():
#     for _ in range(n):
#         k = ll.pop()

# i7-2600k -> 150 ms, 20 MiB
# with measure():
#     for _ in range(n):
#         k = ll.pop_left()


# i7-2600k -> 110 ms, 36 MiB
# with measure():
#     ll.sort()


from functools import partial
from time import time

from k_linked_list import (
    new_kll, insert, append, delete, search, sort,
    iterate_x, iterate_keys, reverse_x, reverse_keys,
    pop_left, pop,
)


llprint = partial(print, sep=' ', end='\n')
llprint = lambda *args, **kwargs: None

start = time()

n = 1000000
test = new_kll(n)

for letter in 'abcdefghij' * (n // 10):
    insert(letter, test)

# for letter in 'abcdefghij':
    # append(letter, test)

delete(1, test)

print('iterate_x')
llprint(*iterate_x(test))

print('iterate_keys')
llprint(*iterate_keys(test))

print('reverse_x')
llprint(*reverse_x(test))

print('reverse_keys')
llprint(*reverse_keys(test))


print('sort')
sort(test)
llprint(*iterate_keys(test))

i = search('f', test)
print(i)

o = pop_left(test)
print(o)
llprint(*iterate_keys(test))

o = pop(test)
print(o)
llprint(*iterate_keys(test))


end = time()
print(f'time: {(end - start) * 1000:.1f} ms')




"""
    +-----+
    !kDoSE¡
    +-----+
    ---------------------------
    bring the code into the lab
    how much to put on the slab
    ---------------------------

    # how many cpu instructions?

    $ sudo -Es
    $ perf stat -e instructions:u python3 whatever.py

    sudo -E preserves env variables -> need PYTHONPATH

"""
from contextlib import contextmanager
from os import getpid
from resource import getrusage, RUSAGE_SELF
from signal import SIGINT
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
from time import sleep, time


@contextmanager
def measure():
    """ 
        reports cpu instructions, max memory, time
        sleep(t) -> reported time off by ~0.2 %
    """
    events = 'instructions,cache-references,cache-misses'

    perf = Popen(
        ['perf', 'stat', '-p', str(getpid()), '-e', events],
        stdout=PIPE, stderr=PIPE
    )

    # allow perf program time to start
    sleep(0.2)
    
    try:
        start = time()
        yield  # code runs here
    finally:
        end = time()

        # do this before SIGINT, don't remember why
        stats = getrusage(RUSAGE_SELF)

        perf.send_signal(SIGINT)

        # docs say do it this way -----
        try:
            out, err = perf.communicate(timeout=1)
        except TimeoutExpired:
            perf.kill()
            perf.communicate()  # -----
        else:
            # TODO:
            # text = do_stuff(out + err)
            # print(text)

            log = (out + err).decode('utf-8')
            # TODO: parse fields and values, average over runs ??? (optional?)

            lines = log.split('\n')
            # excise perf 'time elapsed' lines
            print(*lines[:-4], sep='\n')

            # maxrss -> kilobytes, see man 2 getrusage
            peak_RAM = int(stats.ru_maxrss / 1024)  # mebibytes

            # print new info with consistent format
            ms = (end - start) * 1000
            print(f'{ms:>18,.1f}      time elapsed (ms)')
            print(f'{peak_RAM:>18,}      peak memory (MiB)')


if __name__ == '__main__':
    with measure():
        print('*what does it take to print this line?*')


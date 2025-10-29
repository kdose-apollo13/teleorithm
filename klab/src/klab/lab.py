"""
    how many cpu instructions?

    USAGE
    ---------
    with cpu_stats():
        pass  # your code here

            72,983      cpu instructions
             4,131      cache references
             3,269      cache misses
              28.3      time by perf (ms)
               0.1      time by python (ms)
                13      peak memory (MiB)

    OR

    r = R()
    with cpu_stats(r):
        print('yeah!')
    
    r -> {
        'cache_miss': 2987,
        'cache_ref': 3574,
        'cpu_inst': 77394,
        'peak_mem_MiB': 13,
        't_perf_ms': 19.540853,
        't_python_ms': 0.01811981201171875
    }
    ---------
    t_perf_ms offset from ~200ms sleep to hope for perf startup

    $ sudo -Es
    $ perf stat -e instructions:u python3 whatever.py

    sudo -E preserves env variables -> need PYTHONPATH

    no permission?
    $ echo 2 > /proc/sys/kernel/perf_event_paranoid

"""
from contextlib import contextmanager
from os import getpid
from pprint import pprint as P
from resource import getrusage, RUSAGE_SELF
from signal import SIGINT
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
from time import sleep, time


@contextmanager
def cpu_stats(record=None):
    """ 
        record
            : dict
            : template whose values get modified
            : if None results are printed instead

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
            log = (out + err).decode('utf-8')
            lines = [l.strip().split() for l in log.split('\n')]
            try:
                cpu_inst = int(lines[3][0].replace(',', ''))
                cache_ref = int(lines[4][0].replace(',', ''))
                cache_miss = int(lines[5][0].replace(',', ''))
                t_perf_ms = float(lines[7][0]) * 1000 
            except ValueError as e:
                print(e)
                print('no permission to run perf?')
                print(log)

            # maxrss -> kilobytes, see man 2 getrusage
            peak_RAM = int(stats.ru_maxrss / 1024)  # mebibytes
            t_python_ms = (end - start) * 1000

            if record is None:
                print(f'{cpu_inst:>18,.0f}      cpu instructions')
                print(f'{cache_ref:>18,.0f}      cache references')
                print(f'{cache_miss:>18,.0f}      cache misses')
                print(f'{t_perf_ms-160:>18.1f}      time by perf (ms)')
                print(f'{t_python_ms:>18,.1f}      time by python (ms)')
                print(f'{peak_RAM:>18,}      peak memory (MiB)')
            else:
                record['t_perf_ms'] += t_perf_ms
                record['t_python_ms'] += t_python_ms
                record['cpu_inst'] += cpu_inst
                record['cache_ref'] += cache_ref
                record['cache_miss'] += cache_miss
                record['peak_mem_MiB'] += peak_RAM


def new_template():
    return {
        't_perf_ms': -160,  # offset due to 0.2 s delay perf startup
        't_python_ms': 0,
        'cpu_inst': 0,
        'cache_ref': 0,
        'cache_miss': 0,
        'peak_mem_MiB': 0,
    }


R = new_template

if __name__ == '__main__':
    r = R()
    with cpu_stats(r):
        print('what does it take to print this line?')
    P(r)

    with cpu_stats():
        print('yeah!')



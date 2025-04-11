from unittest import defaultTestLoader
from klab.ututils import Runner


if __name__ == '__main__':
    suite = defaultTestLoader.discover('.')
    runner = Runner()
    runner.run(suite)


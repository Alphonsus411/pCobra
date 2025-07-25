import pathlib
import pytest
import sys


def main():
    root = pathlib.Path(__file__).parent
    sys.exit(pytest.main([str(root), '-k', 'cli']))


if __name__ == '__main__':
    main()

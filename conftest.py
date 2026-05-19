import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent)


def pytest_configure(config):
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

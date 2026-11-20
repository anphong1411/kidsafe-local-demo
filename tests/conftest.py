"""Make the documented nested temporary test directory work in a fresh archive."""
from pathlib import Path


def pytest_configure(config):
    base = config.getoption('basetemp')
    if base:
        Path(base).resolve().parent.mkdir(parents=True, exist_ok=True)

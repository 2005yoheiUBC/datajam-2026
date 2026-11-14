"""Reproduce the presentation from committed aggregates or downloaded raw listings."""
import argparse
from src.analysis import run

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',choices=['aggregates','raw'],default='aggregates')
    run(p.parse_args().source)

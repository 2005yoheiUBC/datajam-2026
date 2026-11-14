"""Compatibility entry point for the current analysis; standard library only."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.analysis import C, select, summary, underwrite, run

if __name__ == '__main__':
    run('aggregates')

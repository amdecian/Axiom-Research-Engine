"""One-shot trusted fixture worker; process boundary is not a security sandbox."""
import argparse
import json
from .algorithms import STRATEGIES, verify


def main():
    p = argparse.ArgumentParser()
    p.add_argument('strategy', choices=sorted(STRATEGIES))
    p.add_argument('seed', type=int)
    a = p.parse_args()
    if not 0 <= a.seed <= 2**32-1:
        p.error('seed out of range')
    print(json.dumps(verify(a.strategy,a.seed),allow_nan=False))

if __name__ == '__main__':
    main()

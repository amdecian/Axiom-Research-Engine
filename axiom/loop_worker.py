"""Trusted one-shot evaluator for data-only strategies. No security sandbox."""
import json, sys
from .strategy import evaluate, validate

def main():
    raw=sys.stdin.buffer.read(1_000_001)
    if len(raw)>1_000_000: raise ValueError('worker input too large')
    body=json.loads(raw)
    if set(body)!={'strategy','cases'} or not isinstance(body['cases'],list) or not 1<=len(body['cases'])<=128: raise ValueError('bad worker input')
    print(json.dumps(evaluate(body['cases'],validate(body['strategy'])),allow_nan=False))

if __name__=='__main__': main()

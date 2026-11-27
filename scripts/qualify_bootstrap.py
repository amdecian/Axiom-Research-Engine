"""Fixed B006 acceptance test; compare deterministic results, not historical timing."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from axiom import loop


def require(condition, message):
    if not condition:
        raise ValueError(message)


def deterministic(value):
    if isinstance(value, dict):
        return {key: deterministic(item) for key, item in value.items()
                if key not in {'elapsed_seconds', 'elapsed_ns'}}
    if isinstance(value, list):
        return [deterministic(item) for item in value]
    return value


def main():
    gate = json.loads((ROOT / 'research/bootstrap/replay-approval.json').read_text(encoding='utf-8'))
    old = json.loads((ROOT / 'evidence/loop-report.json').read_text(encoding='utf-8'))
    prior_replay = json.loads((ROOT / 'evidence/loop-replay.json').read_text(encoding='utf-8'))
    plan = loop.load(ROOT / 'research/plans/adaptive-sat.json')
    spec = loop.prepare(plan)[0]
    require(gate['schema_version'] == 'bootstrap-replay-1' and gate['slice'] == 'B006', 'invalid bootstrap approval')
    require(spec['source_sha256'] == gate['source_sha256'] and spec['approval_digest'] == gate['approval_digest'], 'approved source or plan changed')
    require(spec == old['spec'] and spec['max_evaluations'] == gate['expected_evaluations'], 'historical specification mismatch')
    with tempfile.TemporaryDirectory(prefix='axiom-bootstrap-replay-') as temp:
        path = Path(temp) / 'run'
        actual = loop.run(plan, gate['approval_digest'], path)
        require(actual['reason'] == 'completed', 'campaign did not complete')
        require(deterministic(actual) == deterministic(old), 'deterministic historical report mismatch')
        replay = loop.replay(path)
        require(replay == prior_replay, 'historical replay summary mismatch')
        require(replay['replayed_evaluations'] == gate['expected_evaluations'] and replay['fixture_results_rechecked'] == gate['expected_fixture_results'], 'unexpected replay coverage')
        result = {'slice': 'B006', 'status': 'passed', 'historical_deterministic_report': 'matched', 'replay': replay, 'fresh_run_elapsed_seconds': actual['elapsed_seconds'], 'provider_calls': 0, 'artifact_uploads': 0, 'source_sha256': spec['source_sha256']}
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

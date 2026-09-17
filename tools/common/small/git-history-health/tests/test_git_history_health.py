import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'git_history_health.py'
spec = importlib.util.spec_from_file_location('git_history_health', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_summarize_filters_sorts_and_truncates():
    payload = {
        'uniqueBlobSize': {
            'description': 'all blobs',
            'value': 100,
            'unit': 'B',
            'levelOfConcern': 0.2,
        },
        'maxBlobSize': {
            'description': 'largest blob',
            'value': 50,
            'unit': 'B',
            'levelOfConcern': 3.0,
            'objectDescription': 'assets/big.bin',
        },
        'nested': {
            'maxPathDepth': {
                'value': 30,
                'levelOfConcern': 2.0,
            }
        },
    }
    result = module.summarize(payload, 1.0, 1)
    assert result['metric_count_total'] == 3
    assert result['concern_count_total'] == 2
    assert result['findings_truncated'] is True
    assert result['findings'][0]['metric'] == 'maxBlobSize'
    assert result['findings'][0]['object_description'] == 'assets/big.bin'


def test_zero_limit_is_unlimited():
    payload = {
        'a': {'value': 1, 'levelOfConcern': 1.0},
        'b': {'value': 2, 'levelOfConcern': 2.0},
    }
    result = module.summarize(payload, 0.0, 0)
    assert len(result['findings']) == 2
    assert result['findings_truncated'] is False

"""Measure the normal private snapshot without retaining its contents publicly."""
import gzip
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

from decision import registry, snapshot
from pipeline.data_source import overlay

engine = Path(__file__).resolve().parents[4]
private = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
with tempfile.TemporaryDirectory(dir=engine / 'tmp/model-367/root') as temporary:
    root = overlay(engine, private, Path(temporary) / 'root')
    registry.use_root(root)
    built = snapshot.build_from_repo(root, premier=root / 'premier/slice-1.yaml',
                                     as_of=date(2026, 10, 18))
    packed = built.to_bytes(key=None, ed25519_signer=None)
    result = {'gzip_bytes': len(packed), 'json_bytes': len(gzip.decompress(packed)),
              'content_hash': built.content_hash}
    if '--expect-curated' in sys.argv[3:]:
        plans = {plan['id']: plan['facts'] for plan in built.content['subscriptions']}
        prefix = 'offering.subscription.'
        for plan in ('supergrok-lite', 'supergrok-heavy'):
            for facet in ('models_covered', 'programmatic_or_agent_use',
                          'usage_allowance', 'coverage_quote'):
                assert prefix + facet not in plans['xai/subscription/' + plan], (plan, facet)
        business = plans['xai/subscription/business']
        assert business[prefix + 'models_covered'][:2] == ['known', ['xai/grok-4-7']]
        assert prefix + 'coverage_quote' not in business
        result['curated_snapshot_assertions'] = 'passed'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

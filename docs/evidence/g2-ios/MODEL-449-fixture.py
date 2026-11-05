from datetime import UTC, date, datetime
import json
from pathlib import Path
import socket

from decision.model import load_offerings
from decision.verify import Queue, VerificationLog
from release_signals.pipeline import draft_signal
from schema.card import ModelCard
from tests.test_release_signal_prices import release_catalogue

root = Path('/tmp/model-449-scratch/private-data')
fixture_root = Path('/tmp/model-449-scratch/audit/release-fixture')
fixture_root.mkdir()
signal, fetch = release_catalogue(fixture_root, prices=True)

def forbidden_network(*args, **kwargs):
    raise AssertionError('Synthetic verification must not access the network')

socket.socket.connect = forbidden_network
result = draft_signal(signal, root=root, fetch=fetch, read_date=date(2026, 11, 4))
assert result.offering_path is not None
ModelCard.from_yaml_file(result.card_path)
row, = load_offerings(result.offering_path)
assert {fact.facet: fact.value for fact in row.facts} == {
    'offering.price.input': 2, 'offering.price.output': 8,
}
queue = Queue(root / 'verification')
claims = [claim for key, claim in queue.filed().items()
          if key[1].startswith('google-gemini-api/google/fixture-model/')]
assert len(claims) == 2
receipts = VerificationLog(root / 'verification').latest()
assert all(receipts[('fact', claim.target.id)].independent for claim in claims)
queue.requeue([claim.target for claim in claims], at=datetime.now(UTC))
summary = {
    'model': row.model,
    'offering': row.id,
    'card_schema_valid': True,
    'offering_schema_valid': True,
    'independent_receipts': len(claims),
    'requeued_for_cli_verification': len(claims),
    'firecrawl_credits': result.firecrawl_credits,
}
assert result.firecrawl_credits == 0
print(json.dumps(summary, indent=2))

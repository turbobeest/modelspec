from api.worker.openapi import _validate, build_spec
from decision.hardware_fit import check
from tests.test_hardware_fit import REQUEST, fixture_snapshot, lower_bound_record

spec = build_spec()
schema = spec['components']['schemas']['HardwareFitResponse']
for basis, snapshot in [
    ('full', fixture_snapshot()),
    ('lower_bound', fixture_snapshot([lower_bound_record()], memory_gb=32)),
]:
    status, body = check(REQUEST, snapshot)
    errors = _validate(body, schema, spec)
    assert status == 200 and body['basis'] == basis and errors == [], errors
    print(basis, 'OpenAPI discriminator-aware validation:', errors)

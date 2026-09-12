import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

ENGINE_SPEC = importlib.util.spec_from_file_location(
    "relation_endpoint_contract", SCRIPTS / "relation_endpoint_contract.py"
)
ENGINE = importlib.util.module_from_spec(ENGINE_SPEC)
sys.modules[ENGINE_SPEC.name] = ENGINE
ENGINE_SPEC.loader.exec_module(ENGINE)

FREEZE_SPEC = importlib.util.spec_from_file_location(
    "freeze_relation_endpoint_contract", SCRIPTS / "freeze_relation_endpoint_contract.py"
)
FREEZE = importlib.util.module_from_spec(FREEZE_SPEC)
sys.modules[FREEZE_SPEC.name] = FREEZE
FREEZE_SPEC.loader.exec_module(FREEZE)

EXAMPLE = ROOT / "config" / "relation_endpoint_contract_example.json"
EXPECTED_FINGERPRINT = "83c7a631d08e5f25fb8a57e5029e75365aa9be80a8577a32ff8f7fc2a772a41f"


def example_payload():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_example_contract_has_stable_fingerprint():
    contract = ENGINE.contract_from_mapping(example_payload())
    assert contract.fingerprint_sha256() == EXPECTED_FINGERPRINT
    assert len(contract.fingerprint_sha256()) == 64
    assert contract.canonical_json() == contract.canonical_json()


def test_freeze_receipt_roundtrips_exact_contract():
    raw = example_payload()
    receipt = FREEZE.freeze_contract_payload(raw)
    assert receipt["schema_version"] == "relation_endpoint_contract_freeze_v0_1"
    assert receipt["contract"] == raw
    assert receipt["fingerprint_algorithm"] == "sha256"
    assert receipt["fingerprint_sha256"] == EXPECTED_FINGERPRINT
    assert receipt["outcome_data_read"] is False
    assert receipt["empirical_ledger_increment"] == 0


def test_semantic_change_changes_fingerprint():
    raw = example_payload()
    original = ENGINE.contract_from_mapping(raw).fingerprint_sha256()
    changed = dict(raw)
    changed["relation"] = "successful_reproduction(k) -> compatible_resource(k)"
    mutated = ENGINE.contract_from_mapping(changed).fingerprint_sha256()
    assert original != mutated


def test_unknown_or_missing_fields_are_rejected():
    raw = example_payload()

    missing = dict(raw)
    missing.pop("relation")
    try:
        ENGINE.contract_from_mapping(missing)
    except ValueError as exc:
        assert "missing contract fields" in str(exc)
    else:
        raise AssertionError("missing relation field should fail")

    unknown = dict(raw)
    unknown["posthoc_note"] = "not part of the frozen schema"
    try:
        ENGINE.contract_from_mapping(unknown)
    except ValueError as exc:
        assert "unknown contract fields" in str(exc)
    else:
        raise AssertionError("unknown contract fields should fail")


def test_json_key_order_does_not_change_fingerprint():
    raw = example_payload()
    reversed_mapping = {key: raw[key] for key in reversed(list(raw.keys()))}
    a = ENGINE.contract_from_mapping(raw).fingerprint_sha256()
    b = ENGINE.contract_from_mapping(reversed_mapping).fingerprint_sha256()
    assert a == b == EXPECTED_FINGERPRINT

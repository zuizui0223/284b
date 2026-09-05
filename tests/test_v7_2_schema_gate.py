import unittest

from product_b_v7_2.schema_gate import schema_sha256, validate_snapshot_schema
from product_b_v7_2.snapshot_transport import REQUIRED_SNAPSHOT_FIELDS


def valid_schema():
    schema = {name: "string" for name in REQUIRED_SNAPSHOT_FIELDS}
    schema.update(
        decimallatitude="double",
        decimallongitude="double",
        coordinateuncertaintyinmeters="double",
        recordedby="list<element: string>",
        eventdate="timestamp[ms]",
        taxonkey="string",
        specieskey="string",
        gbifid="string",
    )
    return schema


class SnapshotSchemaGateTests(unittest.TestCase):
    def test_valid_schema_passes_and_hash_is_order_invariant(self):
        schema = valid_schema()
        self.assertEqual(validate_snapshot_schema(schema), ())
        self.assertEqual(schema_sha256(schema), schema_sha256(dict(reversed(list(schema.items())))))

    def test_missing_required_field_fails(self):
        schema = valid_schema()
        del schema["coordinateuncertaintyinmeters"]
        reasons = validate_snapshot_schema(schema)
        self.assertTrue(any(reason.startswith("missing_required_fields:") for reason in reasons))

    def test_2026_snapshot_taxon_keys_must_be_strings(self):
        schema = valid_schema()
        schema["taxonkey"] = "int64"
        reasons = validate_snapshot_schema(schema)
        self.assertIn("taxonkey_must_be_string_in_2026_08_snapshot", reasons)

    def test_coordinate_and_recorder_types_are_not_silently_coerced(self):
        schema = valid_schema()
        schema["decimallatitude"] = "string"
        schema["recordedby"] = "string"
        reasons = validate_snapshot_schema(schema)
        self.assertIn("decimallatitude_must_be_floating", reasons)
        self.assertIn("recordedby_must_be_list", reasons)


if __name__ == "__main__":
    unittest.main()

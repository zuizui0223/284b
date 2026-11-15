"""Dependency-free tests of the predeclared target-identity challenge manifest."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest=json.loads(
            (ROOT/"config/target_identity_controls_v1.json").read_text(encoding="utf-8")
        )

    def test_complete_fixed_disjoint_taxa_and_donors(self):
        x=self.manifest
        entries=x["entries"]
        self.assertEqual(x["schema"],"284b.target_identity_controls_v1")
        self.assertEqual(x["empirical_ledger_increment"],0)
        self.assertEqual(len(entries),12)
        self.assertEqual({e["index"] for e in entries},set(range(12)))
        self.assertEqual(len({e["taxon"] for e in entries}),12)
        by_id={e["index"]:e["taxon"] for e in entries}
        for e in entries:
            self.assertNotEqual(e["taxon"],e["donor_taxon"])
            self.assertEqual(by_id[e["donor_index"]],e["donor_taxon"])

    def test_pinned_source_archive_digests(self):
        entries=self.manifest["entries"]
        all_ids=[]
        for e in entries:
            for tag in ("fit","frame"):
                self.assertTrue(e[f"{tag}_artifact_digest"].startswith("sha256:"))
                self.assertEqual(len(e[f"{tag}_artifact_digest"]),71)
                all_ids.append(e[f"{tag}_artifact_id"])
        self.assertEqual(len(set(all_ids)),24)

    def test_no_threshold_or_original_endpoint_redefinition(self):
        self.assertIn("No threshold re-tuning",self.manifest["reference"])
        self.assertEqual(self.manifest["source_frozen_endpoint"]["artifact_id"],10137399646)
        self.assertEqual(self.manifest["original_reference_artifact_id"],10137248940)
        self.assertEqual(self.manifest["pair_rule"].count("no rescue"),1)


if __name__=="__main__":
    unittest.main()

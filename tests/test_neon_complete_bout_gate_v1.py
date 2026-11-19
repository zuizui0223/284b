"""Synthetic-only regression tests for the conservative NEON 400m² bout gate."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from neon_complete_bout_gate_v1 import (
    evaluate_400m2_bout, SUBPLOTS_1, SUBPLOTS_10, SUBPLOTS_100
)


def fixture():
    base={
        "siteID":"JORN", "plotID":"JORN_001", "eventID":"JORN_001.1.2021",
        "boutNumber":"1","endDate":"2021-07-15",
        "samplingImpractical":"OK",
        "biophysicalCriteria":"OK - no known exceptions",
        "targetTaxaPresent":"N",
        "scientificName":"",
        "taxonRank":"",
        "identificationQualifier":"",
        "morphospeciesID":"",
    }
    one=[{**base,"subplotID":name} for name in sorted(SUBPLOTS_1)]
    large=[{**base,"subplotID":name} for name in sorted(SUBPLOTS_10|SUBPLOTS_100)]
    return one,large


class PlantBoutTests(unittest.TestCase):
    def test_complete_bout_can_support_protocol_conditional_non_detection(self):
        a,b=fixture()
        self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                         "protocol_conditional_non_detection")

    def test_detect_nested_taxon_in_either_table(self):
        for table in (0,1):
            a,b=fixture()
            row=(a,b)[table][0]
            row.update({"targetTaxaPresent":"Y","scientificName":"Artemisia tridentata",
                        "taxonRank":"SPECIES"})
            self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                             "detected")

    def test_do_not_turn_missing_large_subplots_into_absence(self):
        a,b=fixture()
        self.assertEqual(evaluate_400m2_bout(a,b[:-1],focal_scientific_name="Artemisia tridentata")["state"],
                         "unresolved")
        self.assertEqual(evaluate_400m2_bout(a,[],focal_scientific_name="Artemisia tridentata")["state"],
                         "unresolved")

    def test_repeated_subplot_does_not_count_as_missing_other_subplot(self):
        a,b=fixture()
        b[-1]=copy.deepcopy(b[0])
        self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                         "unresolved")

    def test_suboptimal_or_unknown_effort_blocks_non_detection(self):
        for field,value in (("samplingImpractical","location flooded"),
                            ("biophysicalCriteria","conditions not met: not flowering"),
                            ("biophysicalCriteria","")):
            a,b=fixture()
            a[0][field]=value
            self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                             "unresolved")

    def test_unknown_species_does_not_generate_false_absence(self):
        a,b=fixture()
        b[0].update({"targetTaxaPresent":"Y","morphospeciesID":"morph-1"})
        self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                         "unresolved")

    def test_uncertain_focal_genus_does_not_generate_false_absence(self):
        a,b=fixture()
        b[0].update({"targetTaxaPresent":"Y","scientificName":"Artemisia sp.",
                      "taxonRank":"GENUS","identificationQualifier":"cf"})
        self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                         "unresolved")

    def test_contradictory_empty_subplot_sentinel_is_not_an_absence(self):
        a,b=fixture()
        a[0].update({"targetTaxaPresent":"N","scientificName":"Artemisia tridentata",
                     "taxonRank":"SPECIES"})
        state=evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")
        self.assertEqual(state["state"],"unresolved")

    def test_family_level_unidentified_plant_blocks_negative_label(self):
        a,b=fixture()
        b[0].update({"targetTaxaPresent":"Y","scientificName":"Asteraceae",
                     "taxonRank":"FAMILY"})
        out=evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")
        self.assertEqual(out["state"],"unresolved")

    def test_event_and_date_constraints(self):
        a,b=fixture()
        b[0]["eventID"]="WRONG_PLOT.1.2021"
        self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                         "unresolved")
        a,b=fixture()
        for row in a+b:
            row["endDate"]="2019-07-01"
        self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                         "unresolved")

    def test_missing_quality_columns_fail_closed(self):
        a,b=fixture()
        del a[0]["samplingImpractical"]
        self.assertEqual(evaluate_400m2_bout(a,b,focal_scientific_name="Artemisia tridentata")["state"],
                         "unresolved")


if __name__=="__main__":
    unittest.main()

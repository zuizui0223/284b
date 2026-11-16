"""Offline guards for the frozen GBIF S3 object-identity replay."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from check_original_gbif_object_manifest_v1 import (
    _field, _name, OLD_RECEIPT,
    EXPECTED_OBJECT_COUNT, EXPECTED_PARQUET_OBJECT_COUNT, EXPECTED_OBJECT_MANIFEST_SHA256
)
from xml.etree import ElementTree as ET
import json


class ManifestReplayGuards(unittest.TestCase):
    def test_metadata_xpath_namespaces(self):
        xml=ET.fromstring('<r xmlns="urn:s3"><Contents><Key>x</Key><Size>8</Size></Contents></r>')
        self.assertEqual(_field(xml.find(_name(xml,"Contents")),"Key"),"x")
        self.assertEqual(_field(xml.find(_name(xml,"Contents")),"Size"),"8")

    def test_original_source_is_exactly_pinned(self):
        old=json.loads(OLD_RECEIPT.read_text())
        self.assertEqual(old["object_count"],EXPECTED_OBJECT_COUNT)
        self.assertEqual(old["parquet_object_count"],EXPECTED_PARQUET_OBJECT_COUNT)
        self.assertEqual(old["object_manifest_sha256"],EXPECTED_OBJECT_MANIFEST_SHA256)
        self.assertEqual(old["citation_doi"],"10.15468/dl.fs3btq")


if __name__=="__main__":
    unittest.main()

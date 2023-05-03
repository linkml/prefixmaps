import unittest

import yaml

from prefixmaps.ingest.ingest_bioportal import from_bioportal
from tests import INPUT_DIR

EXPECTED_CANONICAL = [
    ("OA", "http://www.w3.org/ns/oa#"),
    ("SCHEMA", "http://schema.org/"),
]

EXPECTED_NONCANONICAL = [
    "http://identifiers.org/omim/",
    "http://meta.schema.org/",
]


class TextETLForBioportal(unittest.TestCase):
    def test_bioportal(self):
        with open(str(INPUT_DIR / "bioportal.yaml")) as file:
            ctxt = from_bioportal(yaml.safe_load(file), "bioportal")
            for prefix_expansion in ctxt.prefix_expansions:
                print(prefix_expansion)
            prefixmap = ctxt.as_dict()
            prefixmap_invert = ctxt.as_inverted_dict()
            for prefix, namespace in EXPECTED_CANONICAL:
                self.assertEqual(prefixmap[prefix], namespace)
                self.assertEqual(prefixmap_invert[namespace], prefix)
            # These maps are not included in the prefixmaps
            # but may be present in other objects
            for namespace in EXPECTED_NONCANONICAL:
                with self.assertRaises(KeyError):
                    prefixmap_invert[namespace]

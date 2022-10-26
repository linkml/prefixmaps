import unittest

import yaml

from prefixmaps.ingest.ingest_bioportal import from_bioportal
from tests import INPUT_DIR

EXPECTED = [
    ("OA", "http://www.w3.org/ns/oa#"),
    ("SCHEMA", "http://schema.org/"),
]


class TextETLForBioportal(unittest.TestCase):
    def test_bioportal(self):
        file = str(INPUT_DIR / "bioportal.yaml")
        ctxt = from_bioportal(yaml.safe_load(file))
        for prefix_expansion in ctxt.prefix_expansions:
            print(prefix_expansion)
        prefixmap = ctxt.as_dict()
        prefixmap_invert = ctxt.as_inverted_dict()
        for prefix, namespace in EXPECTED:
            self.assertEqual(prefixmap[prefix], namespace)
            self.assertEqual(prefixmap_invert[namespace], prefix)

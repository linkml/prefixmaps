import unittest

from prefixmaps.ingest.ingest_shacl import from_obo

EXPECTED = [
    ("GEO", "http://purl.obolibrary.org/obo/GEO_"),
    ("CL", "http://purl.obolibrary.org/obo/CL_"),
    ("UBERON", "http://purl.obolibrary.org/obo/UBERON_"),
    ("GO", "http://purl.obolibrary.org/obo/GO_"),
    ("WBPhenotype", "http://purl.obolibrary.org/obo/WBPhenotype_"),
]


class TextETLForOBO(unittest.TestCase):
    def test_prefix_cc(self):
        ctxt = from_obo()
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, ns in EXPECTED:
            self.assertEqual(pm[pfx], ns)
            self.assertEqual(pmi[ns], pfx)

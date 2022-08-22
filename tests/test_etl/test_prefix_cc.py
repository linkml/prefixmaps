import unittest

from prefixmaps.ingest.ingest_jsonld import from_prefixcc

EXPECTED = [
    ("owl", "http://www.w3.org/2002/07/owl#"),
    ("foaf", "http://xmlns.com/foaf/0.1/"),
]


class TextETLForPrefixCC(unittest.TestCase):
    def test_prefix_cc(self):
        ctxt = from_prefixcc()
        for pe in ctxt.prefix_expansions:
            print(pe)
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, ns in EXPECTED:
            self.assertEqual(pm[pfx], ns)
            self.assertEqual(pmi[ns], pfx)

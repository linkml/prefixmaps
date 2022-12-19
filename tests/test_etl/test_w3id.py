import unittest

from prefixmaps.ingest.ingest_w3id import from_w3id

# use test cases that are likely to be stable
EXPECTED = [
    ("kgcl", "https://w3id.org/kgcl/"),
    ("linkml", "https://w3id.org/linkml/"),
    ("biolink", "https://w3id.org/biolink/"),
    ("chemrof", "https://w3id.org/chemrof/"),
    ("nfdi4cat", "https://w3id.org/nfdi4cat/"),
    ("yago", "https://w3id.org/yago/"),
]


class TestW3id(unittest.TestCase):
    def test_w3id(self):
        ctxt = from_w3id()
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, ns in EXPECTED:
            self.assertEqual(pm[pfx], ns)
            self.assertEqual(pmi[ns], pfx)

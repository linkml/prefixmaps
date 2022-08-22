import unittest

from prefixmaps.datamodel.context import StatusType
from prefixmaps.io.parser import context_from_file, load_context
from prefixmaps.io.writer import context_to_file
from tests import OUTPUT_DIR

EXPECTED_OBO = [
    ("GEO", "http://purl.obolibrary.org/obo/GEO_"),
    ("CL", "http://purl.obolibrary.org/obo/CL_"),
    ("UBERON", "http://purl.obolibrary.org/obo/UBERON_"),
    ("GO", "http://purl.obolibrary.org/obo/GO_"),
    ("WBPhenotype", "http://purl.obolibrary.org/obo/WBPhenotype_"),
]

EXPECTED_SEMWEB = [
    ("owl", "http://www.w3.org/2002/07/owl#"),
    ("foaf", "http://xmlns.com/foaf/0.1/"),
]


class TextPrefixMaps(unittest.TestCase):
    def setUp(self) -> None:
        self.obo_context = load_context("obo")
        self.prefixcc_context = load_context("prefixcc")
        self.bioregistry_context = load_context("bioregistry")
        self.merged_context = load_context("merged")

    def test_load_and_roundtrip(self):
        """
        Tests basic I/O
        """
        ctxt = self.obo_context
        pm = ctxt.as_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pm[pfx], exp)
        pmi = ctxt.as_inverted_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pmi[exp], pfx)
        outpath = OUTPUT_DIR / "tmp.csv"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(str(outpath), "w", encoding="UTF-8") as outfile:
            context_to_file(ctxt, outfile)
        with open(str(outpath)) as roundtrip_file:
            ctxt2 = context_from_file("obo2", roundtrip_file)
        # self.assertEqual(ctxt, ctxt2)
        pm = ctxt2.as_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pm[pfx], exp)
        pmi = ctxt2.as_inverted_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pmi[exp], pfx)

    def test_combine(self):
        """
        tests composition between prefix maps

        - ensure priority order
        - ensure either prefix or namespace duplicates are not marked canonical
        """
        ctxt = self.obo_context
        pm = ctxt.as_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pm[pfx], exp)
        # test adding a lowercase alias, case-insensitive
        ctxt.add_prefix("go", "http://example.org/go/")
        [pe] = ctxt.filter(prefix="go")
        # check ordering is preserved
        self.assertEqual(pe, ctxt.prefix_expansions[-1])
        self.assertEqual(pe.status, StatusType.prefix_alias)
        # test namespace alias
        ctxt.add_prefix("xyzxyz", "http://purl.obolibrary.org/obo/WBPhenotype_")
        [pe] = ctxt.filter(prefix="xyzxyz")
        self.assertEqual(pe.status, StatusType.namespace_alias)
        # test namespace alias, case-insensitive
        ctxt.add_prefix("notcl", "http://purl.obolibrary.org/obo/cl_")
        [pe] = ctxt.filter(prefix="notcl")
        self.assertEqual(pe.status, StatusType.namespace_alias)
        self.assertFalse(pe.canonical())
        # test the GEOGEO case
        ctxt.add_prefix("GEOGEO", "http://purl.obolibrary.org/obo/GEO_")
        [pe] = ctxt.filter(prefix="GEOGEO")
        self.assertEqual(pe.status, StatusType.namespace_alias)
        self.assertEqual(pe.namespace, "http://purl.obolibrary.org/obo/GEO_")
        self.assertFalse(pe.canonical())
        # test adding canonical
        ctxt.add_prefix("x", "http://example.org/x/")
        [pe] = ctxt.filter(prefix="x")
        self.assertEqual(pe.status, StatusType.canonical)
        self.assertTrue(pe.canonical())
        # test multi-alias
        ctxt.add_prefix("CL", "http://purl.obolibrary.org/obo/UBERON_")
        pe = ctxt.prefix_expansions[-1]
        self.assertEqual(pe.status, StatusType.multi_alias)
        self.assertFalse(pe.canonical())
        # test all as expected
        pm = ctxt.as_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pm[pfx], exp)

    def test_merged(self):
        ctxt = self.merged_context
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pm[pfx], exp)
            self.assertEqual(pmi[exp], pfx)
        for pfx, exp in EXPECTED_SEMWEB:
            self.assertEqual(pm[pfx], exp)
            self.assertEqual(pmi[exp], pfx)

    def test_prefixcc(self):
        ctxt = self.prefixcc_context
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, exp in EXPECTED_SEMWEB:
            self.assertEqual(pm[pfx], exp)
            self.assertEqual(pmi[exp], pfx)

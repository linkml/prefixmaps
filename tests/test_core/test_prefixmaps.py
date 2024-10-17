"""Tests core expansion logic and data.
This serves as "checksums" on the underlying ingested data.
"""

import unittest

import prefixmaps
from prefixmaps.datamodel.context import StatusType
from prefixmaps.io.parser import context_from_file, load_context, load_multi_context
from prefixmaps.io.writer import context_to_file
from tests import OUTPUT_DIR

EXPECTED_OBO = [
    # GEO conflicts in other contexts
    ("GEO", "http://purl.obolibrary.org/obo/GEO_"),
    ("CL", "http://purl.obolibrary.org/obo/CL_"),
    ("UBERON", "http://purl.obolibrary.org/obo/UBERON_"),
    ("GO", "http://purl.obolibrary.org/obo/GO_"),
    ("RO", "http://purl.obolibrary.org/obo/RO_"),
    ("IAO", "http://purl.obolibrary.org/obo/IAO_"),
    # test preferred mixed case is preserved
    ("WBPhenotype", "http://purl.obolibrary.org/obo/WBPhenotype_"),
]
"""Expected OBO prefixes, including those that conflict with other sources."""

EXPECTED_LINKED_DATA = [
    ("owl", "http://www.w3.org/2002/07/owl#"),
    ("skos", "http://www.w3.org/2004/02/skos/core#"),
    ("dcterms", "http://purl.org/dc/terms/"),
]
"""Expected LinkedData namespaces. These are highly stable and it is vital that this library gives
correct results since these are frequently used in application logic"""

EXPECTED_PREFIX_CC = [
    ("owl", "http://www.w3.org/2002/07/owl#"),
    ("foaf", "http://xmlns.com/foaf/0.1/"),
    ("skos", "http://www.w3.org/2004/02/skos/core#"),
    # ("dcterms", "http://purl.org/dc/terms/"),
]
"""Expected LinkedData namespaces. These are highly stable and it is vital that this library gives
correct results since these are frequently used in application logic"""

EXPECTED_OTHER = [
    ("biopax", "http://www.biopax.org/release/biopax-level3.owl#"),
    ("wd", "http://www.wikidata.org/entity/"),
]


class TextPrefixMaps(unittest.TestCase):
    """Tests the core canonical PrefixExpansions logic of prefixmaps"""

    def setUp(self) -> None:
        self.obo_context = load_context("obo")
        self.prefixcc_context = load_context("prefixcc")
        self.bioregistry_context = load_context("bioregistry")
        self.merged_context = load_context("merged")
        self.linked_data_context = load_context("linked_data")
        self.dyn_merged_context = load_multi_context(
            ["obo", "go", "linked_data", "bioregistry.upper", "prefixcc"]
        )

    def test_obo_expansions(self):
        """Tests OBO prefix expansions"""
        ctxt = self.obo_context
        pm = ctxt.as_dict()
        # test prefix->ns
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pm[pfx], exp)
        pmi = ctxt.as_inverted_dict()
        # test ns->prefix
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pmi[exp], pfx)

    def test_linked_data_expansions(self):
        """Tests LinkedData prefix expansions"""
        ctxt = self.linked_data_context
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, exp in EXPECTED_LINKED_DATA:
            self.assertEqual(pm[pfx], exp)
            self.assertEqual(pmi[exp], pfx)

    def test_load_and_roundtrip(self):
        """
        Tests basic I/O
        """
        ctxt = self.obo_context
        pm = ctxt.as_dict()
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
        # ctxt.add_prefix("CL", "http://purl.obolibrary.org/obo/UBERON_")
        # pe = ctxt.prefix_expansions[-1]
        # self.assertEqual(pe.status, StatusType.multi_alias)
        # self.assertFalse(pe.canonical())
        # test all as expected
        pm = ctxt.as_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pm[pfx], exp)

    def test_merged(self):
        ctxt = self.merged_context
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, exp in EXPECTED_OBO + EXPECTED_PREFIX_CC + EXPECTED_OTHER:
            self.assertEqual(pm[pfx], exp)
            self.assertEqual(pmi[exp], pfx)
        issues = ctxt.validate()
        for issue in issues:
            print(issue)

    def test_dyn_merged(self):
        ctxt = self.dyn_merged_context
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, exp in EXPECTED_OBO + EXPECTED_PREFIX_CC + EXPECTED_OTHER:
            self.assertEqual(pm[pfx], exp)
            self.assertEqual(pmi[exp], pfx)

    def test_prefixcc(self):
        ctxt = self.prefixcc_context
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, exp in EXPECTED_PREFIX_CC:
            self.assertEqual(pm[pfx], exp)
            self.assertEqual(pmi[exp], pfx)

    def test_from_upstream(self):
        ctxt = load_context("obo", refresh=True)
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, exp in EXPECTED_OBO:
            self.assertEqual(pm[pfx], exp)
            self.assertEqual(pmi[exp], pfx)

    def test_synonyms(self):
        # prefixmaps prioritizes GO prefix resolution over bioregistry in terms of adding canonical tags.
        canonical = "PMID:1234"
        converter = prefixmaps.load_converter("merged")
        # TODO "pmid:1234", "pubmed:1234"
        others = ["PMID:1234", "MEDLINE:1234", canonical]
        for curie in others:
            with self.subTest(curie=curie):
                self.assertEqual(canonical, converter.standardize_curie(curie))

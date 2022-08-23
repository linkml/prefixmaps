import unittest

from bioregistry import curie_from_iri, get_iri

from prefixmaps.ingest.ingest_bioregistry import from_bioregistry

OBO = "obo"
SEMWEB = "semweb"
OTHER = "other"
priority = [
    "obofoundry",
    "semweb",
    "default",
    "bioportal",
    "miriam",
    "ols",
    "n2t",
]

# expected expansions for different priorities
EXPECTED_CURIE_TO_URI = [
    ("GO:0008150", "http://purl.obolibrary.org/obo/GO_0008150", OBO),
    # ("GEO:000000396", "http://purl.obolibrary.org/obo/GEO_000000396", OBO),
    ("owl:Thing", "http://www.w3.org/2002/07/owl#Thing", SEMWEB),
    (
        "oio:inSubset",
        "http://www.geneontology.org/formats/oboInOwl#inSubset",
        OTHER,
    ),
]

EXPECTED = [
    ("GEOGEO", "http://purl.obolibrary.org/obo/GEO_"),
    ("GO", "http://purl.obolibrary.org/obo/GO_"),
    ("FBbt", "http://purl.obolibrary.org/obo/FBbt_"),
]

EXPECTED_UPPER = [
    ("GEOGEO", "http://purl.obolibrary.org/obo/GEO_"),
    ("FlyBase", "http://identifiers.org/fb/"),
    ("HGNC", "http://identifiers.org/hgnc/"),
    ("FBbt", "http://purl.obolibrary.org/obo/FBbt_"),
]


class TestBioregistry(unittest.TestCase):
    def test_from_bioregistry(self):
        ctxt = from_bioregistry()
        # for pe in ctxt.prefix_expansions:
        #    print(pe)
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, ns in EXPECTED:
            self.assertEqual(pm[pfx], ns)
            self.assertEqual(pmi[ns], pfx)

    def test_from_bioregistry_as_upper(self):
        ctxt = from_bioregistry(upper=True)
        # for pe in ctxt.prefix_expansions:
        #    print(pe)
        pm = ctxt.as_dict()
        pmi = ctxt.as_inverted_dict()
        for pfx, ns in EXPECTED_UPPER:
            self.assertEqual(pm[pfx], ns)
            self.assertEqual(pmi[ns], pfx)

    def test_curie_to_iri(self):
        for curie, iri, _ in EXPECTED_CURIE_TO_URI:
            self.assertEqual(get_iri(curie, priority=priority), iri)

    @unittest.skip("TODO: GEO should not be GEOGEO in bioregistry prefixmap")
    def test_iri_to_curie(self):
        for curie, iri, _ in EXPECTED_CURIE_TO_URI:
            self.assertEqual(curie_from_iri(iri), curie)

    def test_semweb_iri_to_curie(self):
        for curie, iri, categ in EXPECTED_CURIE_TO_URI:
            if categ == SEMWEB:
                self.assertEqual(curie_from_iri(iri), curie)

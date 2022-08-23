import unittest

from prefixmaps.ingest.ingest_go import parse_go_xrefs, parse_go_xrefs_from_remote
from prefixmaps.io.writer import context_to_file
from tests import INPUT_DIR, OUTPUT_DIR


class TextETLForGO(unittest.TestCase):
    def test_go(self):
        with open(str(INPUT_DIR / "go-db-xrefs.yaml")) as file:
            ctxt = parse_go_xrefs(file)
            # for pe in ctxt.prefix_expansions:
            #    print(vars(pe))
            pm = ctxt.as_dict()
            self.assertEqual(
                pm["WBPhenotype"],
                "http://purl.obolibrary.org/obo/WBPhenotype_",
            )
            outpath = OUTPUT_DIR / "foo.csv"
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            with open(str(outpath), "w", encoding="UTF-8") as outfile:
                context_to_file(ctxt, outfile)

    def test_go_from_remote(self):
        ctxt = parse_go_xrefs_from_remote()
        # for pe in ctxt.prefix_expansions:
        #    print(vars(pe))
        pm = ctxt.as_dict()
        self.assertEqual(pm["WBPhenotype"], "http://purl.obolibrary.org/obo/WBPhenotype_")
        outpath = OUTPUT_DIR / "bar.csv"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(str(outpath), "w", encoding="UTF-8") as outfile:
            context_to_file(ctxt, outfile)

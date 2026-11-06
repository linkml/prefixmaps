import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from prefixmaps.datamodel.context import Context, StatusType
from prefixmaps.ingest.etl_runner import CONTEXTS, echo_changes, run_etl
from prefixmaps.ingest.ingest_jsonld import (
    from_prefixcc,
    from_prefixcc_snapshot,
    is_excluded_from_prefixcc,
    load_prefixcc_exclusions,
)
from prefixmaps.io.parser import context_from_file, load_context
from tests import INPUT_DIR

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

    def test_prefix_cc_exclusions(self):
        """Test that excluded entries are dropped when ingesting prefix.cc."""
        with open(INPUT_DIR / "prefix-cc.context.jsonld", encoding="utf-8") as file:
            response = mock.Mock(json=mock.Mock(return_value=json.load(file)))
        with mock.patch("requests.get", return_value=response):
            pm = from_prefixcc().as_dict()
        for pfx, ns in EXPECTED:
            self.assertEqual(pm[pfx], ns)
        # the input has veelana and ljkl on excluded hosts, and the excluded prefixes leaks and bgcat
        for pfx in ["veelana", "ljkl", "leaks", "bgcat"]:
            self.assertNotIn(pfx, pm)

    def test_excluded_hosts(self):
        """Test that hosts are excluded with their subdomains, but not lookalike domains."""
        exclusions = {"hosts": {"onlyfans.com": "spam"}, "prefixes": {}}
        for namespace, expected in [
            ("https://onlyfans.com/x/", True),
            ("http://www.onlyfans.com/x/", True),
            ("https://OnlyFans.com/x/", True),
            ("https://notonlyfans.com/x/", False),
            ("https://example.org/onlyfans.com/", False),
            ("https://onlyfans.com./x/", True),
            ("http://[abc/", False),
        ]:
            with self.subTest(namespace=namespace):
                self.assertEqual(expected, is_excluded_from_prefixcc("x", namespace, exclusions))

    def test_snapshot(self):
        """Test that the ETL uses the bundled prefix.cc snapshot without network access."""
        with mock.patch("requests.get", side_effect=AssertionError("prefix.cc was downloaded")):
            context = CONTEXTS["prefixcc"]()
        self.assertEqual(load_context("prefixcc").as_dict(), context.as_dict())
        self.assertEqual(from_prefixcc_snapshot().as_dict(), context.as_dict())
        statuses = [pe.canonical() for pe in context.prefix_expansions]
        self.assertEqual(
            sorted(statuses, reverse=True), statuses, msg="canonical rows must come first"
        )
        # canonical-first ordering only reproduces the merge if prefix.cc has no prefix aliases
        self.assertNotIn(StatusType.prefix_alias, {pe.status for pe in context.prefix_expansions})

    def test_snapshot_exclusions(self):
        """Test that a new exclusion is applied to the bundled prefix.cc snapshot."""
        self.assertIn("foaf", load_context("prefixcc").as_dict())
        exclusions = {"hosts": {"xmlns.com": "test"}, "prefixes": {}}
        target = "prefixmaps.ingest.ingest_jsonld.load_prefixcc_exclusions"
        with mock.patch(target, return_value=exclusions):
            self.assertNotIn("foaf", from_prefixcc_snapshot().as_dict())

    def test_prefix_cc_without_context(self):
        """Test that a prefix.cc response without a JSON-LD context is still rejected."""
        response = mock.Mock(json=mock.Mock(return_value={}))
        with mock.patch("requests.get", return_value=response):
            with self.assertRaises(ValueError):
                from_prefixcc()

    def test_exclusions_loader(self):
        """Test that empty sections are allowed, but misspelled sections are rejected."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prefixcc.excluded.yaml"
            for text, expected in [
                ("", {"hosts": {}, "prefixes": {}}),
                ("hosts:\nprefixes:\n  a: spam\n", {"hosts": {}, "prefixes": {"a": "spam"}}),
            ]:
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    self.assertEqual(expected, load_prefixcc_exclusions(path))
            path.write_text("prefixess:\n  a: spam\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_prefixcc_exclusions(path)

    def test_exclusions_file(self):
        """Test that the exclusions file has reasons for all entries."""
        exclusions = load_prefixcc_exclusions()
        for kind, entries in exclusions.items():
            for entry, reason in entries.items():
                with self.subTest(kind=kind, entry=entry):
                    self.assertTrue(reason)

    def test_echo_changes(self):
        """Test that refreshing prefix.cc reports added and removed expansions."""
        old, new = Context("prefixcc"), Context("prefixcc")
        old.add_prefix("a", "https://example.org/a/")
        old.add_prefix("b", "https://example.org/b/")
        new.add_prefix("a", "https://example.org/a2/")
        new.add_prefix("b", "https://example.org/b/")
        new.add_prefix("c", "https://example.org/c/")
        new.add_prefix("d", "https://example.org/c/")
        with mock.patch("click.echo") as echo:
            echo_changes(old, new)
        self.assertEqual(
            [
                mock.call("- prefixcc a https://example.org/a/ canonical"),
                mock.call("+ prefixcc a https://example.org/a2/ canonical"),
                mock.call("+ prefixcc c https://example.org/c/ canonical"),
                mock.call("+ prefixcc d https://example.org/c/ namespace_alias"),
            ],
            echo.call_args_list,
        )

    def test_refresh_prefixcc(self):
        """Test that the ETL only downloads prefix.cc when asked, and then reports the changes."""
        for refresh, expected in [(False, "a"), (True, "b")]:
            snapshot, download = Context("prefixcc"), Context("prefixcc")
            snapshot.add_prefix("a", "https://example.org/a/")
            download.add_prefix("b", "https://example.org/b/")
            sources = {name: (lambda name=name: Context(name)) for name in CONTEXTS}
            sources["prefixcc"] = lambda snapshot=snapshot: snapshot
            target = "prefixmaps.ingest.etl_runner.from_prefixcc"
            with self.subTest(refresh=refresh), tempfile.TemporaryDirectory() as directory:
                with mock.patch.dict(CONTEXTS, sources), mock.patch("click.echo") as echo:
                    with mock.patch(target, return_value=download) as from_prefixcc_mock:
                        run_etl(directory, refresh_prefixcc=refresh)
                self.assertEqual(refresh, from_prefixcc_mock.called)
                self.assertEqual(refresh, echo.called)
                for name in ["prefixcc", "merged"]:
                    with open(Path(directory) / f"{name}.csv", encoding="utf-8") as file:
                        self.assertEqual([expected], list(context_from_file(name, file).as_dict()))

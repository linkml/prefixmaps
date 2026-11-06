"""Test that no bundled context contains prefix.cc entries that must never be imported."""

import unittest

from prefixmaps import load_context
from prefixmaps.data import context_paths
from prefixmaps.ingest.ingest_jsonld import (
    is_excluded_from_prefixcc,
    load_prefixcc_exclusions,
)


class TestPrefixCCExclusions(unittest.TestCase):
    """Test that no bundled context contains prefix.cc entries that must never be imported."""

    def test_no_excluded_entries(self):
        """Test bundled contexts against prefixcc.excluded.yaml, see issue #61."""
        exclusions = load_prefixcc_exclusions()
        hosts_only = {"hosts": exclusions["hosts"], "prefixes": {}}
        for key in context_paths:
            with self.subTest(key=key):
                excluded = [
                    (expansion.prefix, expansion.namespace)
                    for expansion in load_context(key).prefix_expansions
                    # excluded hosts are spam in any source, excluded prefixes only in prefix.cc
                    if is_excluded_from_prefixcc(
                        expansion.prefix,
                        expansion.namespace,
                        (
                            exclusions
                            if "prefixcc" in (key, expansion.expansion_source)
                            else hosts_only
                        ),
                    )
                ]
                self.assertEqual([], excluded)

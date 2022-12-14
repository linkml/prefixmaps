"""Test loading data into CURIEs converters."""

import unittest

from curies import Converter

import prefixmaps


class TestCuries(unittest.TestCase):
    """Test loading data into CURIEs converters."""

    def test_load(self):
        """Test loading bioportal content."""
        prefix = "WIKIPATHWAYS"
        uri_prefix_1 = "http://vocabularies.wikipathways.org/wp#"
        uri_prefix_2 = "http://vocabularies.wikipathways.org/wpTypes#"

        context = prefixmaps.load_context("bioportal")
        context_namespaces = {expansion.namespace for expansion in context.prefix_expansions}
        self.assertIn(uri_prefix_1, context_namespaces)
        self.assertIn(uri_prefix_2, context_namespaces)

        extended_prefix_map = context.as_extended_prefix_map()
        converter = Converter.from_extended_prefix_map(extended_prefix_map)

        # prefix map checks
        self.assertIn(prefix, converter.prefix_map)
        self.assertEqual(uri_prefix_1, converter.prefix_map[prefix])
        self.assertNotIn(uri_prefix_2, converter.prefix_map.values())

        # Reverse prefix map checks
        self.assertIn(uri_prefix_1, converter.reverse_prefix_map)
        self.assertIn(uri_prefix_2, converter.reverse_prefix_map)
        self.assertEqual(prefix, converter.reverse_prefix_map[uri_prefix_1])
        self.assertEqual(prefix, converter.reverse_prefix_map[uri_prefix_2])

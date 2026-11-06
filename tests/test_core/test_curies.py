"""Test loading data into CURIEs converters."""

import unittest

from curies import Converter, DuplicatePrefixes, DuplicateURIPrefixes

import prefixmaps
from prefixmaps.data import context_paths
from prefixmaps.datamodel.context import Context, PrefixExpansion, StatusType


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

        converter = context.as_converter()
        self.assertIsInstance(converter, Converter)

        self.assertEqual(converter.prefix_map, prefixmaps.load_converter("bioportal").prefix_map)
        self.assertEqual(converter.prefix_map, prefixmaps.load_converter(["bioportal"]).prefix_map)

        # prefix map checks
        self.assertIn(prefix, converter.prefix_map)
        self.assertEqual(uri_prefix_1, converter.prefix_map[prefix])
        self.assertNotIn(uri_prefix_2, converter.prefix_map.values())

        # Reverse prefix map checks
        self.assertIn(uri_prefix_1, converter.reverse_prefix_map)
        self.assertIn(uri_prefix_2, converter.reverse_prefix_map)
        self.assertEqual(prefix, converter.reverse_prefix_map[uri_prefix_1])
        self.assertEqual(prefix, converter.reverse_prefix_map[uri_prefix_2])

    def test_load_all(self):
        """Test that every bundled context can be loaded into a converter."""
        for key in context_paths:
            with self.subTest(key=key):
                self.assertIsInstance(prefixmaps.load_converter(key), Converter)

    def test_duplicate_uri_prefixes(self):
        """Test that two records sharing a URI prefix are still rejected."""
        context = Context("test")
        context.prefix_expansions = [
            PrefixExpansion("test", "a", "https://example.org/a/", StatusType.canonical),
            PrefixExpansion("test", "b", "https://example.org/a/", StatusType.canonical),
        ]
        with self.assertRaises(DuplicateURIPrefixes):
            context.as_converter()

    def test_duplicate_prefixes(self):
        """Test that two records sharing a prefix synonym are still rejected."""
        context = Context("test")
        context.prefix_expansions = [
            PrefixExpansion("test", "a", "https://example.org/a/", StatusType.canonical),
            PrefixExpansion("test", "b", "https://example.org/b/", StatusType.canonical),
            PrefixExpansion("test", "c", "https://example.org/a/", StatusType.namespace_alias),
            PrefixExpansion("test", "c", "https://example.org/b/", StatusType.namespace_alias),
        ]
        with self.assertRaises(DuplicatePrefixes):
            context.as_converter()

    def test_duplicate_uri_prefix_synonyms(self):
        """Test that a URI prefix synonym shared with another record is still rejected."""
        context = Context("test")
        context.prefix_expansions = [
            PrefixExpansion("test", "a", "https://example.org/a/", StatusType.canonical),
            PrefixExpansion("test", "b", "https://example.org/b/", StatusType.canonical),
            PrefixExpansion("test", "b", "https://example.org/a/", StatusType.prefix_alias),
        ]
        with self.assertRaises(DuplicateURIPrefixes):
            context.as_converter()

    def test_duplicate_canonical_prefix_synonym(self):
        """Test that a prefix synonym equal to another record's prefix is still rejected."""
        context = Context("test")
        context.prefix_expansions = [
            PrefixExpansion("test", "a", "https://example.org/a/", StatusType.canonical),
            PrefixExpansion("test", "b", "https://example.org/b/", StatusType.canonical),
            PrefixExpansion("test", "a", "https://example.org/b/", StatusType.namespace_alias),
        ]
        with self.assertRaises(DuplicatePrefixes):
            context.as_converter()

    def test_duplicate_shared_uri_prefix_synonym(self):
        """Test that two records sharing a URI prefix synonym are still rejected."""
        context = Context("test")
        context.prefix_expansions = [
            PrefixExpansion("test", "a", "https://example.org/a/", StatusType.canonical),
            PrefixExpansion("test", "b", "https://example.org/b/", StatusType.canonical),
            PrefixExpansion("test", "a", "https://example.org/z/", StatusType.prefix_alias),
            PrefixExpansion("test", "b", "https://example.org/z/", StatusType.prefix_alias),
        ]
        with self.assertRaises(DuplicateURIPrefixes):
            context.as_converter()

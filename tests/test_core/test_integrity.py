"""This module contains tests for data integrity."""

import unittest
from typing import Mapping

from prefixmaps import load_context
from prefixmaps.datamodel.context import Context, StatusType
from prefixmaps.data import context_paths

from collections import Counter


class TestIntegrity(unittest.TestCase):
    """A test case that checks data integrity."""

    def setUp(self) -> None:
        """Set up the test case with all contexts."""
        self.contexts: Mapping[str, Context] = {
            key: load_context(key)
            for key, path in context_paths.items()
        }

    def test_unique_canonical_prefix(self):
        """Test that no contexts have duplicate canonical prefixes."""
        for key, context in self.contexts.items():
            with self.subTest(key=key):
                counter = Counter(
                    expansion.prefix
                    for expansion in context.prefix_expansions
                    if expansion.canonical()
                )
                duplicates = {
                    prefix
                    for prefix, count in counter.items()
                    if count > 1
                }
                self.assertEqual(
                    set(),
                    duplicates,
                    msg=f"[{key} multiple canonical records with the same prefix"
                )

    def test_unique_canonical_namespace(self):
        """Test that no contexts have duplicate canonical namespaces."""
        for key, context in self.contexts.items():
            with self.subTest(key=key):
                counter = Counter(
                    expansion.namespace
                    for expansion in context.prefix_expansions
                    if expansion.canonical()
                )
                duplicates = {
                    prefix
                    for prefix, count in counter.items()
                    if count > 1
                }
                self.assertEqual(
                    set(),
                    duplicates,
                    msg=f"[{key} multiple canonical records with the same namespace"
                )

    def test_valid_namespace_synonyms(self):
        """Test that namespace aliases have a valid prefix."""
        for key, context in self.contexts.items():
            with self.subTest(key=key):
                canonical_prefixes = {
                    expansion.prefix
                    for expansion in context.prefix_expansions
                    if expansion.canonical()
                }
                # A namespace alias means that the prefix should be the same as a canonical prefix somewhere
                missing_canonical_prefixes = {
                    expansion.prefix
                    for expansion in context.prefix_expansions
                    if expansion.status == StatusType.namespace_alias and expansion.prefix not in canonical_prefixes
                }
                self.assertEqual(
                    set(),
                    missing_canonical_prefixes,
                    msg=f"[{key}] prefix aliases were missing corresponding canonical prefixes",
                )

    def test_valid_prefix_synonyms(self):
        """Test that prefix aliases have a valid namespace."""
        for key, context in self.contexts.items():
            with self.subTest(key=key):
                canonical_namespaces = {
                    expansion.namespace
                    for expansion in context.prefix_expansions
                    if expansion.canonical()
                }
                # A prefix alias means that the namespace should appear in a canoncail record as well
                missing_canonical_namespace = {
                    expansion.namespace
                    for expansion in context.prefix_expansions
                    if expansion.status == StatusType.prefix_alias and expansion.namespace not in canonical_namespaces
                }
                self.assertEqual(
                    set(),
                    missing_canonical_namespace,
                    msg=f"[{key}] prefix aliases were missing corresponding canonical prefixes",
                )

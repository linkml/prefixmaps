import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Mapping, Optional

__all__ = [
    "StatusType",
    "PrefixExpansion",
    "Context",
]

CONTEXT = str
PREFIX = str
NAMESPACE = str
PREFIX_EXPANSION_DICT = Mapping[PREFIX, NAMESPACE]
INVERSE_PREFIX_EXPANSION_DICT = Mapping[NAMESPACE, PREFIX]


PREFIX_RE = re.compile(r"^[\w\.]+$")
NAMESPACE_RE = re.compile(r"http[s]?://[\w\.\-\/]+[#/_:]$")


class StatusType(Enum):
    """
    Classification of prefix expansions
    """

    canonical = "canonical"
    prefix_alias = "prefix_alias"
    namespace_alias = "namespace_alias"
    multi_alias = "multi_alias"


@dataclass
class PrefixExpansion:
    """
    An individual mapping between a prefix and a namespace
    """

    context: CONTEXT
    prefix: PREFIX
    namespace: NAMESPACE
    status: StatusType

    def canonical(self) -> bool:
        """
        True if this is the canonical expansions

        :return:
        """
        return self.status == StatusType.canonical

    def validate(self) -> List[str]:
        messages = []
        if not PREFIX_RE.match(self.prefix):
            messages.append(f"prefix {self.prefix} does not match {PREFIX_RE}")
        if not NAMESPACE_RE.match(self.namespace):
            messages.append(
                f"namespace {self.namespace} does not match {NAMESPACE_RE}\
                (prefix: {self.prefix})"
            )
        return messages


@dataclass
class Context:
    """
    A context is a localized collection of prefix expansions
    """

    name: CONTEXT
    description: Optional[str] = None
    prefix_expansions: List[PrefixExpansion] = field(default_factory=lambda: [])
    comments: List[str] = None
    location: Optional[str] = None
    format: Optional[str] = None
    merged_from: Optional[List[str]] = None
    upper: bool = None
    lower: bool = None

    def combine(self, context: "Context"):
        """
        Merge a context into this one

        The current context stays primary

        :param context:
        :return:
        """
        for pe in context.prefix_expansions:
            self.add_prefix(pe.prefix, pe.namespace, pe.status)

    def add_prefix(
        self,
        prefix: PREFIX,
        namespace: NAMESPACE,
        status: StatusType = StatusType.canonical,
        preferred: bool = False,
    ):
        """
        Adds a prefix expansion to this context

        The current context stays canonical. Additional prefixes
        added may be classified as aliases

        If upper or lower is set for this context, the the
        prefix will be auto-case normalized,
        UNLESS preferred=True

        :param prefix:
        :param namespace:
        :param status:
        :param preferred:
        :return:
        """
        # TODO: check status
        if not preferred:
            if self.upper:
                prefix = prefix.upper()
                if self.lower:
                    raise ValueError("Cannot set both upper AND lower")
            if self.lower:
                prefix = prefix.lower()
        prefixes = self.prefixes(lower=True)
        namespaces = self.namespaces(lower=True)
        if prefix.lower() in prefixes:
            if namespace.lower() in namespaces:
                return
                # status = StatusType.multi_alias
            else:
                status = StatusType.prefix_alias
        else:
            if namespace.lower() in namespaces:
                status = StatusType.namespace_alias
        self.prefix_expansions.append(
            PrefixExpansion(
                context=self.name,
                prefix=prefix,
                namespace=namespace,
                status=status,
            )
        )

    def filter(self, prefix: PREFIX = None, namespace: NAMESPACE = None):
        """
        Returns namespaces matching query

        :param prefix:
        :param namespace:
        :return:
        """
        filtered_pes = []
        for pe in self.prefix_expansions:
            if prefix is not None and prefix != pe.prefix:
                continue
            if namespace is not None and namespace != pe.namespace:
                continue
            filtered_pes.append(pe)
        return filtered_pes

    def prefixes(self, lower=False) -> List[str]:
        """
        All unique prefixes in all prefix expansions

        :return:
        """
        if lower:
            return list({pe.prefix.lower() for pe in self.prefix_expansions})
        else:
            return list({pe.prefix for pe in self.prefix_expansions})

    def namespaces(self, lower=False) -> List[str]:
        """
        All unique namespaces in all prefix expansions

        :return:
        """
        if lower:
            return list({pe.namespace.lower() for pe in self.prefix_expansions})
        else:
            return list({pe.namespace for pe in self.prefix_expansions})

    def as_dict(self) -> PREFIX_EXPANSION_DICT:
        """
        Returns a mapping between canonical prefixes and expansions

        :return:
        """
        return {pe.prefix: pe.namespace for pe in self.prefix_expansions if pe.canonical()}

    def as_inverted_dict(self) -> INVERSE_PREFIX_EXPANSION_DICT:
        """
        Returns a mapping between canonical expansions and prefixes

        :return:
        """
        return {pe.namespace: pe.prefix for pe in self.prefix_expansions if pe.canonical()}

    def validate(self, canonical_only=True) -> List[str]:
        messages = []
        for pe in self.prefix_expansions:
            if canonical_only and not pe.canonical():
                continue
            messages += pe.validate()
        # namespaces = self.namespaces(lower=True)
        # prefixes = self.namespaces(lower=True)
        return messages

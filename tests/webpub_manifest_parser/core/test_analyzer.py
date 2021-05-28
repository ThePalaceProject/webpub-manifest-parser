import datetime
from unittest import TestCase

from parameterized import parameterized

from webpub_manifest_parser.core.analyzer import BaseAnalyzerError, NodeFinder
from webpub_manifest_parser.core.ast import (
    CollectionList,
    CompactCollection,
    Link,
    LinkList,
    Manifestlike,
    PresentationMetadata,
)
from webpub_manifest_parser.core.registry import LinkRelationsRegistry
from webpub_manifest_parser.odl.ast import (
    ODLFeed,
    ODLLicense,
    ODLLicenseMetadata,
    ODLPublication,
)
from webpub_manifest_parser.opds2 import (
    OPDS2LinkRelationsRegistry,
    OPDS2MediaTypesRegistry,
)
from webpub_manifest_parser.opds2.ast import (
    OPDS2Feed,
    OPDS2FeedMetadata,
    OPDS2Group,
    OPDS2Navigation,
    OPDS2Publication,
)
from webpub_manifest_parser.rwpm import (
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
)
from webpub_manifest_parser.rwpm.ast import RWPMManifest


class AnalyzerTest(TestCase):
    """Base class for all analyzer tests."""

    def check_analyzer_errors(
        self, context_errors, expected_errors, error_class=BaseAnalyzerError
    ):
        """Ensure that lists of expected and real errors are the same.

        :param context_errors: List of errors returned by a parser
        :type context_errors: List[BaseAnalyzerError]

        :param expected_errors: List of expected errors
        :type expected_errors: List[BaseAnalyzerError]

        :param error_class: Type of the error
        :type error_class: Type
        """
        self.assertEqual(len(expected_errors), len(context_errors))

        for expected_error in expected_errors:
            self.assertIsInstance(expected_error, error_class)

            for context_error in context_errors:
                self.assertIsInstance(context_error, error_class)

                if (
                    context_error.node.__class__ == expected_error.node.__class__
                    and (
                        (
                            context_error.node_property is None
                            and expected_error.node_property is None
                        )
                        or (
                            context_error.node_property is not None
                            and expected_error.node_property is not None
                            and context_error.node_property.__class__
                            == expected_error.node_property.__class__
                        )
                    )
                    and context_error.error_message == expected_error.error_message
                ):
                    break
            else:
                self.fail(
                    "Expected error for {0} node's property '{1}' with error message \"{2}\" wasn't raised".format(
                        expected_error.node.__class__,
                        expected_error.node_property.key
                        if expected_error.node_property
                        else "",
                        expected_error.error_message,
                    )
                )


MANIFEST = Manifestlike(
    metadata=PresentationMetadata(title="Manifest # 1"),
    links=LinkList(
        [
            Link(
                href="http://example.com",
                rels=["test"],
            )
        ]
    ),
)

RWPM_MANIFEST = RWPMManifest(
    metadata=PresentationMetadata("test"),
    links=LinkList(
        [
            Link(
                href="example.com",
                rels=[RWPMLinkRelationsRegistry.SELF.key],
            )
        ]
    ),
    reading_order=CompactCollection(
        role=RWPMCollectionRolesRegistry.READING_ORDER.key,
        links=LinkList([Link(href="test")]),
    ),
    resources=CompactCollection(
        role=RWPMCollectionRolesRegistry.READING_ORDER.key,
        links=LinkList([Link(href="test")]),
    ),
)

OPDS2_FEED = OPDS2Feed(
    metadata=OPDS2FeedMetadata(title="test"),
    links=LinkList(
        [
            Link(
                href="http://example.com",
                rels=[RWPMLinkRelationsRegistry.SELF.key],
            )
        ]
    ),
    publications=CollectionList(
        [
            OPDS2Publication(
                metadata=PresentationMetadata(title="Publication 1"),
                links=LinkList(
                    [
                        Link(
                            href="http://example.com",
                            rels=[OPDS2LinkRelationsRegistry.ACQUISITION.key],
                        )
                    ]
                ),
            )
        ]
    ),
    navigation=OPDS2Navigation(
        links=LinkList(
            [
                Link(
                    href="/new",
                    title="New Publications",
                    _type=OPDS2MediaTypesRegistry.OPDS_FEED,
                    rels=["current"],
                )
            ]
        )
    ),
    groups=CollectionList(
        [
            OPDS2Group(
                metadata=OPDS2FeedMetadata(title="Group 1"),
                publications=CollectionList(
                    [
                        OPDS2Publication(
                            metadata=PresentationMetadata(title="Publication 1.1"),
                            links=LinkList(
                                [
                                    Link(
                                        href="http://example.com",
                                        rels=[
                                            OPDS2LinkRelationsRegistry.ACQUISITION.key
                                        ],
                                    )
                                ]
                            ),
                        )
                    ]
                ),
            )
        ]
    ),
)

ODL_FEED = ODLFeed(
    metadata=OPDS2FeedMetadata(title="test"),
    links=LinkList(
        [
            Link(
                href="http://example.com",
                rels=[LinkRelationsRegistry.SELF.key],
            )
        ]
    ),
    publications=CollectionList(
        [
            ODLPublication(
                metadata=PresentationMetadata(title="Publication 1"),
                links=LinkList([Link(href="http://example.com")]),
                licenses=CollectionList(
                    [
                        ODLLicense(
                            metadata=ODLLicenseMetadata(
                                identifier="license-1",
                                formats=["text/html"],
                                created=datetime.datetime(2021, 1, 1, 0, 0, 0),
                            ),
                            links=LinkList([Link(href="http://example.com")]),
                        )
                    ]
                ),
            ),
            ODLPublication(
                metadata=PresentationMetadata(title="Publication 1"),
                links=LinkList([Link(href="http://example.com")]),
                licenses=CollectionList(
                    [
                        ODLLicense(
                            metadata=ODLLicenseMetadata(
                                identifier="license-1",
                                formats=["text/html"],
                                created=datetime.datetime(2021, 1, 1, 0, 0, 0),
                            ),
                            links=LinkList([Link(href="http://example.com")]),
                        )
                    ]
                ),
            ),
        ]
    ),
)


class NodeFinderTest(TestCase):
    @parameterized.expand(
        [
            (
                "Core. Find a Manifestlike parent of the Link node: it must return the root Manifestlike node",
                MANIFEST,
                MANIFEST.links[0],
                Manifestlike,
                MANIFEST,
            ),
            (
                "Core. Find a CompactCollection parent of the Link node: it must return the root Manifestlike node",
                MANIFEST,
                MANIFEST.links[0],
                CompactCollection,
                MANIFEST,
            ),
            (
                "Core. Find a Link parent of the Link node: it must return the same Link node",
                MANIFEST,
                MANIFEST.links[0],
                Link,
                MANIFEST.links[0],
            ),
            (
                "Core. Find a PresentationMetadata parent of the Link node: it must return None",
                MANIFEST,
                MANIFEST.links[0],
                PresentationMetadata,
                None,
            ),
            (
                "RWPM. Find a RWPMManifest parent of the Link node: it must return the root RWPMManifest node",
                RWPM_MANIFEST,
                RWPM_MANIFEST.reading_order.links[0],
                RWPMManifest,
                RWPM_MANIFEST,
            ),
            (
                "RWPM. Find a CompactCollection parent of the Link node: "
                "it must return the reading_order node not the root node",
                RWPM_MANIFEST,
                RWPM_MANIFEST.reading_order.links[0],
                CompactCollection,
                RWPM_MANIFEST.reading_order,
            ),
            (
                "OPDS 2.x. Find a OPDS2Publication parent of the Link node: "
                "it must return the OPDS2Publication node where the link is located",
                OPDS2_FEED,
                OPDS2_FEED.groups[0].publications[0].links[0],
                OPDS2Publication,
                OPDS2_FEED.groups[0].publications[0],
            ),
            (
                "OPDS 2.x. Find a OPDS2Group parent of the Link node: "
                "it must return the OPDS2Group node where the links's publication is located",
                OPDS2_FEED,
                OPDS2_FEED.groups[0].publications[0].links[0],
                OPDS2Group,
                OPDS2_FEED.groups[0],
            ),
            (
                "OPDS 2.x. Find a OPDS2Fed parent of the Link node: "
                "it must return the root OPDS2Feed node",
                OPDS2_FEED,
                OPDS2_FEED.groups[0].publications[0].links[0],
                OPDS2Feed,
                OPDS2_FEED,
            ),
            (
                "ODL 2.x. Find a ODLLicense parent of the Link node: "
                "it must return the ODLLicense node where the link is located",
                ODL_FEED,
                ODL_FEED.publications[0].licenses[0].links[0],
                ODLLicense,
                ODL_FEED.publications[0].licenses[0],
            ),
            (
                "ODL 2.x. Find a ODLPublication parent of the Link node: "
                "it must return the ODLPublication node where the link is located",
                ODL_FEED,
                ODL_FEED.publications[0].licenses[0].links[0],
                ODLPublication,
                ODL_FEED.publications[0],
            ),
            (
                "ODL 2.x. Find a ODLFeed parent of the Link node: "
                "it must return the root ODLFeed node",
                ODL_FEED,
                ODL_FEED.publications[0].licenses[0].links[0],
                ODLFeed,
                ODL_FEED,
            ),
        ]
    )
    def test(self, _, root, target_node, target_parent_class, expected_parent_node):
        node_finder = NodeFinder()

        parent_node = node_finder.find_parent_or_self(root, target_node, target_parent_class)

        self.assertEqual(expected_parent_node, parent_node)

import datetime

from parameterized import parameterized

from tests.webpub_manifest_parser.core.test_analyzer import AnalyzerTest
from webpub_manifest_parser.core.ast import CollectionList, Link, LinkList
from webpub_manifest_parser.core.registry import LinkRelationsRegistry
from webpub_manifest_parser.core.semantic import (
    MANIFEST_MISSING_SELF_LINK_ERROR,
    SemanticAnalyzerError,
)
from webpub_manifest_parser.odl.ast import (
    ODLFeed,
    ODLLicense,
    ODLLicenseMetadata,
    ODLPublication,
)
from webpub_manifest_parser.odl.semantic import (
    ODL_FEED_CONTAINS_REDUNDANT_FACETS_SUBCOLLECTIONS_ERROR,
    ODL_FEED_CONTAINS_REDUNDANT_GROUPS_SUBCOLLECTIONS_ERROR,
    ODL_FEED_CONTAINS_REDUNDANT_NAVIGATION_SUBCOLLECTION_ERROR,
    ODL_FEED_MISSING_PUBLICATIONS_SUBCOLLECTION_ERROR,
    ODL_LICENSE_MUST_CONTAIN_CHECKOUT_LINK_TO_LICENSE_STATUS_DOCUMENT_ERROR,
    ODL_LICENSE_MUST_CONTAIN_SELF_LINK_TO_LICENSE_INFO_DOCUMENT_ERROR,
    ODL_PUBLICATION_MUST_CONTAIN_EITHER_LICENSES_OR_ACQUISITION_LINK_ERROR,
    ODLSemanticAnalyzer,
)
from webpub_manifest_parser.opds2 import (
    OPDS2CollectionRolesRegistry,
    OPDS2LinkRelationsRegistry,
    OPDS2MediaTypesRegistry,
)
from webpub_manifest_parser.opds2.ast import (
    OPDS2Facet,
    OPDS2FeedMetadata,
    OPDS2Group,
    OPDS2Navigation,
    OPDS2PublicationMetadata,
)


class ODLSemanticAnalyzerTest(AnalyzerTest):
    @parameterized.expand(
        [
            (
                "when_feed_does_not_contain_publications",
                ODLFeed(metadata=OPDS2FeedMetadata(title="test"), links=LinkList()),
                [
                    ODL_FEED_MISSING_PUBLICATIONS_SUBCOLLECTION_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=ODLFeed.publications,
                    ),
                    MANIFEST_MISSING_SELF_LINK_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=None,
                    ),
                ],
            ),
            (
                "when_feed_contains_groups",
                ODLFeed(
                    metadata=OPDS2FeedMetadata(title="test"),
                    links=LinkList(),
                    groups=CollectionList([OPDS2Group()]),
                ),
                [
                    ODL_FEED_MISSING_PUBLICATIONS_SUBCOLLECTION_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=ODLFeed.publications,
                    ),
                    MANIFEST_MISSING_SELF_LINK_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=None,
                    ),
                    ODL_FEED_CONTAINS_REDUNDANT_GROUPS_SUBCOLLECTIONS_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=ODLFeed.groups,
                    ),
                ],
            ),
            (
                "when_feed_contains_facets",
                ODLFeed(
                    metadata=OPDS2FeedMetadata(title="test"),
                    links=LinkList(),
                    facets=CollectionList([OPDS2Facet()]),
                ),
                [
                    ODL_FEED_MISSING_PUBLICATIONS_SUBCOLLECTION_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=ODLFeed.publications,
                    ),
                    MANIFEST_MISSING_SELF_LINK_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=None,
                    ),
                    ODL_FEED_CONTAINS_REDUNDANT_FACETS_SUBCOLLECTIONS_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=ODLFeed.facets,
                    ),
                ],
            ),
            (
                "when_feed_contains_navigation",
                ODLFeed(
                    metadata=OPDS2FeedMetadata(title="test"),
                    links=LinkList(),
                    navigation=OPDS2Navigation(),
                ),
                [
                    ODL_FEED_MISSING_PUBLICATIONS_SUBCOLLECTION_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=ODLFeed.publications,
                    ),
                    MANIFEST_MISSING_SELF_LINK_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=None,
                    ),
                    ODL_FEED_CONTAINS_REDUNDANT_NAVIGATION_SUBCOLLECTION_ERROR(
                        node=ODLFeed(metadata=OPDS2FeedMetadata(title="test")),
                        node_property=ODLFeed.navigation,
                    ),
                ],
            ),
            (
                "when_publication_does_not_contain_licenses_nor_acquisition_link",
                ODLFeed(
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
                                metadata=OPDS2PublicationMetadata(
                                    title="Publication 1"
                                ),
                                licenses=CollectionList(),
                            )
                        ]
                    ),
                ),
                [
                    ODL_PUBLICATION_MUST_CONTAIN_EITHER_LICENSES_OR_ACQUISITION_LINK_ERROR(
                        node=ODLPublication(
                            metadata=OPDS2PublicationMetadata(title="Publication 1")
                        ),
                        node_property=None,
                    )
                ],
            ),
            (
                "when_publication_does_not_contain_licenses_nor_acquisition_link",
                ODLFeed(
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
                                metadata=OPDS2PublicationMetadata(
                                    title="Publication 1"
                                ),
                                links=LinkList([Link(href="http://example.com")]),
                            )
                        ]
                    ),
                ),
                [
                    ODL_PUBLICATION_MUST_CONTAIN_EITHER_LICENSES_OR_ACQUISITION_LINK_ERROR(
                        node=ODLPublication(
                            metadata=OPDS2PublicationMetadata(title="Publication 1")
                        ),
                        node_property=None,
                    )
                ],
            ),
            (
                "when_publication_does_not_contain_licenses_and_has_a_oa_link",
                ODLFeed(
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
                                metadata=OPDS2PublicationMetadata(
                                    title="Publication 1"
                                ),
                                links=LinkList(
                                    [
                                        Link(
                                            href="http://example.com",
                                            rels=[
                                                OPDS2LinkRelationsRegistry.OPEN_ACCESS.key
                                            ],
                                        )
                                    ]
                                ),
                            )
                        ]
                    ),
                ),
                [],
            ),
            (
                "when_publication_does_not_contain_licenses_and_has_an_acquisition_link",
                ODLFeed(
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
                                metadata=OPDS2PublicationMetadata(
                                    title="Publication 1"
                                ),
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
                ),
                [],
            ),
            (
                "when_publication_does_not_contain_licenses_and_has_an_unknown_acquisition_link",
                ODLFeed(
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
                                metadata=OPDS2PublicationMetadata(
                                    title="Publication 1"
                                ),
                                links=LinkList(
                                    [
                                        Link(
                                            href="http://example.com",
                                            rels=[
                                                f"{OPDS2LinkRelationsRegistry.ACQUISITION.key}/unknown"
                                            ],
                                        )
                                    ]
                                ),
                            )
                        ]
                    ),
                ),
                [],
            ),
            (
                "when_license_does_not_contain_self_link_and_borrow_link",
                ODLFeed(
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
                                metadata=OPDS2PublicationMetadata(
                                    title="Publication 1"
                                ),
                                links=LinkList([Link(href="http://example.com")]),
                                licenses=CollectionList(
                                    [
                                        ODLLicense(
                                            metadata=ODLLicenseMetadata(
                                                identifier="license-1",
                                                formats=["text/html"],
                                                created=datetime.datetime(
                                                    2021, 1, 1, 0, 0, 0
                                                ),
                                            )
                                        )
                                    ]
                                ),
                            )
                        ]
                    ),
                ),
                [
                    ODL_LICENSE_MUST_CONTAIN_SELF_LINK_TO_LICENSE_INFO_DOCUMENT_ERROR(
                        node=ODLLicense(
                            metadata=ODLLicenseMetadata(identifier="license-1")
                        ),
                        node_property=None,
                    ),
                    ODL_LICENSE_MUST_CONTAIN_CHECKOUT_LINK_TO_LICENSE_STATUS_DOCUMENT_ERROR(
                        node=ODLLicense(
                            metadata=ODLLicenseMetadata(identifier="license-1")
                        ),
                        node_property=None,
                    ),
                ],
            ),
        ]
    )
    def test_semantic_analyzer_raises_error(self, _, manifest, expected_errors):
        """Ensure that the ODL 2.x semantic analyzer correctly raises errors and saves them in the current context.

        :param manifest: AST object containing the RWPM-like manifest
        :type manifest: webpub_manifest_parser.odl.ast.ODLFeed

        :param expected_errors: List of expected semantic errors
        :type expected_errors: List[webpub_manifest_parser.core.analyzer.BaseAnalyzerError]
        """
        # Arrange
        media_types_registry = OPDS2MediaTypesRegistry()
        link_relations_registry = OPDS2LinkRelationsRegistry()
        collection_roles_registry = OPDS2CollectionRolesRegistry()
        semantic_analyzer = ODLSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        semantic_analyzer.visit(manifest)

        # Assert
        self.check_analyzer_errors(
            semantic_analyzer.context.errors, expected_errors, SemanticAnalyzerError
        )

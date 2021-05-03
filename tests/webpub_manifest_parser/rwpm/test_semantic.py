from parameterized import parameterized

from tests.webpub_manifest_parser.core.test_analyzer import AnalyzerTest
from webpub_manifest_parser.core.ast import (
    CompactCollection,
    Link,
    LinkList,
    PresentationMetadata,
)
from webpub_manifest_parser.core.semantic import (
    MANIFEST_SELF_LINK_WRONG_HREF_FORMAT_ERROR,
    SemanticAnalyzerError,
)
from webpub_manifest_parser.rwpm.ast import RWPMManifest
from webpub_manifest_parser.rwpm.registry import (
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
    RWPMMediaTypesRegistry,
)
from webpub_manifest_parser.rwpm.semantic import (
    READING_ORDER_SUBCOLLECTION_LINK_MISSING_TYPE_PROPERTY_ERROR,
    RESOURCES_SUBCOLLECTION_MISSING_LINK_TYPE_PROPERTY_ERROR,
    RWPMSemanticAnalyzer,
)


class RWPMSemanticAnalyzerTest(AnalyzerTest):
    @parameterized.expand(
        [
            (
                "when_reading_order_link_does_not_have_type_property",
                RWPMManifest(
                    metadata=PresentationMetadata("test"),
                    links=LinkList(
                        [
                            Link(
                                href="http://example.com",
                                rels=[RWPMLinkRelationsRegistry.SELF.key],
                            )
                        ]
                    ),
                    reading_order=CompactCollection(
                        role=RWPMCollectionRolesRegistry.READING_ORDER.key,
                        links=LinkList([Link(href="test")]),
                    ),
                ),
                [
                    READING_ORDER_SUBCOLLECTION_LINK_MISSING_TYPE_PROPERTY_ERROR(
                        node=Link(href="test"), node_property=Link.type
                    )
                ],
            ),
            (
                "when_resources_link_does_not_have_type_property",
                RWPMManifest(
                    metadata=PresentationMetadata("test"),
                    links=LinkList(
                        [
                            Link(
                                href="http://example.com",
                                rels=[RWPMLinkRelationsRegistry.SELF.key],
                            )
                        ]
                    ),
                    reading_order=CompactCollection(
                        role=RWPMCollectionRolesRegistry.READING_ORDER.key,
                        links=LinkList(
                            [Link(href="test", _type=RWPMMediaTypesRegistry.JPEG.key)]
                        ),
                    ),
                    resources=CompactCollection(
                        role=RWPMCollectionRolesRegistry.READING_ORDER.key,
                        links=LinkList([Link(href="test")]),
                    ),
                ),
                [
                    RESOURCES_SUBCOLLECTION_MISSING_LINK_TYPE_PROPERTY_ERROR(
                        node=Link(href="test"), node_property=Link.type
                    )
                ],
            ),
            (
                "when_reading_order_and_resource_links_do_not_have_type_property_and_self_link_has_incorrect_href",
                RWPMManifest(
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
                ),
                [
                    MANIFEST_SELF_LINK_WRONG_HREF_FORMAT_ERROR(
                        node=Link(href="example.com"), node_property=Link.href
                    ),
                    READING_ORDER_SUBCOLLECTION_LINK_MISSING_TYPE_PROPERTY_ERROR(
                        node=Link(href="test"), node_property=Link.type
                    ),
                    RESOURCES_SUBCOLLECTION_MISSING_LINK_TYPE_PROPERTY_ERROR(
                        node=Link(href="test"), node_property=Link.type
                    ),
                ],
            ),
        ]
    )
    def test_semantic_analyzer_raises_error(self, _, manifest, expected_errors):
        """Ensure that the base semantic analyzer correctly raises errors and saves them in the current context.

        :param manifest: AST object containing the RWPM-like manifest
        :type manifest: webpub_manifest_parser.core.ast.Node

        :param expected_errors: List of expected semantic errors
        :type expected_errors: List[webpub_manifest_parser.core.analyzer.BaseAnalyzerError]
        """
        # Arrange
        media_types_registry = RWPMMediaTypesRegistry()
        link_relations_registry = RWPMLinkRelationsRegistry()
        collection_roles_registry = RWPMCollectionRolesRegistry()
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        semantic_analyzer.visit(manifest)

        # Assert
        self.check_analyzer_errors(
            semantic_analyzer.context.errors, expected_errors, SemanticAnalyzerError
        )

    def test_semantic_analyzer_does_correctly_processes_valid_ast(self):
        manifest = RWPMManifest(
            metadata=PresentationMetadata("test"),
            links=LinkList(
                [
                    Link(
                        href="http://example.com",
                        rels=[RWPMLinkRelationsRegistry.SELF.key],
                    )
                ]
            ),
            reading_order=CompactCollection(
                role=RWPMCollectionRolesRegistry.READING_ORDER.key,
                links=LinkList(
                    [
                        Link(href="test", _type=RWPMMediaTypesRegistry.JPEG.key),
                    ]
                ),
            ),
            resources=CompactCollection(
                role=RWPMCollectionRolesRegistry.READING_ORDER.key,
                links=LinkList(
                    [
                        Link(href="test", _type=RWPMMediaTypesRegistry.JPEG.key),
                    ]
                ),
            ),
        )
        media_types_registry = RWPMMediaTypesRegistry()
        link_relations_registry = RWPMLinkRelationsRegistry()
        collection_roles_registry = RWPMCollectionRolesRegistry()
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        semantic_analyzer.visit(manifest)

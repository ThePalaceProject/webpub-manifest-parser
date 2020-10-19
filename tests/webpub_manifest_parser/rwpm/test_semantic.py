from unittest import TestCase

from nose.tools import assert_raises, eq_
from parameterized import parameterized

from webpub_manifest_parser.core.ast import (
    CompactCollection,
    Link,
    LinkList,
    PresentationMetadata,
)
from webpub_manifest_parser.rwpm.ast import RWPMManifest
from webpub_manifest_parser.rwpm.registry import (
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
    RWPMMediaTypesRegistry,
)
from webpub_manifest_parser.rwpm.semantic import (
    MISSING_READING_ORDER_LINK_TYPE_PROPERTY_ERROR,
    MISSING_RESOURCES_LINK_TYPE_PROPERTY_ERROR,
    RWPMSemanticAnalyzer,
)


class SemanticAnalyzerTest(TestCase):
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
                                rel=[RWPMLinkRelationsRegistry.SELF.key],
                            )
                        ]
                    ),
                    reading_order=CompactCollection(
                        role=RWPMCollectionRolesRegistry.READING_ORDER.key,
                        links=LinkList([Link(href="test")]),
                    ),
                ),
                MISSING_READING_ORDER_LINK_TYPE_PROPERTY_ERROR,
            ),
            (
                "when_resources_link_does_not_have_type_property",
                RWPMManifest(
                    metadata=PresentationMetadata("test"),
                    links=LinkList(
                        [
                            Link(
                                href="http://example.com",
                                rel=[RWPMLinkRelationsRegistry.SELF.key],
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
                MISSING_RESOURCES_LINK_TYPE_PROPERTY_ERROR,
            ),
        ]
    )
    def test_semantic_analyzer_raises_error(self, _, manifest, expected_error):
        # Arrange
        media_types_registry = RWPMMediaTypesRegistry()
        link_relations_registry = RWPMLinkRelationsRegistry()
        collection_roles_registry = RWPMCollectionRolesRegistry()
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        with assert_raises(expected_error.__class__) as assert_raises_context:
            semantic_analyzer.visit(manifest)

        # Assert
        eq_(str(assert_raises_context.exception), str(expected_error))

    def test_semantic_analyzer_does_correctly_processes_valid_ast(self):
        manifest = RWPMManifest(
            metadata=PresentationMetadata("test"),
            links=LinkList(
                [
                    Link(
                        href="http://example.com",
                        rel=[RWPMLinkRelationsRegistry.SELF.key],
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

from parameterized import parameterized

from tests.webpub_manifest_parser.core.test_analyzer import AnalyzerTest
from webpub_manifest_parser.core.ast import (
    Link,
    LinkList,
    Manifestlike,
    PresentationMetadata,
)
from webpub_manifest_parser.core.registry import LinkRelationsRegistry, Registry
from webpub_manifest_parser.core.semantic import (
    MANIFEST_LINK_MISSING_REL_PROPERTY_ERROR,
    MANIFEST_MISSING_SELF_LINK_ERROR,
    MANIFEST_SELF_LINK_WRONG_HREF_FORMAT_ERROR,
    SemanticAnalyzer,
    SemanticAnalyzerError,
)


class SemanticAnalyzerTest(AnalyzerTest):
    @parameterized.expand(
        [
            (
                "when_manifest_link_rel_property_is_missing",
                Manifestlike(
                    metadata=PresentationMetadata(title="Manifest # 1"),
                    links=LinkList([Link(href="http://example.com")]),
                ),
                [
                    MANIFEST_LINK_MISSING_REL_PROPERTY_ERROR(
                        node=Link(href="http://example.com"), node_property=Link.rels
                    ),
                    MANIFEST_MISSING_SELF_LINK_ERROR(
                        node=Manifestlike(
                            metadata=PresentationMetadata(identifier="Manifest # 1")
                        ),
                        node_property=None,
                    ),
                ],
            ),
            (
                "when_manifest_self_link_is_missing",
                Manifestlike(
                    metadata=PresentationMetadata(title="Manifest # 1"),
                    links=LinkList(
                        [
                            Link(
                                href="http://example.com",
                                rels=["test"],
                            )
                        ]
                    ),
                ),
                [
                    MANIFEST_MISSING_SELF_LINK_ERROR(
                        node=Manifestlike(
                            metadata=PresentationMetadata(title="Manifest # 1")
                        ),
                        node_property=None,
                    )
                ],
            ),
            (
                "when_manifest_self_link_has_wrong_href",
                Manifestlike(
                    metadata=PresentationMetadata(title="Manifest # 1"),
                    links=LinkList(
                        [
                            Link(
                                href="example.com",
                                rels=[LinkRelationsRegistry.SELF.key],
                            )
                        ]
                    ),
                ),
                [
                    MANIFEST_SELF_LINK_WRONG_HREF_FORMAT_ERROR(
                        node=Link(href="example.com"), node_property=Link.href
                    )
                ],
            ),
            (
                "when_manifest_link_rel_property_is_missing_and_self_link_has_incorrect_href",
                Manifestlike(
                    metadata=PresentationMetadata(title="Manifest # 1"),
                    links=LinkList(
                        [
                            Link(href="http://example.com"),
                            Link(
                                href="example.com",
                                rels=[LinkRelationsRegistry.SELF.key],
                            ),
                        ]
                    ),
                ),
                [
                    MANIFEST_LINK_MISSING_REL_PROPERTY_ERROR(
                        node=Link(href="http://example.com"), node_property=Link.rels
                    ),
                    MANIFEST_SELF_LINK_WRONG_HREF_FORMAT_ERROR(
                        node=Link(href="example.com"), node_property=Link.href
                    ),
                ],
            ),
        ]
    )
    def test_semantic_analyzer_raises_error(self, _, manifest, expected_errors):
        """Ensure that the base semantic analyzer correctly raises errors and saves them in the current context.

        :param manifest: AST object containing the RWPM-like manifest
        :type manifest: webpub_manifest_parser.core.ast.Manifestlike

        :param expected_errors: List of expected semantic errors
        :type expected_errors: List[webpub_manifest_parser.core.analyzer.BaseAnalyzerError]
        """
        # Arrange
        media_types_registry = Registry()
        link_relations_registry = Registry()
        collection_roles_registry = Registry()
        semantic_analyzer = SemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        semantic_analyzer.visit(manifest)

        # Assert
        self.check_analyzer_errors(
            semantic_analyzer.context.errors, expected_errors, SemanticAnalyzerError
        )

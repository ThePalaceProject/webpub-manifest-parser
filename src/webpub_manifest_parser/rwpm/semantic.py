import logging
from functools import partial

from multipledispatch import dispatch

from webpub_manifest_parser.core.ast import (
    Collection,
    CollectionList,
    CompactCollection,
    Link,
    LinkList,
    Manifestlike,
    Metadata,
)
from webpub_manifest_parser.core.semantic import LinkSemanticError, SemanticAnalyzer

READING_ORDER_SUBCOLLECTION_LINK_MISSING_TYPE_PROPERTY_ERROR = partial(
    LinkSemanticError,
    message="readingOrder subcollection's link '{0}' does not have a required 'type' property",
)
RESOURCES_SUBCOLLECTION_MISSING_LINK_TYPE_PROPERTY_ERROR = partial(
    LinkSemanticError,
    message="resources subcollection's link '{0}' does not have a required 'type' property",
)


class RWPMSemanticAnalyzer(SemanticAnalyzer):
    """RWPM semantic analyzer."""

    def __init__(
        self, media_types_registry, link_relations_registry, collection_roles_registry
    ):
        """Initialize a new instance of RWPMSemanticAnalyzer class.

        :param media_types_registry: Media types registry
        :type media_types_registry: python_rwpm_parser.registry.Registry

        :param link_relations_registry: Link relations registry
        :type link_relations_registry: python_rwpm_parser.registry.Registry

        :param collection_roles_registry: Collections roles registry
        :type collection_roles_registry: python_rwpm_parser.registry.Registry
        """
        super().__init__(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        self._logger = logging.getLogger(__name__)

    @dispatch(Manifestlike)
    def visit(self, node):
        """Perform semantic analysis of the manifest node.

        :param node: Manifest's metadata
        :type node: RWPMManifest
        """
        super().visit(node)

        for link in node.reading_order.links:
            with self._record_errors():
                if link.type is None:
                    raise READING_ORDER_SUBCOLLECTION_LINK_MISSING_TYPE_PROPERTY_ERROR(
                        node=link, node_property=Link.type
                    )

        if node.resources:
            for link in node.resources.links:
                with self._record_errors():
                    if link.type is None:
                        raise RESOURCES_SUBCOLLECTION_MISSING_LINK_TYPE_PROPERTY_ERROR(
                            node=link, node_property=Link.type
                        )

    @dispatch(Metadata)
    def visit(self, node):
        """Perform semantic analysis of the manifest's metadata.

        :param node: Manifest's metadata
        :type node: Metadata
        """
        super().visit(node)

    @dispatch(LinkList)
    def visit(self, node):
        """Perform semantic analysis of the list of links.

        :param node: Manifest's metadata
        :type node: LinkList
        """
        super().visit(node)

    @dispatch(Link)
    def visit(self, node):
        """Perform semantic analysis of the link node.

        :param node: Link node
        :type node: Link
        """
        super().visit(node)

    @dispatch(CollectionList)
    def visit(self, node):
        """Perform semantic analysis of the list of sub-collections.

        :param node: CollectionList node
        :type node: CollectionList
        """
        super().visit(node)

    @dispatch(CompactCollection)
    def visit(self, node):
        """Perform semantic analysis of the compact collection node.

        :param node: Collection node
        :type node: CompactCollection
        """
        super().visit(node)

    @dispatch(Collection)
    def visit(self, node):
        """Perform semantic analysis of the collection node.

        :param node: Collection node
        :type node: Collection
        """
        super().visit(node)

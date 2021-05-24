import logging
from functools import partial

from multipledispatch import dispatch

from webpub_manifest_parser.core.analyzer import BaseAnalyzer, BaseAnalyzerError
from webpub_manifest_parser.core.ast import (
    Collection,
    CollectionList,
    CompactCollection,
    Link,
    LinkList,
    Manifestlike,
    Metadata,
    Visitor,
)
from webpub_manifest_parser.core.parsers import (
    URIParser,
    URIReferenceParser,
    ValueParserError,
)
from webpub_manifest_parser.core.registry import LinkRelationsRegistry
from webpub_manifest_parser.utils import encode, first_or_default


class SemanticAnalyzerError(BaseAnalyzerError):
    """Exception raised in the case of semantic errors."""

    def __init__(self, node, node_property=None, message=None, inner_exception=None):
        """Initialize a new instance of ManifestSemanticError class.

        :param node: RWPM node
        :type node: webpub_manifest_parser.core.ast.Node

        :param node_property: AST node's property associated with the error
        :type node_property: Optional[webpub_manifest_parser.core.properties.Property]

        :param message: Parameterized string containing description of the error occurred
            and the placeholder for the feed's identifier
        :type message: Optional[str]

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        message = self._format_message(node, node_property, message, inner_exception)

        super(SemanticAnalyzerError, self).__init__(
            node, node_property, message, inner_exception
        )

    def _format_message(
        self,
        node,  # pylint: disable=unused-argument
        node_property=None,  # pylint: disable=unused-argument
        message=None,
        inner_exception=None,  # pylint: disable=unused-argument
    ):
        """Format the error message.

        :param node: RWPM node
        :type node: webpub_manifest_parser.core.ast.Node

        :param node_property: AST node's property associated with the error
        :type node_property: Optional[webpub_manifest_parser.core.properties.Property]

        :param message: Parameterized string containing description of the error occurred
        :type message: Optional[str]

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        return message


class ManifestSemanticError(SemanticAnalyzerError):
    """Base class for semantic errors related to RWPM-like manifests."""

    def _format_message(
        self, node, node_property=None, message=None, inner_exception=None
    ):
        """Format the error message.

        :param node: RWPM-like manifest
        :type node: webpub_manifest_parser.core.ast.Manifestlike

        :param node_property: AST node's property associated with the error
        :type node_property: Optional[webpub_manifest_parser.core.properties.Property]

        :param message: Parameterized string containing description of the error occurred
            and the placeholder for the feed's identifier
        :type message: Optional[str]

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        if not isinstance(node, Manifestlike):
            raise ValueError(
                "Argument 'node' must be an instance of {0}".format(Manifestlike)
            )

        if node.metadata:
            if node.metadata.title:
                message = message.format(node.metadata.title)
            elif node.metadata.identifier:
                message = message.format(node.metadata.identifier)

        return message


class LinkSemanticError(SemanticAnalyzerError):
    """Base class for semantic errors related to RWPM-like links."""

    def _format_message(
        self, node, node_property=None, message=None, inner_exception=None
    ):
        """Format the error message.

        :param node: RWPM-like link
        :type node: webpub_manifest_parser.core.ast.Link

        :param node_property: AST node's property associated with the error
        :type node_property: Optional[webpub_manifest_parser.core.properties.Property]

        :param message: Parameterized string containing description of the error occurred
            and the placeholder for the feed's identifier
        :type message: Optional[str]

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        if not isinstance(node, Link):
            raise ValueError("Argument 'node' must be an instance of {0}".format(Link))

        message = message.format(node.href)

        return message


MANIFEST_LINK_MISSING_REL_PROPERTY_ERROR = partial(
    LinkSemanticError,
    message="Manifest link '{0}' does not have a required 'rel' property",
)

MANIFEST_MISSING_SELF_LINK_ERROR = partial(
    ManifestSemanticError, message="Manifest '{0}' does not have a required 'self' link"
)

MANIFEST_SELF_LINK_WRONG_HREF_FORMAT_ERROR = partial(
    LinkSemanticError,
    message="Manifest 'self' link's href {0} is incorrect: "
    "it must be an absolute URI to the canonical location of the manifest",
)


class CollectionWrongFormatError(SemanticAnalyzerError):
    """Exception raised in the case when collection's format (compact, full) doesn't not conform with its role."""

    def __init__(self, collection, inner_exception=None):
        """Initialize a new instance of CollectionWrongFormat class.

        :param collection: Collection with a wrong format
        :type collection: python_rwpm_parser.ast.Collection

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        message = "Collection {0} must be {1} but it is not".format(
            collection.role.key, "compact" if collection.role.compact else "full"
        )

        super(CollectionWrongFormatError, self).__init__(
            collection, None, message, inner_exception
        )

        self._collection = collection

    @property
    def collection(self):
        """Return a collection with a wrong format.

        :return: Collection with a wrong format
        :rtype: python_rwpm_parser.ast.Collection
        """
        return self._collection


class SemanticAnalyzer(BaseAnalyzer, Visitor):
    """Visitor performing semantic analysis of the RWPM-compatible documents."""

    def __init__(
        self, media_types_registry, link_relations_registry, collection_roles_registry
    ):
        """Initialize a new instance of SemanticAnalyzer.

        :param media_types_registry: Media types registry
        :type media_types_registry: webpub_manifest_parser.core.registry.Registry

        :param link_relations_registry: Link relations registry
        :type link_relations_registry: webpub_manifest_parser.core.registry.Registry

        :param collection_roles_registry: Collections roles registry
        :type collection_roles_registry: webpub_manifest_parser.core.registry.Registry
        """
        super(SemanticAnalyzer, self).__init__()

        self._media_types_registry = media_types_registry
        self._link_relations_registry = link_relations_registry
        self._collection_roles_registry = collection_roles_registry
        self._logger = logging.getLogger(__name__)

    def _check_manifest_self_link(self, node):
        """Ensure that manifest contains a correctly formatted self link.

        :param node: Manifest-like node
        :type node: Manifestlike
        """
        for link in node.links:
            if not link.rels:
                with self._record_errors():
                    raise MANIFEST_LINK_MISSING_REL_PROPERTY_ERROR(
                        node=link, node_property=Link.rels
                    )

        self_link = first_or_default(
            node.links.get_by_rel(LinkRelationsRegistry.SELF.key)
        )

        if self_link is None:
            raise MANIFEST_MISSING_SELF_LINK_ERROR(node=node, node_property=None)

        parser = URIParser()

        try:
            parser.parse(self_link.href)
        except ValueParserError:
            raise MANIFEST_SELF_LINK_WRONG_HREF_FORMAT_ERROR(
                node=self_link, node_property=Link.href
            )

    @dispatch(Manifestlike)
    def visit(self, node):
        """Perform semantic analysis of the manifest node.

        :param node: Manifest-like node
        :type node: Manifestlike
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        self.context.reset()

        with self._record_errors():
            node.metadata.accept(self)

        with self._record_errors():
            node.links.accept(self)

        with self._record_errors():
            self._check_manifest_self_link(node)

        with self._record_errors():
            node.sub_collections.accept(self)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(Metadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the manifest's metadata.

        :param node: Manifest's metadata
        :type node: Metadata
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(LinkList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of links.

        :param node: Manifest's metadata
        :type node: LinkList
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        for link in node:
            with self._record_errors():
                link.accept(self)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(Link)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the link node.

        :param node: Link node
        :type node: Link
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        if not node.templated:
            parser = URIReferenceParser()
            parser.parse(node.href)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(CollectionList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of sub-collections.

        :param node: CollectionList node
        :type node: CollectionList
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        for collection in node:
            with self._record_errors():
                collection.accept(self)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(CompactCollection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the compact collection node.

        :param node: Collection node
        :type node: CompactCollection
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        with self._record_errors():
            node.links.accept(self)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(Collection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the collection node.

        :param node: Collection node
        :type node: Collection
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        with self._record_errors():
            node.metadata.accept(self)

        with self._record_errors():
            node.links.accept(self)

        with self._record_errors():
            node.sub_collections.accept(self)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

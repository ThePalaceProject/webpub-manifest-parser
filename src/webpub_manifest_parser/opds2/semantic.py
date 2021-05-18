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
from webpub_manifest_parser.core.semantic import SemanticAnalyzer, SemanticAnalyzerError
from webpub_manifest_parser.opds2.ast import (
    OPDS2FeedMetadata,
    OPDS2Group,
    OPDS2Navigation,
    OPDS2Publication,
)
from webpub_manifest_parser.opds2.registry import OPDS2LinkRelationsRegistry
from webpub_manifest_parser.utils import cast, encode

MISSING_REQUIRED_FEED_SUB_COLLECTIONS = partial(
    SemanticAnalyzerError,
    message="OPDS 2.0 feed must contain one of the following sub-collections: publications, navigation, groups",
)

MISSING_NAVIGATION_LINK_TITLE_ERROR = partial(
    SemanticAnalyzerError, message="OPDS 2.0 navigation link must contain a title"
)

MISSING_ACQUISITION_LINK = partial(
    SemanticAnalyzerError,
    message="OPDS 2.0 publication must contain at least one acquisition link",
)

WRONG_GROUP_STRUCTURE = partial(
    SemanticAnalyzerError,
    message="OPDS 2.0 group must contain either a single navigation collection or a single publications collection",
)


class OPDS2SemanticAnalyzer(SemanticAnalyzer):
    """OPDS 2.0 semantic analyzer."""

    def __init__(
        self, media_types_registry, link_relations_registry, collection_roles_registry
    ):
        """Initialize a new instance of OPDS2SemanticAnalyzer class.

        :param media_types_registry: Media types registry
        :type media_types_registry: python_rwpm_parser.registry.Registry

        :param link_relations_registry: Link relations registry
        :type link_relations_registry: python_rwpm_parser.registry.Registry

        :param collection_roles_registry: Collections roles registry
        :type collection_roles_registry: python_rwpm_parser.registry.Registry
        """
        super(OPDS2SemanticAnalyzer, self).__init__(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        self._logger = logging.getLogger(__name__)

    @dispatch(Manifestlike)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the manifest node.

        :param node: Manifest's metadata
        :type node: OPDS2Feed
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        super(OPDS2SemanticAnalyzer, self).visit(node)

        if (
            node.publications is None
            and node.navigation is None
            and node.groups is None
        ):
            with self._record_errors():
                raise MISSING_REQUIRED_FEED_SUB_COLLECTIONS(
                    node=node, node_property=None
                )

        if node.publications is not None:
            with self._record_errors():
                node.publications.accept(self)
        if node.navigation is not None:
            with self._record_errors():
                node.navigation.accept(self)
        if node.groups is not None:
            with self._record_errors():
                node.groups.accept(self)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(OPDS2FeedMetadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the feed's metadata.

        :param node: Feed's metadata
        :type node: OPDS2FeedMetadata
        """

    @dispatch(Metadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the publication's metadata.

        :param node: Publication's metadata
        :type node: Metadata
        """
        super(OPDS2SemanticAnalyzer, self).visit(node)

    @dispatch(LinkList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of links.

        :param node: Manifest's metadata
        :type node: LinkList
        """
        super(OPDS2SemanticAnalyzer, self).visit(node)

    @dispatch(Link)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the link node.

        :param node: Link node
        :type node: Link
        """
        super(OPDS2SemanticAnalyzer, self).visit(node)

    @dispatch(CollectionList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of sub-collections.

        :param node: CollectionList node
        :type node: CollectionList
        """
        super(OPDS2SemanticAnalyzer, self).visit(node)

    @dispatch(OPDS2Publication)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the OPDS 2.0 publication.

        :param node: OPDS 2.0 publication
        :type node: OPDS2Publication
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        super(OPDS2SemanticAnalyzer, self).visit(node)

        acquisition_links = [
            OPDS2LinkRelationsRegistry.PREVIEW.key,
            OPDS2LinkRelationsRegistry.ACQUISITION.key,
            OPDS2LinkRelationsRegistry.BUY.key,
            OPDS2LinkRelationsRegistry.OPEN_ACCESS.key,
            OPDS2LinkRelationsRegistry.BORROW.key,
            OPDS2LinkRelationsRegistry.SAMPLE.key,
            OPDS2LinkRelationsRegistry.SUBSCRIBE.key,
        ]

        for link in node.links:
            if link.rels is not None and set(acquisition_links) & set(link.rels):
                break
        else:
            with self._record_errors():
                raise MISSING_ACQUISITION_LINK(node=node, node_property=None)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(OPDS2Group)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the OPDS 2.0 group.

        :param node: OPDS 2.0 group
        :type node: OPDS2Group
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        # FIXME: It seems that group definition relaxes requirements for having metadata
        # It means we have to override default behaviour
        # super(OPDS2SemanticAnalyzer, self).visit(node)

        if node.metadata:
            with self._record_errors():
                node.metadata.accept(self)

        if node.publications and node.navigation:
            with self._record_errors():
                raise WRONG_GROUP_STRUCTURE(node=node, node_property=None)

        if node.publications:
            with self._record_errors():
                node.publications.accept(self)
        if node.navigation:
            with self._record_errors():
                node.navigation.accept(self)
        if node.links:
            with self._record_errors():
                node.links.accept(self)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(OPDS2Navigation)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the OPDS 2.0 navigation.

        :param node: OPDS 2.0 navigation
        :type node: OPDS2Navigation
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        with self._record_errors():
            self.visit(cast(node, CompactCollection))

        for link in node.links:
            if link.title is None:
                with self._record_errors():
                    raise MISSING_NAVIGATION_LINK_TITLE_ERROR(
                        node=link, node_property=Link.title
                    )

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(CompactCollection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the compact collection node.

        :param node: Collection node
        :type node: CompactCollection
        """
        super(OPDS2SemanticAnalyzer, self).visit(node)

    @dispatch(Collection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the collection node.

        :param node: Collection node
        :type node: Collection
        """
        super(OPDS2SemanticAnalyzer, self).visit(node)

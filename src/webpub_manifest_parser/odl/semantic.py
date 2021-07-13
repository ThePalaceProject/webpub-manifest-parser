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
from webpub_manifest_parser.core.semantic import (
    ManifestSemanticError,
    SemanticAnalyzer,
    SemanticAnalyzerError,
)
from webpub_manifest_parser.odl.ast import ODLFeed, ODLLicense, ODLPublication
from webpub_manifest_parser.odl.registry import ODLMediaTypesRegistry
from webpub_manifest_parser.opds2.ast import OPDS2FeedMetadata
from webpub_manifest_parser.opds2.registry import OPDS2LinkRelationsRegistry
from webpub_manifest_parser.utils import encode, first_or_default


class ODLPublicationSemanticError(SemanticAnalyzerError):
    """Base class for semantic errors related to ODL 2.x feeds."""

    def _format_message(
        self, node, node_property=None, message=None, inner_exception=None
    ):
        """Format the error message.

        :param node: ODL 2.x publication
        :type node: webpub_manifest_parser.odl.ast.ODLPublication

        :param node_property: AST node's property associated with the error
        :type node_property: Optional[webpub_manifest_parser.core.properties.Property]

        :param message: Parameterized string containing description of the error occurred
            and the placeholder for the feed's identifier
        :type message: Optional[str]

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        if not isinstance(node, ODLPublication):
            raise ValueError(
                "Argument 'node' must be an instance of {0}".format(ODLPublication)
            )

        if node.metadata:
            if node.metadata.title:
                message = message.format(node.metadata.title)
            elif node.metadata.identifier:
                message = message.format(node.metadata.identifier)

        return message


class ODLLicenseSemanticError(SemanticAnalyzerError):
    """Base class for semantic errors related to ODL 2.x feeds."""

    def _format_message(
        self, node, node_property=None, message=None, inner_exception=None
    ):
        """Format the error message.

        :param node: ODL 2.x license
        :type node: webpub_manifest_parser.odl.ast.ODLLicense

        :param node_property: AST node's property associated with the error
        :type node_property: Optional[webpub_manifest_parser.core.properties.Property]

        :param message: Parameterized string containing description of the error occurred
            and the placeholder for the feed's identifier
        :type message: Optional[str]

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        if not isinstance(node, ODLLicense):
            raise ValueError(
                "Argument 'node' must be an instance of {0} class".format(ODLLicense)
            )

        if node.metadata:
            message = message.format(node.metadata.identifier)

        return message


ODL_FEED_MISSING_PUBLICATIONS_SUBCOLLECTION_ERROR = partial(
    ManifestSemanticError,
    message="ODL feed '{0}' does not contain required 'publications' subcollection",
)

ODL_FEED_CONTAINS_REDUNDANT_GROUPS_SUBCOLLECTIONS_ERROR = partial(
    ManifestSemanticError,
    message="ODL feed '{0}' contains redundant 'groups' subcollections",
)

ODL_FEED_CONTAINS_REDUNDANT_FACETS_SUBCOLLECTIONS_ERROR = partial(
    ManifestSemanticError,
    message="ODL feed '{0}' contains redundant 'facets' subcollections",
)

ODL_FEED_CONTAINS_REDUNDANT_NAVIGATION_SUBCOLLECTION_ERROR = partial(
    ManifestSemanticError,
    message="ODL feed '{0}' contains redundant 'navigation' subcollection",
)

ODL_PUBLICATION_MUST_CONTAIN_EITHER_LICENSES_OR_OA_ACQUISITION_LINK_ERROR = partial(
    ODLPublicationSemanticError,
    message="ODL publication '{0}' contains neither 'licenses' subcollection nor "
    "an Open-Access Acquisition Link (http://opds-spec.org/acquisition/open-access)",
)

ODL_LICENSE_MUST_CONTAIN_SELF_LINK_TO_LICENSE_INFO_DOCUMENT_ERROR = partial(
    ODLLicenseSemanticError,
    message="ODL license '{0}' does not contain a 'self' link to the License Info Document",
)

ODL_LICENSE_MUST_CONTAIN_CHECKOUT_LINK_TO_LICENSE_STATUS_DOCUMENT_ERROR = partial(
    ODLLicenseSemanticError,
    message="ODL license '{0}' does not contain a 'checkout' link to the License Status Document",
)


class ODLSemanticAnalyzer(SemanticAnalyzer):
    """ODL semantic analyzer."""

    @dispatch(Manifestlike)
    def visit(self, node):
        """Perform semantic analysis of the manifest node.

        :param node: Manifest-like node
        :type node: Manifestlike
        """
        super(ODLSemanticAnalyzer, self).visit(node)

        if not node.publications:
            with self._record_errors():
                raise ODL_FEED_MISSING_PUBLICATIONS_SUBCOLLECTION_ERROR(
                    node=node, node_property=ODLFeed.publications
                )

        if node.groups:
            with self._record_errors():
                raise ODL_FEED_CONTAINS_REDUNDANT_GROUPS_SUBCOLLECTIONS_ERROR(
                    node=node, node_property=ODLFeed.groups
                )

        if node.facets:
            with self._record_errors():
                raise ODL_FEED_CONTAINS_REDUNDANT_FACETS_SUBCOLLECTIONS_ERROR(
                    node=node, node_property=ODLFeed.facets
                )

        if node.navigation:
            with self._record_errors():
                raise ODL_FEED_CONTAINS_REDUNDANT_NAVIGATION_SUBCOLLECTION_ERROR(
                    node=node, node_property=ODLFeed.navigation
                )

        if node.links is not None:
            with self._record_errors():
                node.links.accept(self)
        if node.publications is not None:
            with self._record_errors():
                node.publications.accept(self)

    @dispatch(OPDS2FeedMetadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the feed's metadata.

        :param node: Feed's metadata
        :type node: OPDS2FeedMetadata
        """
        # super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(Metadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the feed's metadata.

        :param node: Feed's metadata
        :type node: Metadata
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(ODLPublication)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the OPDS 2.0 publication.

        :param node: ODL 2.0 publication
        :type node: ODLPublication
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        if (not node.licenses or len(node.licenses) == 0) and (
            (not node.licenses or len(node.links) == 0)
            or not node.links.get_by_rel(OPDS2LinkRelationsRegistry.OPEN_ACCESS.key)
        ):
            with self._record_errors():
                raise ODL_PUBLICATION_MUST_CONTAIN_EITHER_LICENSES_OR_OA_ACQUISITION_LINK_ERROR(
                    node=node, node_property=None
                )
        elif node.licenses:
            node.licenses.accept(self)

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(LinkList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of links.

        :param node: Manifest's metadata
        :type node: LinkList
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(Link)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the link node.

        :param node: Link node
        :type node: Link
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(CollectionList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of sub-collections.

        :param node: CollectionList node
        :type node: CollectionList
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(CompactCollection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the compact collection node.

        :param node: Collection node
        :type node: CompactCollection
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(Collection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the collection node.

        :param node: Collection node
        :type node: Collection
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(ODLLicense)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the ODL license node.

        :param node: ODLLicense node
        :type node: ODLLicense
        """
        self_link = (
            first_or_default(node.links.get_by_rel(OPDS2LinkRelationsRegistry.SELF.key))
            if node.links
            else None
        )

        if (
            not self_link
            or self_link.type != ODLMediaTypesRegistry.ODL_LICENSE_INFO_DOCUMENT.key
        ):
            with self._record_errors():
                raise ODL_LICENSE_MUST_CONTAIN_SELF_LINK_TO_LICENSE_INFO_DOCUMENT_ERROR(
                    node=node, node_property=None
                )

        borrow_link = (
            first_or_default(
                node.links.get_by_rel(OPDS2LinkRelationsRegistry.BORROW.key)
            )
            if node.links
            else None
        )

        if (
            not borrow_link
            or borrow_link.type != ODLMediaTypesRegistry.ODL_LICENSE_STATUS_DOCUMENT.key
        ):
            with self._record_errors():
                raise ODL_LICENSE_MUST_CONTAIN_CHECKOUT_LINK_TO_LICENSE_STATUS_DOCUMENT_ERROR(
                    node=node, node_property=None
                )

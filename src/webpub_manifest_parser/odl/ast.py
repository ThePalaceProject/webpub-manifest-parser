import datetime

from webpub_manifest_parser.core.ast import (
    ArrayOfCollectionsProperty,
    ArrayOfLinksProperty,
    Collection,
    CollectionList,
    Node,
)
from webpub_manifest_parser.core.properties import (
    ArrayOfStringsProperty,
    BooleanProperty,
    DateOrTimeProperty,
    NumberProperty,
    TypeProperty,
    URIProperty,
)
from webpub_manifest_parser.odl.registry import ODLCollectionRolesRegistry
from webpub_manifest_parser.opds2.ast import OPDS2Feed, OPDS2Price, OPDS2Publication
from webpub_manifest_parser.opds2.registry import OPDS2CollectionRolesRegistry
from webpub_manifest_parser.utils import is_string


class ODLLicenseTerms(Node):
    """ODL license terms & conditions."""

    checkouts = NumberProperty("checkouts", required=False)
    expires = DateOrTimeProperty("expires", required=False)
    concurrency = NumberProperty("concurrency", required=False)
    length = NumberProperty("length", required=False)


class ODLLicenseProtection(Node):
    """ODL license protection information."""

    formats = ArrayOfStringsProperty("format", required=False)
    devices = NumberProperty("devices", required=False)
    copy_allowed = BooleanProperty("copy", required=False)
    print_allowed = BooleanProperty("print", required=False)
    tts_allowed = BooleanProperty("tts", required=False)


class ODLLicenseMetadata(Node):
    """ODL license metadata."""

    identifier = URIProperty("identifier", required=True)
    formats = ArrayOfStringsProperty("format", required=True)
    created = DateOrTimeProperty("created", required=True)
    terms = TypeProperty(
        "terms",
        required=False,
        nested_type=ODLLicenseTerms,
    )
    protection = TypeProperty(
        "protection",
        required=False,
        nested_type=ODLLicenseProtection,
    )
    price = TypeProperty(
        "price",
        required=False,
        nested_type=OPDS2Price,
    )
    source = URIProperty("source", required=False)

    def __init__(self, identifier=None, formats=None, created=None):
        """Initialize a new instance of ODLLicenseMetadata class.

        :param identifier: License's identifier
        :type identifier: str

        :param formats: List of license formats
        :type formats: List[str]

        :param created: Time when the license was created
        :type created: datetime.datetime
        """
        super(ODLLicenseMetadata, self).__init__()

        if identifier and not is_string(identifier):
            raise ValueError("Argument 'identifier' must be a string")
        if formats and not isinstance(formats, list):
            raise ValueError("Argument 'formats' must be a list")
        if created and not isinstance(created, datetime.datetime):
            raise ValueError(
                "Argument 'created' must be an instance of {0}".format(
                    datetime.datetime
                )
            )

        self.identifier = identifier
        self.formats = formats
        self.created = created


class ODLLicense(Collection):
    """ODL license subcollection."""

    metadata = TypeProperty("metadata", required=True, nested_type=ODLLicenseMetadata)

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash((self.metadata, self.links))


class ODLPublication(OPDS2Publication):
    """ODL publication."""

    links = ArrayOfLinksProperty(key="links", required=False)
    licenses = ArrayOfCollectionsProperty(
        "licenses",
        required=False,
        role=ODLCollectionRolesRegistry.LICENSES,
        collection_type=ODLLicense,
    )

    def __init__(self, metadata=None, links=None, images=None, licenses=None):
        """Initialize a new instance of ODLPublication class.

        :param metadata: Publication's metadata
        :type metadata: webpub_manifest_parser.core.ast.Metadata

        :param links: List of publication's links
        :type links: LinkList

        :param images: List of publication's images
        :type images: LinkList

        :param licenses: List of publication's licenses
        :type licenses: LinkList
        """
        super(ODLPublication, self).__init__(metadata, links, images)

        if licenses and not isinstance(licenses, CollectionList):
            raise ValueError(
                "Argument 'licenses' must be an instance of {0}".format(CollectionList)
            )

        self.licenses = licenses

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash((super(ODLPublication, self).__hash__(), self.licenses))


class ODLFeed(OPDS2Feed):
    """ODL 2.x feed."""

    publications = ArrayOfCollectionsProperty(
        "publications",
        required=False,
        role=OPDS2CollectionRolesRegistry.PUBLICATIONS,
        collection_type=ODLPublication,
    )

from enum import Enum

from webpub_manifest_parser.core.ast import (
    ArrayOfCollectionsProperty,
    Collection,
    CollectionList,
    CompactCollection,
    CompactCollectionProperty,
    LinkList,
    LinkProperties,
    Manifestlike,
    Node,
    PresentationMetadata,
)
from webpub_manifest_parser.core.parsers import (
    AnyOfParser,
    ArrayParser,
    ObjectParser,
    StringParser,
    TypeParser,
)
from webpub_manifest_parser.core.properties import (
    ArrayProperty,
    DateOrTimeProperty,
    DateTimeProperty,
    EnumProperty,
    IntegerProperty,
    NumberProperty,
    ParsableProperty,
    StringProperty,
    TypeProperty,
    URIProperty,
)
from webpub_manifest_parser.opds2.registry import OPDS2CollectionRolesRegistry


class OPDS2Price(Node):
    """OPDS 2.0 price information."""

    value = NumberProperty("value", required=True, minimum=0)
    currency = EnumProperty(
        "currency",
        required=True,
        items=[
            "AED",
            "AFN",
            "ALL",
            "AMD",
            "ANG",
            "AOA",
            "ARS",
            "AUD",
            "AWG",
            "AZN",
            "BAM",
            "BBD",
            "BDT",
            "BGN",
            "BHD",
            "BIF",
            "BMD",
            "BND",
            "BOB",
            "BOV",
            "BRL",
            "BSD",
            "BTN",
            "BWP",
            "BYN",
            "BZD",
            "CAD",
            "CDF",
            "CHE",
            "CHF",
            "CHW",
            "CLF",
            "CLP",
            "CNY",
            "COP",
            "COU",
            "CRC",
            "CUC",
            "CUP",
            "CVE",
            "CZK",
            "DJF",
            "DKK",
            "DOP",
            "DZD",
            "EGP",
            "ERN",
            "ETB",
            "EUR",
            "FJD",
            "FKP",
            "GBP",
            "GEL",
            "GHS",
            "GIP",
            "GMD",
            "GNF",
            "GTQ",
            "GYD",
            "HKD",
            "HNL",
            "HRK",
            "HTG",
            "HUF",
            "IDR",
            "ILS",
            "INR",
            "IQD",
            "IRR",
            "ISK",
            "JMD",
            "JOD",
            "JPY",
            "KES",
            "KGS",
            "KHR",
            "KMF",
            "KPW",
            "KRW",
            "KWD",
            "KYD",
            "KZT",
            "LAK",
            "LBP",
            "LKR",
            "LRD",
            "LSL",
            "LYD",
            "MAD",
            "MDL",
            "MGA",
            "MKD",
            "MMK",
            "MNT",
            "MOP",
            "MRU",
            "MUR",
            "MVR",
            "MWK",
            "MXN",
            "MXV",
            "MYR",
            "MZN",
            "NAD",
            "NGN",
            "NIO",
            "NOK",
            "NPR",
            "NZD",
            "OMR",
            "PAB",
            "PEN",
            "PGK",
            "PHP",
            "PKR",
            "PLN",
            "PYG",
            "QAR",
            "RON",
            "RSD",
            "RUB",
            "RWF",
            "SAR",
            "SBD",
            "SCR",
            "SDG",
            "SEK",
            "SGD",
            "SHP",
            "SLL",
            "SOS",
            "SRD",
            "SSP",
            "STN",
            "SVC",
            "SYP",
            "SZL",
            "THB",
            "TJS",
            "TMT",
            "TND",
            "TOP",
            "TRY",
            "TTD",
            "TWD",
            "TZS",
            "UAH",
            "UGX",
            "USD",
            "USN",
            "UYI",
            "UYU",
            "UZS",
            "VEF",
            "VES",
            "VND",
            "VUV",
            "WST",
            "XAF",
            "XAG",
            "XAU",
            "XBA",
            "XBB",
            "XBC",
            "XBD",
            "XCD",
            "XDR",
            "XOF",
            "XPD",
            "XPF",
            "XPT",
            "XSU",
            "XTS",
            "XUA",
            "XXX",
            "YER",
            "ZAR",
            "ZMW",
            "ZWL",
        ],
    )


class OPDS2AcquisitionObject(Node):
    """OPDS 2.0 acquisition information."""

    type = StringProperty("type", required=True)
    child = ArrayProperty(
        "child",
        required=False,
        item_parser=TypeParser(
            "webpub_manifest_parser.opds2.ast.OPDS2AcquisitionObject"
        ),
    )


class OPDS2HoldsInformation(Node):
    """OPDS 2.0 holds information."""

    total = IntegerProperty("total", required=False, minimum=0)
    position = IntegerProperty("position", required=False, minimum=0)


class OPDS2CopiesInformation(Node):
    """OPDS 2.0 information about available copies."""

    total = IntegerProperty("total", required=False, minimum=0)
    available = IntegerProperty("available", required=False, minimum=0)


class OPDS2AvailabilityType(Enum):
    """Enumeration of different availability types."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RESERVED = "reserved"
    READY = "ready"


class OPDS2AvailabilityInformation(Node):
    """OPDS 2.0 availability information."""

    state = EnumProperty(
        "state",
        required=True,
        items=[
            OPDS2AvailabilityType.AVAILABLE.value,
            OPDS2AvailabilityType.UNAVAILABLE.value,
            OPDS2AvailabilityType.RESERVED.value,
            OPDS2AvailabilityType.READY.value,
        ],
    )
    since = DateOrTimeProperty("since", required=False)
    until = DateOrTimeProperty("until", required=False)


class OPDS2LinkProperties(LinkProperties):
    """OPDS 2.0 link properties."""

    number_of_items = IntegerProperty("numberOfItems", required=False, minimum=0)
    price = TypeProperty("price", required=False, nested_type=OPDS2Price)
    indirect_acquisition = ArrayProperty(
        "indirectAcquisition",
        required=False,
        item_parser=TypeParser(OPDS2AcquisitionObject),
    )
    holds = TypeProperty("holds", required=False, nested_type=OPDS2HoldsInformation)
    copies = TypeProperty("copies", required=False, nested_type=OPDS2CopiesInformation)
    availability = TypeProperty(
        "availability", required=False, nested_type=OPDS2AvailabilityInformation
    )


LinkProperties.extensions = (OPDS2LinkProperties,)


class TitleProperty(ParsableProperty):
    """Property containing arbitrary values."""

    PARSER = AnyOfParser(
        [StringParser(), ArrayParser(StringParser()), ObjectParser(StringParser())]
    )


class OPDS2FeedMetadata(Node):
    """OPDS 2.x feed metadata."""

    identifier = URIProperty("identifier", required=False)
    type = URIProperty("@type", required=False)
    title = TitleProperty("title", required=True)
    subtitle = TitleProperty("subtitle", required=False)
    modified = DateTimeProperty("modified", required=False)
    description = StringProperty("description", required=False)
    items_per_page = IntegerProperty(
        "itemsPerPage", required=False, exclusive_minimum=0
    )
    current_page = IntegerProperty("currentPage", required=False, exclusive_minimum=0)
    number_of_items = IntegerProperty("numberOfItems", required=False, minimum=0)

    def __init__(  # pylint: disable=R0913
        self,
        title=None,
        _type=None,
        subtitle=None,
        modified=None,
        description=None,
        items_per_page=None,
        current_page=None,
        number_of_items=None,
    ):
        """Initialize a new instance of OPDS2FeedMetadata class."""
        super(OPDS2FeedMetadata, self).__init__()

        self.title = title
        self.type = _type
        self.subtitle = subtitle
        self.modified = modified
        self.description = description
        self.items_per_page = items_per_page
        self.current_page = current_page
        self.number_of_items = number_of_items


class OPDS2Publication(Collection):
    """OPDS 2.0 publication."""

    images = CompactCollectionProperty(
        "images", required=True, role=OPDS2CollectionRolesRegistry.IMAGES
    )

    def __init__(self, metadata=None, links=None, images=None):
        """Initialize a new instance of OPDS2Publication class."""
        super(OPDS2Publication, self).__init__()

        if metadata and not isinstance(metadata, PresentationMetadata):
            raise ValueError(
                "Argument 'metadata' must be an instance of {0}".format(
                    PresentationMetadata
                )
            )
        if links and not isinstance(links, LinkList):
            raise ValueError(
                "Argument 'links' must be an instance of {0}".format(LinkList)
            )
        if images and not isinstance(images, LinkList):
            raise ValueError(
                "Argument 'images' must be an instance of {0}".format(LinkList)
            )

        self.metadata = metadata
        self.links = links
        self.images = images

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash((super(OPDS2Publication, self).__hash__(), self.images))


class OPDS2Facet(Collection):
    """OPDS 2.0 facet."""

    metadata = TypeProperty("metadata", required=False, nested_type=OPDS2FeedMetadata)


class OPDS2Navigation(CompactCollection):
    """OPDS 2 navigation for the catalog using links."""


class OPDS2Group(Collection):
    """OPDS 2.0 group."""

    metadata = TypeProperty("metadata", required=False, nested_type=OPDS2FeedMetadata)
    publications = ArrayOfCollectionsProperty(
        "publications",
        required=False,
        role=OPDS2CollectionRolesRegistry.PUBLICATIONS,
        collection_type=OPDS2Publication,
    )
    navigation = CompactCollectionProperty(
        "navigation",
        required=False,
        role=OPDS2CollectionRolesRegistry.NAVIGATION,
        collection_class=OPDS2Navigation,
    )

    def __init__(self, metadata=None, publications=None, navigation=None):
        """Initialize a new instance of OPDS2Group class."""
        super(OPDS2Group, self).__init__()

        if metadata and not isinstance(metadata, OPDS2FeedMetadata):
            raise ValueError(
                "Argument 'metadata' must be an instance of {0}".format(
                    OPDS2FeedMetadata
                )
            )
        if publications and not isinstance(publications, CollectionList):
            raise ValueError(
                "Argument 'publications' must be an instance of {0}".format(
                    CollectionList
                )
            )
        if navigation and not isinstance(navigation, OPDS2Navigation):
            raise ValueError(
                "Argument 'navigation' must be an instance of {0}".format(
                    OPDS2Navigation
                )
            )

        self.metadata = metadata
        self.publications = publications
        self.navigation = navigation


class OPDS2Feed(Manifestlike):
    """OPDS 2.x feed."""

    metadata = TypeProperty("metadata", required=True, nested_type=OPDS2FeedMetadata)
    publications = ArrayOfCollectionsProperty(
        "publications",
        required=False,
        role=OPDS2CollectionRolesRegistry.PUBLICATIONS,
        collection_type=OPDS2Publication,
    )
    navigation = CompactCollectionProperty(
        "navigation",
        required=False,
        role=OPDS2CollectionRolesRegistry.NAVIGATION,
        collection_class=OPDS2Navigation,
    )
    facets = ArrayOfCollectionsProperty(
        "facets",
        required=False,
        role=OPDS2CollectionRolesRegistry.FACETS,
        collection_type=OPDS2Facet,
    )
    groups = ArrayOfCollectionsProperty(
        "groups",
        required=False,
        role=OPDS2CollectionRolesRegistry.GROUPS,
        collection_type=OPDS2Group,
    )

    def __init__(  # pylint: disable=R0913
        self,
        metadata=None,
        links=None,
        publications=None,
        navigation=None,
        facets=None,
        groups=None,
    ):
        """Initialize a new instance of OPDS2Feed class."""
        super(OPDS2Feed, self).__init__()

        if metadata and not isinstance(metadata, OPDS2FeedMetadata):
            raise ValueError(
                "Argument 'metadata' must be an instance of {0}".format(
                    OPDS2FeedMetadata
                )
            )
        if links and not isinstance(links, LinkList):
            raise ValueError(
                "Argument 'links' must be an instance of {0}".format(LinkList)
            )
        if publications and not isinstance(publications, CollectionList):
            raise ValueError(
                "Argument 'publications' must be an instance of {0}".format(
                    CollectionList
                )
            )
        if navigation and not isinstance(navigation, OPDS2Navigation):
            raise ValueError(
                "Argument 'navigation' must be an instance of {0}".format(
                    OPDS2Navigation
                )
            )
        if facets and not isinstance(facets, CollectionList):
            raise ValueError(
                "Argument 'facets' must be an instance of {0}".format(CollectionList)
            )
        if groups and not isinstance(groups, CollectionList):
            raise ValueError(
                "Argument 'groups' must be an instance of {0}".format(CollectionList)
            )

        self.metadata = metadata
        self.links = links
        self.publications = publications
        self.navigation = navigation
        self.facets = facets
        self.groups = groups

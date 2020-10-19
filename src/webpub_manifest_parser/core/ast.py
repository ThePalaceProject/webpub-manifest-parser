from abc import ABCMeta, abstractmethod

import six

from webpub_manifest_parser.core.parsers import (
    AnyOfParser,
    ArrayParser,
    StringParser,
    TypeParser,
)
from webpub_manifest_parser.core.properties import (
    ArrayOfStringsProperty,
    ArrayProperty,
    BooleanProperty,
    DateOrTimeProperty,
    DateTimeProperty,
    EnumProperty,
    IntegerProperty,
    LanguageProperty,
    ListProperty,
    LocalizableStringProperty,
    NumberProperty,
    ParsableProperty,
    PropertiesGrouping,
    Property,
    StringProperty,
    TypeProperty,
    URIProperty,
    URITemplateProperty,
)
from webpub_manifest_parser.core.registry import CollectionRole
from webpub_manifest_parser.utils import encode


@six.add_metaclass(ABCMeta)
class Visitor(object):
    """Interface for visitors walking through abstract syntax trees (AST)."""

    @abstractmethod
    def visit(self, node):
        """Process the specified node.

        :param node: AST node
        :type node: Node
        """
        raise NotImplementedError()


@six.add_metaclass(ABCMeta)
class Visitable(object):
    """Interface for objects walkable by AST visitors."""

    @abstractmethod
    def accept(self, visitor):
        """Accept  the specified visitor.

        :param visitor: Visitor object
        :type visitor: Visitor
        """
        raise NotImplementedError()


@six.add_metaclass(ABCMeta)
class Extendable(object):
    """Abstract class adding ability to extend classes.

    For example, RWPM link properties can be extended by EPUB link properties and OPDS 2.0 link properties.
    """

    extensions = None

    @classmethod
    def get_extension(cls):
        """Return a new class having all extensions as mixins.

        :return: New class containing extensions as mixins.
        :rtype: Type
        """
        if not cls.extensions:
            return cls

        if len(cls.extensions) == 1:
            return cls.extensions[0]

        class_names = [cls.__name__] + [
            extension.__name__ for extension in cls.extensions
        ]
        extended_class_name = "_".join(class_names)
        extended_class = type(extended_class_name, tuple(cls.extensions), {})

        return extended_class


class Node(PropertiesGrouping, Visitable, Extendable):
    """Base class for all AST nodes."""

    def accept(self, visitor):
        """Accept the specified visitor.

        :param visitor: Visitor object
        :type visitor: Visitor
        """
        visitor.visit(self)


class LinkProperties(Node):
    """Link properties."""

    clipped = BooleanProperty("clipped", required=False)
    fit = EnumProperty(
        "fit", required=False, items=["contain", "cover", "width", "height"]
    )
    orientation = EnumProperty(
        "orientation", required=False, items=["auto", "landscape", "portrait"]
    )
    page = EnumProperty("page", required=False, items=["left", "right", "center"])
    spread = EnumProperty(
        "spread", required=False, items=["auto", "both", "none", "landscape"]
    )

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash((self.clipped, self.orientation, self.page, self.spread))

    def __repr__(self):
        """Return a string representation of the object.

        :return: String representation
        :rtype: str
        """
        return u"<LinkProperties(clipped={0}, fit={1}, orientation={2}, page={3}, spread={4})>".format(
            self.clipped, self.fit, self.orientation, self.page, self.spread
        )


class Link(Node):
    """Link to another resource."""

    href = URITemplateProperty("href", required=True)
    templated = BooleanProperty("templated", required=False)
    type = StringProperty("type", required=False)
    title = StringProperty("title", required=False)
    rel = ArrayOfStringsProperty("rel", required=False)
    properties = TypeProperty("properties", required=False, nested_type=LinkProperties)
    height = IntegerProperty("height", required=False, exclusive_minimum=0)
    width = IntegerProperty("width", required=False, exclusive_minimum=0)
    bitrate = NumberProperty("bitrate", required=False, exclusive_minimum=0)
    duration = NumberProperty("duration", required=False, exclusive_minimum=0)
    language = LanguageProperty("language", required=False)
    alternate = ArrayProperty(
        "alternate",
        required=False,
        item_parser=TypeParser("webpub_manifest_parser.core.ast.Link"),
    )
    children = ArrayProperty(
        "children",
        required=False,
        item_parser=TypeParser("webpub_manifest_parser.core.ast.Link"),
    )

    def __init__(  # pylint: disable=R0913
        self,
        href=None,
        templated=None,
        _type=None,
        title=None,
        rel=None,
        properties=None,
        height=None,
        width=None,
        duration=None,
        bitrate=None,
        language=None,
        alternate=None,
        children=None,
    ):
        """Initialize a new instance of Link class.

        :param href: Link's URL
        :type href: str

        :param templated: Boolean value indicating whether href is a URI template
        :type templated: bool

        :param _type: Media type of the linked resource
        :type _type: Union[str, MediaType]

        :param title: Title of the linked resource
        :type title: str

        :param rel: Relation between the resource and its containing collection
        :type rel: List[registry.LinkRelation]

        :param properties: Relation between the resource and its containing collection
        :type properties: object

        :param height: Height of the linked resource in pixels
        :type height: int

        :param width: Width of the linked resource in pixels
        :type width: int

        :param duration: Duration of the linked resource in seconds
        :type duration: float

        :param bitrate: Bit rate of the linked resource in kilobits per second
        :type bitrate: float

        :param language: Expected language of the linked resource
        :type language: List[str]

        :param alternate: Alternate resources for the linked resource
        :type alternate: List[Link]

        :param children: Resources that are children of the linked resource, in the context of a given collection role
        :type children: List[Link]
        """
        super(Link, self).__init__()

        self.href = href
        self.templated = templated
        self.type = _type
        self.title = title
        self.rel = rel
        self.properties = properties
        self.height = height
        self.width = width
        self.duration = duration
        self.bitrate = bitrate
        self.language = language
        self.alternate = alternate
        self.children = children

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash(
            (
                self.href,
                self.templated,
                self.type,
                self.title,
                frozenset(self.rel),
                self.properties,
                self.height,
                self.width,
                self.duration,
                self.bitrate,
                frozenset(self.language)
                if isinstance(self.language, list)
                else self.language,
                frozenset(self.alternate),
                frozenset(self.children),
            )
        )

    def __repr__(self):
        """Return a string representation of the object.

        :return: String representation
        :rtype: str
        """
        return (
            u"<Link("
            u"href={0}, "
            u"templated={1}, "
            u"type={2}, "
            u"title={3}, "
            u"rel={4}, "
            u"properties={5}, "
            u"height={6}, "
            u"width={7}, "
            u"duration={8}, "
            u"bitrate={9}, "
            u"language={10}, "
            u"alternate={11}, "
            u"children={12}".format(
                self.href,
                self.templated,
                self.type,
                self.title,
                self.rel,
                self.properties,
                self.height,
                self.width,
                self.duration,
                self.bitrate,
                self.language,
                self.alternate,
                self.children,
            )
        )


class LinkList(Node, list):
    """List of links."""

    def __init__(self, items=None):
        """Initialize a new instance of LinksList class.

        :param items: (Optional) Items to be added to the list
        :type items: Optional[List]
        """
        super(LinkList, self).__init__()

        if items is not None:
            if not isinstance(items, list):
                raise ValueError("Items argument must be a list")

            self.extend(items)

    def get_by_rel(self, rel):
        """Return links with the specific relation.

        :param rel: Link's relation
        :type rel: str

        :return: Links with the specified relation
        :rtype: List[Link]
        """
        return [link for link in self if rel in link.rel]

    def get_by_href(self, href):
        """Return links with the specific URL.

        :param href: Link's URL
        :type href: str

        :return: Links with the specified relation
        :rtype: List[Link]
        """
        return [link for link in self if href == link.href]


class ArrayOfLinksProperty(ListProperty):
    """Property allowing to contain only unique links."""

    def __init__(self, key, required):
        """Initialize a new instance of ArrayOfLinksProperty class.

        :param key: Property's key
        :type key: str

        :param required: Boolean value indicating whether the property is required or not
        :type required: bool
        """
        super(ArrayOfLinksProperty, self).__init__(
            key, required, ArrayParser(TypeParser(Link), True), LinkList
        )


class Contributor(Node):
    """Contributor object."""

    name = LocalizableStringProperty("name", required=True)
    identifier = URIProperty("identifier", required=False)
    sort_as = StringProperty("sortAs", required=False)
    role = ArrayOfStringsProperty("role", required=False)
    position = NumberProperty("position", required=False)
    links = ArrayOfLinksProperty("links", required=False)

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash(
            (
                self.name,
                self.identifier,
                self.sort_as,
                frozenset(self.role),
                self.position,
                frozenset(self.links),
            )
        )

    def __repr__(self):
        """Return a string representation of the object.

        :return: String representation
        :rtype: str
        """
        return u"<Contributor(name={0}, identifier={1}, sort_as={2}, role={3}, position={4}, links={5})>".format(
            encode(self.name),
            self.identifier,
            self.sort_as,
            self.role,
            self.position,
            self.links,
        )


class ContributorProperty(ParsableProperty):
    """Property containing information about a contributor."""

    PARSER = AnyOfParser(
        [
            StringParser(),
            ArrayParser(AnyOfParser([StringParser(), TypeParser(Contributor)])),
            TypeParser(Contributor),
        ]
    )


class Subject(Node, PropertiesGrouping):
    """Subject object."""

    name = LocalizableStringProperty("name", required=True)
    sort_as = StringProperty("sortAs", required=False)
    code = StringProperty("code", required=False)
    scheme = URIProperty("scheme", required=False)
    links = ArrayOfLinksProperty("links", required=False)

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash(
            (self.name, self.sort_as, self.code, self.scheme, frozenset(self.links))
        )

    def __repr__(self):
        """Return a string representation of the object.

        :return: String representation
        :rtype: str
        """
        return (
            u"<Subject(name={0}, sort_as={1}, code={2}, scheme={3}, links={4})>".format(
                self.name, self.sort_as, self.code, self.scheme, self.links
            )
        )


class SubjectProperty(ParsableProperty):
    """Property containing information about a subject."""

    PARSER = AnyOfParser(
        [
            StringParser(),
            ArrayParser(AnyOfParser([StringParser(), TypeParser(Subject)])),
            TypeParser(Subject),
        ]
    )


class Owner(Node, PropertiesGrouping):
    """Object containing information about the collection's owners."""

    collection = TypeProperty("collection", required=False, nested_type=Contributor)
    series = TypeProperty("series", required=False, nested_type=Contributor)

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash((self.collection, self.series))

    def __repr__(self):
        """Return a string representation of the object.

        :return: String representation
        :rtype: str
        """
        return u"<Owner(collection={0}, series={1})>".format(
            self.collection, self.series
        )


class Metadata(Node):
    """Dictionary containing manifest's metadata."""

    identifier = URIProperty("identifier", required=False)
    type = URIProperty("@type", required=False)
    title = LocalizableStringProperty("title", required=True)
    subtitle = LocalizableStringProperty("subtitle", required=False)
    modified = DateTimeProperty("modified", required=False)
    published = DateOrTimeProperty("published", required=False)
    language = LanguageProperty("language", required=False)
    sort_as = StringProperty("sortAs", required=False)
    author = ContributorProperty("author", required=False)
    translator = ContributorProperty("translator", required=False)
    editor = ContributorProperty("editor", required=False)
    artist = ContributorProperty("artist", required=False)
    illustrator = ContributorProperty("illustrator", required=False)
    letterer = ContributorProperty("letterer", required=False)
    penciler = ContributorProperty("penciler", required=False)
    colorist = ContributorProperty("colorist", required=False)
    inker = ContributorProperty("inker", required=False)
    narrator = ContributorProperty("narrator", required=False)
    contributor = ContributorProperty("contributor", required=False)
    publisher = ContributorProperty("publisher", required=False)
    imprint = ContributorProperty("imprint", required=False)
    subject = SubjectProperty("subject", required=False)
    reading_progression = EnumProperty(
        "readingProgression",
        required=False,
        items=["rtl", "ltr", "ttb", "btt", "auto"],
        default_value="auto",
    )
    description = StringProperty("description", required=False)
    duration = NumberProperty("duration", required=False, exclusive_minimum=0)
    number_of_pages = NumberProperty(
        "numberOfPages", required=False, exclusive_minimum=0
    )
    belongs_to = TypeProperty("belongsTo", required=False, nested_type=Owner)

    def __init__(  # pylint: disable=R0913, R0914
        self,
        title=None,
        identifier=None,
        subtitle=None,
        modified=None,
        published=None,
        language=None,
        sort_as=None,
        author=None,
        translator=None,
        editor=None,
        artist=None,
        illustrator=None,
        letterer=None,
        penciler=None,
        colorist=None,
        inker=None,
        narrator=None,
        contributor=None,
        publisher=None,
        imprint=None,
        subject=None,
        description=None,
        duration=None,
        number_of_pages=None,
        belongs_to=None,
    ):
        """Initialize a new instance of Metadata class."""
        super(Metadata, self).__init__()
        self.title = title
        self.identifier = identifier
        self.title = title
        self.subtitle = subtitle
        self.modified = modified
        self.published = published
        self.language = language
        self.sort_as = sort_as
        self.author = author
        self.translator = translator
        self.editor = editor
        self.artist = artist
        self.illustrator = illustrator
        self.letterer = letterer
        self.penciler = penciler
        self.colorist = colorist
        self.inker = inker
        self.narrator = narrator
        self.contributor = contributor
        self.publisher = publisher
        self.imprint = imprint
        self.subject = subject
        self.description = description
        self.duration = duration
        self.number_of_pages = number_of_pages
        self.belongs_to = belongs_to

    def __hash__(self):
        """Calculate the hash.

        :return: Hash
        :rtype: int
        """
        return hash(
            (
                self.identifier,
                self.type,
                self.title,
                self.subtitle,
                self.modified,
                self.published,
                self.language,
                self.sort_as,
                self.author,
                self.translator,
                self.editor,
                self.artist,
                self.illustrator,
                self.letterer,
                self.penciler,
                self.colorist,
                self.inker,
                self.narrator,
                self.contributor,
                self.publisher,
                self.imprint,
                self.subject,
                self.description,
                self.duration,
                self.number_of_pages,
                self.belongs_to,
            )
        )


class PresentationMetadata(Metadata):
    """RWPM extension containing presentation metadata."""

    clipped = BooleanProperty("clipped", False)
    continuous = BooleanProperty("continuous", False)
    fit = EnumProperty("fit", False, ["width", "height", "contain", "cover"])
    orientation = EnumProperty("orientation", False, ["auto", "landscape", "portrait"])
    overflow = EnumProperty(
        "overflow", False, ["auto", "paginated", "scrolled", "scrolled-continuous"]
    )
    spread = EnumProperty("spread", False, ["auto", "both", "none", "landscape"])


class CompactCollection(Node):
    """A compact collection is defined as a grouping of links."""

    links = ArrayOfLinksProperty(key="links", required=True)

    def __init__(self, role=None, links=None):
        """Initialize a new instance of Collection class.

        :param role: Collection's role (can be empty when self is a manifest)
        :type role: Optional[CollectionRole]

        :param links: Collection's links
        :type links: Optional[LinksList]
        """
        super(CompactCollection, self).__init__()

        self._role = role
        self.links = links

    @property
    def role(self):
        """Return the collection's role.

        :return: Collection's role.
        :rtype: Optional[CollectionRole]
        """
        return self._role


class Collection(CompactCollection):
    """A collection is defined as a grouping of metadata, links and sub-collections."""

    def __init__(self, role=None, links=None, metadata=None):
        """Initialize a new instance of Collection class.

        :param role: Collection's role (can be empty when self is a manifest)
        :type role: Optional[CollectionRole]

        :param links: Collection's links
        :type links: Optional[LinksList]

        :param metadata: Collection's metadata
        :type metadata: Optional[Metadata]
        """
        super(Collection, self).__init__(role, links)

        self._role = role
        self._sub_collections = CollectionList()
        self.metadata = metadata

    metadata = TypeProperty(
        key="metadata", required=True, nested_type=PresentationMetadata
    )

    @property
    def sub_collections(self):
        """Return a list of sub-collections.

        :return: List of sub-collections.
        :rtype: CollectionList
        """
        return self._sub_collections

    @property
    def compact(self):
        """Return a boolean value indicating if this collection is compact.

        :return: Boolean value indicating if this collection is compact
        :rtype: bool
        """
        return self.metadata is None and len(self._sub_collections) == 0

    @property
    def full(self):
        """Return a boolean value indicating if this collection is full.

        :return: Boolean value indicating if this collection is full
        :rtype: bool
        """
        return self.metadata is not None and len(self._sub_collections) > 0


class CollectionList(Node, list):
    """List of sub-collections."""

    def __init__(self, items=None):
        """Initialize a new instance of CollectionList class.

        :param items: (Optional) Items to be added to the list
        :type items: Optional[List]
        """
        super(CollectionList, self).__init__()

        if items is not None:
            if not isinstance(items, list):
                raise ValueError("Items argument must be a list")

            self.extend(items)

    def get_by_role(self, role):
        """Return collections with the specific role.

        :param role: Collection's role
        :type role: str

        :return: Collections with the specific role
        :rtype: List[Collection]
        """
        return [collection for collection in self if collection.role.key == role]


class CompactCollectionProperty(Property):
    """Property allowing to contain a compact sub-collection."""

    def __init__(self, key, required, role, collection_class=CompactCollection):
        """Initialize a new instance of CompactCollectionProperty class.

        :param key: Property's key
        :type key: str

        :param required: Boolean value indicating whether the property is required or not
        :type required: bool

        :param role: Collection role
        :type role: CollectionRole
        """
        if not isinstance(role, CollectionRole):
            raise ValueError(
                "Role argument must be an instance of CollectionRole class"
            )
        if not issubclass(collection_class, CompactCollection):
            raise ValueError(
                "Collection class argument must be a subclass of CompactCollection class"
            )

        super(CompactCollectionProperty, self).__init__(
            key, required, TypeParser(collection_class)
        )

        self._role = role

    @property
    def role(self):
        """Return the sub-collection's role.

        :return: Sub-collection's role
        :rtype: CollectionRole
        """
        return self._role


class ArrayOfCollectionsProperty(ListProperty):
    """Property allowing to contain a compact sub-collection."""

    def __init__(self, key, required, role, collection_type=Collection):
        """Initialize a new instance of ArrayOfCollectionsProperty class.

        :param key: Property's key
        :type key: str

        :param required: Boolean value indicating whether the property is required or not
        :type required: bool

        :param role: Collection role
        :type role: CollectionRole
        """
        if not isinstance(role, CollectionRole):
            raise ValueError(
                "Role argument must be an instance of CollectionRole class"
            )
        if not issubclass(collection_type, Collection):
            raise ValueError(
                "Collection type argument must be a subclass of Collection class"
            )

        super(ArrayOfCollectionsProperty, self).__init__(
            key,
            required,
            ArrayParser(TypeParser(collection_type), True),
            CollectionList,
        )

        self._role = role

    @property
    def role(self):
        """Return the sub-collection's role.

        :return: Sub-collection's role
        :rtype: CollectionRole
        """
        return self._role


class Manifestlike(Collection):
    """Base class for Manifest (Readium Web Publication Manifest) and Feed (OPDS 2).

    An OPDS 2 feed is defined as a RWPM with enumerated exceptions.

    This class implements the behavior common to both specs.  The
    alternative is to have the Feed class subclass Manifest and then
    implement a lot of exceptions.
    """

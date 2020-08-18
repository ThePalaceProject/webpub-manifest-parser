class Role(object):

    def __init__(self, name, compact=True, type_required=False):
        """Constructor.
        """
        self.name = name
        self.compact = compact
        self.type_required = type_required

    def validation_errors(self, manifest, collection):
        """Enforce validation rules on a subcollection presumed to have this
        role.
        
        :param manifest: A Manifestlike
        :param collection: A Collection
        :return: A 2-typle ([validation errors], [warnings])
        """
        errors = []
        if self.compact and not collection.is_compact_collection:
            errors.append(
                "Collection with role %s must be compact." % self.name
            )

        if self.type_required:
            # "All resources listed in readingOrder and resources must
            # indicate their media type using type."
            # - https://github.com/readium/webpub-manifest#21-sub-collections
            for link in collection.links:
                if not link.type:
                    errors.append(
                        'Link to "%s" is missing required type' % link.href
                    )
        return errors, []

# Create Role objects for each role mentioned in the RWPM Collection
# Roles Registry:
# https://github.com/readium/webpub-manifest/blob/master/roles.md

# RWPM Core
Role.readingOrder = Role("readingOrder", compact=True, type_required=True)
Role.resources = Role("resources", compact=True, type_required=True)
Role.toc = Role("toc", compact=True)

# RWPM Extensions
for role in ("guided", "landmarks", "loa", "loi", "lot", "lov", "pageList"):
    setattr(Role, role, Role(role))

# OPDS 2.0
for role in ("navigation", "images"):
    setattr(Role, role, Role(role))

for role in ("publications", "facets", "groups"):
    setattr(Role, role, Role(role, compact=False))

# End Role code.
    
class MediaTypes(object):
    """Constants for media types mentioned in the RWPM or OPDS 2.0 specs."""
    
    # https://github.com/readium/webpub-manifest#4-media-type
    MANIFEST = "application/webpub+json"
   
    # https://github.com/readium/webpub-manifest#7-cover
    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    WEBP = "image/webp"
    SVG = "image/svg"

    # https://drafts.opds.io/opds-2.0.html#overview
    OPDS_FEED = "application/opds+json"

    # https://drafts.opds.io/opds-2.0.html#41-opds-publication
    OPDS_PUBLICATION = "application/opds-publication+json"

    # https://github.com/readium/webpub-manifest#9-package
    WEB_PUBLICATION_PACKAGE = "application/webpub+zip"


class LinkRelations(object):
    """Constants for link relations mentioned in the RWPM Link Relations
    Registry.
    
    https://github.com/readium/webpub-manifest/blob/master/relationships.md
    """

    ALTERNATE = "alternate"
    CONTENTS = "contents"
    COVER = "cover"
    MANIFEST = "manifest"
    SEARCH = "search"
    SELF = "self"

    ACQUISITION = "http://opds-spec.org/acquisition"
    OPEN_ACCESS = "http://opds-spec.org/acquisition/open-access"
    BORROW = "http://opds-spec.org/acquisition/borrow"
    BUY = "http://opds-spec.org/acquisition/buy"
    SAMPLE = "http://opds-spec.org/acquisition/sample"
    PREVIEW = "preview"
    SUBSCRIBE = "http://opds-spec.org/acquisition/subscribe"

    
class JSONable(object):

    """An object whose Unicode representation is a JSON dump
    of a dictionary.
    """

    def __unicode__(self):
        return json.dumps(self.as_dict)

    # For Python 2 compatibility
    __str__ = __unicode__
    
    @property
    def as_dict(self):
        raise NotImplementedError()

    @classmethod
    def json_ready(cls, value):
        if isinstance(value, JSONable):
            return value.as_dict
        elif isinstance(value, list):
            return [cls.json_ready(x) for x in value]
        else:
            return value


class Collection(JSONable):
    """

    "A collection is defined as a grouping of metadata, links and
    sub-collections." - RWPM

    """

    REQUIRED_SUBCOLLECTIONS = []
    
    def __init__(self, metadata=None, links=None,
                 subcollections=None, role=None, **extra):
        """Constructor.

        :param metadata: A Metadata object.
        :param links: A list of Link objects.
        :param subcollections: A list of Collection objects.
        :param role: The role of this Collection with respect to its parent,
           if any. Either a Role object or a string.
        :param extra: Any extra information that should be preserved
           as-is in the JSON representation of this collection.
        """

        if metadata is None:
            metadata = Metadata()
        if links is None:
            links = []
        if subcollections is None:
            subcollections = dict()
        self.metadata = metadata
        self.links = links
        self.subcollections = {}
        for s in subcollections:
            self.add_subcollection(s)
        if not isinstance(role, Role):
            role = Role(role, compact=False)
        self.role = role
        self.extra = extra
        
    def add_subcollection(self, subcollection):
        """Add a subcollection."""
        if not subcollection.role:
            raise ValueError("Subcollection must have a role.")
        self.subcollections[subcollection.role] = subcollection

    @classmethod
    def from_json(cls, data, role=None):
        if not isinstance(data, dict):
            data = json.loads(data)
        if not isinstance(data, dict):
            raise ValueError("Input must be a JSON object.")

        metadata = Metadata(data.get('metadata', {}))

        links = data.get('links', [])
        links = [Link(**link_data) for link_data in links]

        # Everything other than metadata and links is either a
        # subcollection, or extra information that should be left
        # alone.
        subcollections = []
        extra = {}
        for role, collection_data in data.items():
            if role in ('metadata', 'links'):
                continue
            if isinstance(collection_data, dict):
                collection = cls.from_json(collection_data, role=Role(role))
                subcollections.append(collection)
            else:
                extra[role] = collection_data

        return cls(
            metadata=metadata, links=links, subcollections=subcollections,
            role=role, extra=extra
        )
            
    # These properties test the terminology defined in 
    # https://github.com/readium/webpub-manifest#12-terminology
    @property
    def is_full_collection(self):
        """Is this a full collection?

        "A collection that contains at least two or more data items
        among metadata, links and sub-collections."
        """
        count = 0
        if len(self.metadata):
            count +=1
        if len(self.links) > 0:
            count += 1
        if len(self.subcollections) > 0:
            count += 1
        return count >= 2
        
    @property
    def is_compact_collection(self):
        """Is this a compact collection?

        "A collection that contains one or more links, but doesn't
        contain any metadata or sub-collections."
        """
        return (
            len(self.links) >= 1 and not self.keys()
            and not self.subcollections
        )

    @property
    def is_manifest(self):
        """Is this a manifest?

        "A manifest is a full collection that represents structured
        information about a publication."
        """
        # See the Manifest class.
        return False

    # End properties for checking terminology.

    def by_role(self, role):
        """Find the subcollection, if any, with the given role.

        :param role: A Role or string.
        :return: A Collection, or None if there is no subcollection
           with this role.
        """
        if isinstance(role, Role):
            role = role.name
        return self.subcollections.get(role)
    
    def validation_errors(self, manifest):
        """Validate this Collection and everything inside.

        :param manifest: A Manifestlike object setting ground rules for
            validation.
        :return: A 2-typle ([validation errors], [warnings])
        """
        errors = []
        warnings = []
        
        # Subcollections with different roles are subject to different
        # validation rules.
        if self.role:
            errors.extend(self.role.validation_errors(manifest, self))
            
        for required_role in self.REQUIRED_SUBCOLLECTIONS:
            if not self.by_role(required_role):
                errors.append(
                    "No subcollection with required role %s" % self.role.namef
                )

        # Validate the components of this collection: its
        # sub-Collections (recursively), each of its Links, and its
        # Metadata.
        for needs_validation in (
            self.subcollections.values(),
            self.links,
            [self.metadata]
        ):
            for item in needs_validation:
                new_errors, new_warnings = item.validation_errors(self)
                errors.extend(new_errors)
                warnings.extend(new_warnings)
        return errors, warnings
    
    @property
    def as_dict(self):
        """Convert this collection and its contents to a Python dictionary.

        :return: a dict
        """
        d = dict(
            metadata=self.metadata.as_dict
            links=[x.as_dict for x in self.links]
        )
        for collection in subcollections:
            d[collection.role] = collection.as_dict
        d.update(self.extra)
        return d


class Metadata(dict, JSONable):
    """Metadata associated with a Collection.

    :TODO: Currently any special JSON-LD features will be ignored; data is
    added to the dictionary without any normalization.
    """

    def validation_errors(self, manifest):
        """Validate the metadata.

        :param manifest: A Manifestlike object setting ground rules for
            validation.
        :return: A 2-typle ([validation errors], [warnings])
        """
        errors = []
        warnings = []
        
        for field in manifest.required_fields:
            if field not in self:
                errors.append(
                    "Required metadata '{}' is missing.".format(field)
                )

        for field in manifestlike.recommended_fields:
            if field not in self:
                warnings.append(
                    "Recommended metadata '{}' is missing.".format(field)
                )

        return errors, warnings
    
    @property
    def as_dict(self):
        return self


class Link(JSONable):
    """A link to another resource."""
    def __init__(
            self, href, templated=False, type=None, title=None, rel=None,
            properties=None, height=None, width=None, duration=None,
            bitrate=None, language=None, alternate=None, children=None,
            **kwargs
    ):
        """Constructor.

        :param href: URI or URI template of the linked resource
        :param templated: Indicates that `href` is a URI template
        :param type: Media type of the linked resource
        :param title: Title of the linked resource
        :param rel: Relation between the resource and its containing collection
        :param properties: Properties associated to the linked resource
        :param height: Height of the linked resource in pixels
        :param width: Width of the linked resource in pixels
        :param duration: Duration of the linked resource in seconds
        :param bitrate: Bit rate of the linked resource in kilobits per second
        :param language: Expected language of the linked resource
        :param alternate: Alternate resources for the linked resource
        :param children: One or more Link objects representing resources that are children of the linked resource, in the context of a given collection role.
        :param kwargs: Any properties introduced by extensions. These will
            be presented as-is.

        """
        self.href = href
        self.templated = templated
        self.type = type
        self.rel = rel
        self.properties = properties
        self.height = height
        self.width = width
        self.duration = duration
        self.bitrate = bitrate
        self.language = self._guarantee_list(language)
        self.alternate = self._guarantee_list(alternate)
        self.children = self._guarantee_list(children)
        self._extra = kwargs
        
    def _guarantee_list(self, x):
        """If `x` is not a list, return a one-item list containing it."""
        if not isinstance(x, list):
            return [x]
        return x

    def validation_errors(self, manifest):
        """Validate the data in this Link object.

        :param manifest: A Manifestlike object setting ground rules for
            validation.
        :return: A 2-typle ([validation errors], [warnings])
        """
        errors = []

        # https://github.com/readium/webpub-manifest#24-the-link-object
        if not self.href:
            errors.append(
                'Link missing required field "href": %r' % self.as_dict
            )
        return errors
        
    @property
    def as_dict(self):
        d = dict(
            href=self.href,
            rel=self.rel,
            properties=self.properties
            height=self.height,
            width=self.width,
            duration=self.duration,
            bitrate=self.bitrate,
            language=self._guarantee_list(self.language)
            alternate=[
                x.as_dict for x in self._guarantee_list(self.alternate)
            ]
            children=self._format_list(self.children),
        )
        d.update(self._extra)

        if self.templated:
            d['templated'] = self.templated
        
        # Compress the dictionary by deleting keys with no value.
        for k, v in list(dict.items()):
            if v in (None, []):
                del d[k]
        return d


class Manifestlike(Collection):
    """Base class for Manifest (Readium Web Publication Manifest)
    and Feed (OPDS 2)

    An OPDS 2 feed is defined as a RWPM with enumerated exceptions.

    This class implements the behavior common to both specs.  The
    alternative is to have the Feed class subclass Manifest and then
    implement a lot of exceptions.
    """

    # All subclasses of this class MUST set a value for this constant.
    DEFAULT_CONTEXT = None

    # These are optional.
    REQUIRED_METADATA_FIELDS = []
    RECOMMENDED_METADATA_FIELDS = []
    
    def __init__(self, *args, **kwargs)):
        self.context = kwargs.pop('context', self.DEFAULT_CONTEXT)
        super(Manifestlike, self).__init__(*args, **kwargs)
        
    @property
    def as_dict(self):
        d = super(Manifestlike, self).as_dict
        d['@context'] = self.context
        return d

    def validation_errors(self):
        errors, warnings = super(Manifestlike, self).validation_errors(self)
        for relation in self.REQUIRED_LINKS:
            if not self.for_rel(relation):
                errors.append(
                    'Required link with rel="{}" is missing.'.format(relation)
                )
        for role in self.REQUIRED_ROLES:
            if not self.by_role(role):
                errors.append(
                    "Required subcollection '{}' is missing.".format(
                        role.name
                    )
                )
        return errors, warnings

    
class Manifest(Manifestlike):
    """A Readium Web Publication Manifest."""

    # https://github.com/readium/webpub-manifest#22-metadata
    DEFAULT_CONTEXT = "http://readium.org/webpub/default.jsonld"

    # "The Readium Web Publication Manifest has a single
    # requirement in terms of metadata: all publications must
    # include a title." -
    # https://github.com/readium/webpub-manifest#22-metadata        
    REQUIRED_METADATA_FIELDS = ["title"]

    # "In addition all publications should include a @type key to
    # describe the nature of the publication."
    RECOMMENDED_METADATA_FIELDS = ["@type"]

    # "A manifest must contain at least one link using the self
    # relationship where href is an absolute URI to the canonical
    # location of the manifest."
    # - https://github.com/readium/webpub-manifest#23-links
    REQUIRED_LINKS = [LinkRelations.SELF]
    
    # "A manifest must contain a readingOrder sub-collection."
    # https://github.com/readium/webpub-manifest#21-sub-collections
    REQUIRED_SUBCOLLECTIONS = [Roles.readingOrder]
    
    @property
    def is_manifest(self):
        """Override of Collection.is_manifest."""
        return True

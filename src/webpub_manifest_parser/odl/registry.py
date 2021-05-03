from webpub_manifest_parser.core.registry import CollectionRole, MediaType
from webpub_manifest_parser.opds2.registry import (
    OPDS2CollectionRolesRegistry,
    OPDS2MediaTypesRegistry,
)


class ODLMediaTypesRegistry(OPDS2MediaTypesRegistry):
    """Registry containing ODL 2.0 media types."""

    ODL_LICENSE_INFO_DOCUMENT = MediaType(key="application/vnd.odl.info+json")
    ODL_LICENSE_STATUS_DOCUMENT = MediaType(
        key="application/vnd.readium.license.status.v1.0+json"
    )


class ODLCollectionRolesRegistry(OPDS2CollectionRolesRegistry):
    """Registry containing ODPS 2.0 collection roles."""

    LICENSES = CollectionRole(key="licenses", compact=True, required=False)

    ODL_ROLES = [LICENSES] + OPDS2CollectionRolesRegistry.OPDS_2_0_ROLES

    def __init__(self):
        """Initialize a new instance of OPDS2CollectionRolesRegistry class."""
        super(ODLCollectionRolesRegistry, self).__init__()

        self._add_items(self.ODL_ROLES)

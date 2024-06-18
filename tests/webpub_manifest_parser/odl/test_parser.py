import datetime
import os
from unittest import TestCase

from dateutil.tz import tzoffset, tzutc

from webpub_manifest_parser.core import ManifestParserResult
from webpub_manifest_parser.odl import ODLFeedParserFactory
from webpub_manifest_parser.opds2.ast import (
    OPDS2AvailabilityInformation,
    OPDS2AvailabilityType,
    OPDS2FeedMetadata,
    OPDS2PublicationMetadata,
)
from webpub_manifest_parser.opds2.registry import OPDS2LinkRelationsRegistry
from webpub_manifest_parser.utils import first_or_default


class ODLParserTest(TestCase):
    def test(self):
        # Arrange
        parser_factory = ODLFeedParserFactory()
        parser = parser_factory.create()
        input_file_path = os.path.join(
            os.path.dirname(__file__), "../../files/odl/feed.json"
        )

        # Act
        result = parser.parse_file(input_file_path)

        # Assert
        self.assertIsInstance(result, ManifestParserResult)
        self.assertEqual(0, len(result.errors))

        feed = result.root
        self.assertIsInstance(feed.metadata, OPDS2FeedMetadata)
        self.assertEqual("Test", feed.metadata.title)

        self.assertEqual(1, len(feed.publications))
        [publication] = feed.publications

        self.assertIsInstance(publication.metadata, OPDS2PublicationMetadata)
        self.assertIsInstance(
            publication.metadata.availability, OPDS2AvailabilityInformation
        )
        self.assertEqual(
            OPDS2AvailabilityType.AVAILABLE.value,
            publication.metadata.availability.state,
        )

        self.assertEqual(1, len(publication.licenses))
        [license] = publication.licenses

        self.assertEqual(
            "urn:uuid:f7847120-fc6f-11e3-8158-56847afe9799", license.metadata.identifier
        )
        self.assertEqual(["application/epub+zip"], license.metadata.formats)

        self.assertEqual("USD", license.metadata.price.currency)
        self.assertEqual(7.99, license.metadata.price.value)

        self.assertEqual(
            datetime.datetime(2014, 4, 25, 12, 25, 21, tzinfo=tzoffset(None, 7200)),
            license.metadata.created,
        )

        self.assertEqual(30, license.metadata.terms.checkouts)
        self.assertEqual(
            datetime.datetime(2016, 4, 25, 12, 25, 21, tzinfo=tzoffset(None, 7200)),
            license.metadata.terms.expires,
        )
        self.assertEqual(10, license.metadata.terms.concurrency)
        self.assertEqual(5097600, license.metadata.terms.length)

        self.assertEqual(
            [
                "application/vnd.adobe.adept+xml",
                "application/vnd.readium.lcp.license.v1.0+json",
            ],
            license.metadata.protection.formats,
        )
        self.assertEqual(6, license.metadata.protection.devices)
        self.assertEqual(False, license.metadata.protection.copy_allowed)
        self.assertEqual(False, license.metadata.protection.print_allowed)
        self.assertEqual(False, license.metadata.protection.tts_allowed)

        self.assertIsInstance(
            license.metadata.availability, OPDS2AvailabilityInformation
        )
        self.assertEqual(
            OPDS2AvailabilityType.UNAVAILABLE.value, license.metadata.availability.state
        )
        self.assertEqual(
            datetime.datetime(2000, 5, 4, 3, 2, 1, tzinfo=tzutc()),
            license.metadata.availability.until,
        )
        self.assertEqual("a detailed reason", license.metadata.availability.detail)
        self.assertEqual(
            "https://registry.opds.io/reason#exhausted",
            license.metadata.availability.reason,
        )

        self.assertEqual(2, len(license.links))
        borrow_link = first_or_default(
            license.links.get_by_rel(OPDS2LinkRelationsRegistry.BORROW.key)
        )
        self.assertEqual(
            "application/vnd.readium.license.status.v1.0+json", borrow_link.type
        )

        self_link = first_or_default(
            license.links.get_by_rel(OPDS2LinkRelationsRegistry.SELF.key)
        )
        self.assertEqual("application/vnd.odl.info+json", self_link.type)

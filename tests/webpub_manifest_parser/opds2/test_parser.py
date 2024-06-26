import datetime
import json
import os
from unittest import TestCase

from dateutil.tz import tzutc

from webpub_manifest_parser.core import ManifestParserResult
from webpub_manifest_parser.core.ast import (
    CompactCollection,
    Contributor,
    LinkList,
    PresentationMetadata,
)
from webpub_manifest_parser.opds2 import OPDS2FeedParserFactory
from webpub_manifest_parser.opds2.ast import (
    OPDS2AcquisitionObject,
    OPDS2AvailabilityInformation,
    OPDS2AvailabilityType,
    OPDS2Feed,
    OPDS2FeedMetadata,
    OPDS2LinkProperties,
    OPDS2PublicationMetadata,
)
from webpub_manifest_parser.opds2.registry import (
    OPDS2LinkRelationsRegistry,
    OPDS2MediaTypesRegistry,
)
from webpub_manifest_parser.utils import first_or_default


class OPDS2ParserTest(TestCase):
    def test(self):
        # Arrange
        parser_factory = OPDS2FeedParserFactory()
        parser = parser_factory.create()
        input_file_path = os.path.join(
            os.path.dirname(__file__), "../../files/opds2/feed.json"
        )

        # Act
        result = parser.parse_file(input_file_path)

        # Assert
        self.assertIsInstance(result, ManifestParserResult)
        self.assertEqual(0, len(result.errors))

        feed = result.root
        self.assertIsInstance(feed, OPDS2Feed)

        self.assertIsInstance(feed.metadata, OPDS2FeedMetadata)
        self.assertEqual("Example listing publications", feed.metadata.title)

        self.assertIsInstance(feed.links, list)
        self.assertEqual(1, len(feed.links))
        [manifest_link] = feed.links
        self.assertEqual(OPDS2LinkRelationsRegistry.SELF.key, manifest_link.rels[0])
        self.assertEqual("http://example.com/new", manifest_link.href)
        self.assertEqual(OPDS2MediaTypesRegistry.OPDS_FEED.key, manifest_link.type)

        self.assertIsInstance(feed.publications, list)
        self.assertEqual(2, len(feed.publications))
        publication = feed.publications[0]

        self.assertIsInstance(publication.metadata, OPDS2PublicationMetadata)
        self.assertEqual("http://schema.org/Book", publication.metadata.type)
        self.assertEqual("Moby-Dick", publication.metadata.title)
        self.assertEqual(
            [Contributor(name="Herman Melville", roles=[], links=LinkList())],
            publication.metadata.authors,
        )
        self.assertEqual("urn:isbn:978-3-16-148410-0", publication.metadata.identifier)
        self.assertEqual(
            ["urn:isbn:978-3-16-148410-0"], publication.metadata.reference_identifiers
        )
        self.assertEqual(["978-3-16-148410-0"], publication.metadata.isbns)
        self.assertEqual(["en"], publication.metadata.languages)
        self.assertEqual(
            datetime.datetime(2015, 9, 29, 17, 0, tzinfo=tzutc()),
            publication.metadata.modified,
        )
        self.assertIsInstance(
            publication.metadata.availability, OPDS2AvailabilityInformation
        )
        self.assertEqual(
            publication.metadata.availability.state,
            OPDS2AvailabilityType.UNAVAILABLE.value,
        )
        self.assertEqual(
            publication.metadata.availability.since,
            datetime.datetime(2019, 9, 29, 1, 3, 2, tzinfo=tzutc()),
        )
        self.assertEqual(
            publication.metadata.availability.detail,
            "This publication is no longer available in your subscription",
        )
        self.assertEqual(
            publication.metadata.availability.reason,
            "https://registry.opds.io/reason#removed",
        )
        self.assertIs(publication.metadata.time_tracking, True)

        self.assertIsInstance(publication.links, list)
        self.assertEqual(len(publication.links), 2)

        publication_self_link = first_or_default(
            publication.links.get_by_rel(OPDS2LinkRelationsRegistry.SELF.key)
        )
        self.assertEqual(
            OPDS2LinkRelationsRegistry.SELF.key, publication_self_link.rels[0]
        )
        self.assertEqual(
            "http://example.org/publication.json", publication_self_link.href
        )
        self.assertEqual(
            OPDS2MediaTypesRegistry.OPDS_PUBLICATION.key, publication_self_link.type
        )

        publication_acquisition_link = first_or_default(
            publication.links.get_by_rel(OPDS2LinkRelationsRegistry.OPEN_ACCESS.key)
        )
        self.assertEqual(
            OPDS2LinkRelationsRegistry.OPEN_ACCESS.key,
            publication_acquisition_link.rels[0],
        )
        self.assertEqual(
            "http://example.org/file.epub", publication_acquisition_link.href
        )
        self.assertEqual(
            OPDS2MediaTypesRegistry.EPUB_PUBLICATION_PACKAGE.key,
            publication_acquisition_link.type,
        )

        self.assertIsInstance(publication.images, CompactCollection)
        self.assertIsInstance(publication.images.links, list)
        self.assertEqual(3, len(publication.images.links))

        jpeg_cover_link = first_or_default(
            publication.images.links.get_by_href("http://example.org/cover.jpg")
        )
        self.assertEqual([], jpeg_cover_link.rels)
        self.assertEqual("http://example.org/cover.jpg", jpeg_cover_link.href)
        self.assertEqual(OPDS2MediaTypesRegistry.JPEG.key, jpeg_cover_link.type)
        self.assertEqual(1400, jpeg_cover_link.height)
        self.assertEqual(800, jpeg_cover_link.width)

        small_jpeg_cover_link = first_or_default(
            publication.images.links.get_by_href("http://example.org/cover-small.jpg")
        )
        self.assertEqual(
            "http://example.org/cover-small.jpg", small_jpeg_cover_link.href
        )
        self.assertEqual(OPDS2MediaTypesRegistry.JPEG.key, small_jpeg_cover_link.type)
        self.assertEqual(700, small_jpeg_cover_link.height)
        self.assertEqual(400, small_jpeg_cover_link.width)

        svg_cover_link = first_or_default(
            publication.images.links.get_by_href("http://example.org/cover.svg")
        )
        self.assertEqual(svg_cover_link.href, "http://example.org/cover.svg")
        self.assertEqual(svg_cover_link.type, OPDS2MediaTypesRegistry.SVG_XML.key)

        publication = feed.publications[1]
        self.assertIsInstance(publication.metadata, PresentationMetadata)
        self.assertEqual("http://schema.org/Book", publication.metadata.type)
        self.assertEqual("Adventures of Huckleberry Finn", publication.metadata.title)
        self.assertEqual(
            [
                Contributor(name="Mark Twain", roles=[], links=LinkList()),
                Contributor(
                    name="Samuel Langhorne Clemens", roles=[], links=LinkList()
                ),
            ],
            publication.metadata.authors,
        )
        self.assertEqual("urn:isbn:978-3-16-148410-0", publication.metadata.identifier)
        self.assertEqual(["eng", "fre"], publication.metadata.languages)
        self.assertEqual(
            datetime.datetime(2015, 9, 29, 0, 0, tzinfo=tzutc()),
            publication.metadata.published,
        )
        self.assertEqual(
            datetime.datetime(2015, 9, 29, 17, 0, 0, tzinfo=tzutc()),
            publication.metadata.modified,
        )

        self.assertIs(publication.metadata.availability, None)
        self.assertIs(publication.metadata.time_tracking, False)

        self.assertIsInstance(publication.links, list)

        publication_acquisition_link = first_or_default(
            publication.links.get_by_rel(OPDS2LinkRelationsRegistry.BORROW.key)
        )
        self.assertEqual(
            OPDS2LinkRelationsRegistry.BORROW.key, publication_acquisition_link.rels[0]
        )
        self.assertEqual(
            OPDS2MediaTypesRegistry.OPDS_PUBLICATION.key,
            publication_acquisition_link.type,
        )

        link_properties = publication_acquisition_link.properties
        self.assertIsInstance(link_properties, OPDS2LinkProperties)

        availability = link_properties.availability
        self.assertIsInstance(availability, OPDS2AvailabilityInformation)
        self.assertEqual(OPDS2AvailabilityType.AVAILABLE.value, availability.state)
        self.assertEqual(
            datetime.datetime(2019, 9, 29, 1, 3, 2, tzinfo=tzutc()),
            availability.until,
        )
        self.assertEqual("a detailed reason", availability.detail)
        self.assertEqual("http://terms.example.org/available", availability.reason)

        self.assertEqual(2, len(link_properties.indirect_acquisition))

        indirect_acquisition_object = link_properties.indirect_acquisition[0]
        self.assertEqual(
            "application/vnd.adobe.adept+xml", indirect_acquisition_object.type
        )
        self.assertEqual(1, len(indirect_acquisition_object.child))
        self.assertIsInstance(
            indirect_acquisition_object.child[0], OPDS2AcquisitionObject
        )
        self.assertEqual(
            "application/epub+zip", indirect_acquisition_object.child[0].type
        )

        indirect_acquisition_object = link_properties.indirect_acquisition[1]
        self.assertEqual(
            "application/vnd.readium.lcp.license.v1.0+json",
            indirect_acquisition_object.type,
        )
        self.assertEqual(1, len(indirect_acquisition_object.child))
        self.assertIsInstance(
            indirect_acquisition_object.child[0], OPDS2AcquisitionObject
        )
        self.assertEqual(
            "application/epub+zip", indirect_acquisition_object.child[0].type
        )

    def test_incorrect_language_fallback(self):
        """Whenever an incorrectly formatted language code is encountered
        the languages property should fallback to the default `[]`
        and not be set to the unsupported NoneType value
        """
        parser_factory = OPDS2FeedParserFactory()
        parser = parser_factory.create()
        with open("tests/files/opds2/feed.json") as fp:
            feed = json.load(fp)
        feed["publications"][0]["metadata"]["language"] = "en uk"
        feed["publications"] = [feed["publications"][0]]

        result = parser.parse_json(feed)
        assert [] == result.root.publications[0].metadata.languages

import datetime
import os
from unittest import TestCase

from nose.tools import eq_

from webpub_manifest_parser.core.ast import CompactCollection, Metadata
from webpub_manifest_parser.rwpm.ast import RWPMManifest
from webpub_manifest_parser.rwpm.parser import RWPMDocumentParserFactory
from webpub_manifest_parser.rwpm.registry import (
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
    RWPMMediaTypesRegistry,
)
from webpub_manifest_parser.utils import first_or_default


class RWPMParserTest(TestCase):
    def test(self):
        # Arrange
        parser_factory = RWPMDocumentParserFactory()
        parser = parser_factory.create()
        input_file_path = os.path.join(
            os.path.dirname(__file__), "../../files/rwpm/spec_example.json"
        )

        # Act
        manifest = parser.parse_file(input_file_path)

        # Assert
        self.assertIsInstance(manifest.context, list)
        self.assertEqual(1, len(manifest.context))
        [context] = manifest.context
        self.assertEqual(context, "https://readium.org/webpub-manifest/context.jsonld")

        self.assertIsInstance(manifest.metadata, Metadata)
        self.assertEqual("http://schema.org/Book", manifest.metadata.type)
        self.assertEqual("Moby-Dick", manifest.metadata.title)
        self.assertEqual("Herman Melville", manifest.metadata.author)
        self.assertEqual("urn:isbn:978031600000X", manifest.metadata.identifier)
        self.assertEqual("en", manifest.metadata.language)
        self.assertEqual(
            datetime.datetime(2015, 9, 29, 17, 0, 0), manifest.metadata.modified
        )

        self.assertIsInstance(manifest.links, list)
        self.assertEqual(3, len(manifest.links))

        self_link = first_or_default(
            manifest.links.get_by_rel(RWPMLinkRelationsRegistry.SELF.key)
        )
        self.assertIsNotNone(self_link)
        self.assertIn(RWPMLinkRelationsRegistry.SELF.key, self_link.rel)
        self.assertEqual("https://example.com/manifest.json", self_link.href)
        self.assertEqual(RWPMMediaTypesRegistry.MANIFEST.key, self_link.type)

        alternate_link = first_or_default(
            manifest.links.get_by_rel(RWPMLinkRelationsRegistry.ALTERNATE.key)
        )
        self.assertIsNotNone(alternate_link)
        self.assertIn(RWPMLinkRelationsRegistry.ALTERNATE.key, alternate_link.rel)
        self.assertEqual("https://example.com/publication.epub", alternate_link.href)
        self.assertEqual(
            RWPMMediaTypesRegistry.EPUB_PUBLICATION_PACKAGE.key, alternate_link.type
        )

        search_link = first_or_default(
            manifest.links.get_by_rel(RWPMLinkRelationsRegistry.SEARCH.key)
        )
        self.assertIsNotNone(search_link)
        self.assertIn(RWPMLinkRelationsRegistry.SEARCH.key, search_link.rel)
        self.assertEqual("https://example.com/search{?query}", search_link.href)
        self.assertEqual(RWPMMediaTypesRegistry.HTML.key, search_link.type)

        self.assertIsInstance(manifest.reading_order, CompactCollection)
        # self.assertIsInstance(manifest.reading_order.role, CollectionRole)
        # self.assertEqual(manifest.reading_order.role.key, RWPMCollectionRolesRegistry.READING_ORDER.key)
        self.assertIsInstance(manifest.reading_order.links, list)
        self.assertEqual(2, len(manifest.reading_order.links))
        # [reading_order_link] = manifest.reading_order.links
        # self.assertEqual('https://example.com/c001.html', reading_order_link.href)
        # self.assertEqual(RWPMMediaTypesRegistry.HTML.key, reading_order_link.type)
        # self.assertEqual('Chapter 1', reading_order_link.title)

        # eq_(len(manifest.sub_collections), 2)
        #
        # reading_order_sub_collection = first_or_default(
        #     manifest.sub_collections.get_by_role(
        #         RWPMCollectionRolesRegistry.READING_ORDER.key
        #     )
        # )
        # eq_(
        #     reading_order_sub_collection.role.key,
        #     RWPMCollectionRolesRegistry.READING_ORDER.key,
        # )
        # eq_(len(reading_order_sub_collection.links), 2)
        # eq_(reading_order_sub_collection.links[0].href, "https://example.com/c001.html")
        # eq_(reading_order_sub_collection.links[0].type, RWPMMediaTypesRegistry.HTML.key)
        # eq_(reading_order_sub_collection.links[0].title, "Chapter 1")
        #
        # eq_(reading_order_sub_collection.links[1].href, "https://example.com/c002.html")
        # eq_(reading_order_sub_collection.links[1].type, RWPMMediaTypesRegistry.HTML.key)
        # eq_(reading_order_sub_collection.links[1].title, "Chapter 2")
        #
        # resources_sub_collection = first_or_default(
        #     manifest.sub_collections.get_by_role(
        #         RWPMCollectionRolesRegistry.RESOURCES.key
        #     )
        # )
        # eq_(
        #     resources_sub_collection.role.key, RWPMCollectionRolesRegistry.RESOURCES.key
        # )
        # eq_(len(resources_sub_collection.links), 5)
        # eq_(resources_sub_collection.links[0].rel, RWPMLinkRelationsRegistry.COVER.key)
        # eq_(resources_sub_collection.links[0].href, "https://example.com/cover.jpg")
        # eq_(resources_sub_collection.links[0].type, RWPMMediaTypesRegistry.JPEG.key)
        # eq_(resources_sub_collection.links[0].height, 600)
        # eq_(resources_sub_collection.links[0].width, 400)
        #
        # eq_(resources_sub_collection.links[1].href, "https://example.com/style.css")
        # eq_(resources_sub_collection.links[1].type, RWPMMediaTypesRegistry.CSS.key)
        #
        # eq_(resources_sub_collection.links[2].href, "https://example.com/whale.jpg")
        # eq_(resources_sub_collection.links[2].type, RWPMMediaTypesRegistry.JPEG.key)
        #
        # eq_(resources_sub_collection.links[3].href, "https://example.com/boat.svg")
        # eq_(resources_sub_collection.links[3].type, RWPMMediaTypesRegistry.SVG_XML.key)
        #
        # eq_(resources_sub_collection.links[4].href, "https://example.com/notes.html")
        # eq_(resources_sub_collection.links[4].type, RWPMMediaTypesRegistry.HTML.key)

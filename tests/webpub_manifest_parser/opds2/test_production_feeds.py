import logging
from unittest import TestCase, skip

import requests
from parameterized import parameterized

from webpub_manifest_parser.core import ManifestParserResult
from webpub_manifest_parser.opds2 import OPDS2FeedParserFactory


class OPDS2FeedParserIntegrationTest(TestCase):
    @parameterized.expand(
        [
            (
                "Feedbooks OPDS 2.0 feed",
                "https://catalog.feedbooks.com/catalog/index.json",
            ),
            (
                "Fulcrum OPDS 2.0 feed",
                "https://www.fulcrum.org/api/opds/umpebc_oa",
            ),
        ]
    )
    @skip("These tests require network access")
    def test_production_feed(self, _, url, encoding="utf-8"):
        # Arrange

        # NOTE: Using logging.basicConfig doesn't work because there are no associated handlers,
        # so we have to set the root's level manually
        logging.root.level = logging.WARNING

        parser_factory = OPDS2FeedParserFactory()
        parser = parser_factory.create()

        # Act
        result = parser.parse_url(url, encoding)

        # Assert
        self.assertIsInstance(result, ManifestParserResult)
        self.assertEqual(0, len(result.errors))

    @skip("The test requires a running SOCKS proxy to pull the ProQuest feed")
    def test_proquest_feed(self):
        """Ensure that the production ProQuest can be parsed correctly.

        NOTE: The feed is accessible only from whitelisted IP addresses,
        hence to run this test you need to run a SOCKS proxy \
        tunneling all the requests through the machine with the whitelisted IP address.

        npm install -g http-proxy-to-socks
        ssh -D 8888 -f -C -q -N <machine with the whitelisted IP address>
        hpts -s 127.0.0.1:8888 -p 8080
        """
        # Arrange
        logging.basicConfig(level=logging.WARNING)
        proxies = {"http": "http://localhost:8080", "https": "https://localhost:8080"}
        page = 0
        pages = None
        items_per_page = 5000
        parser_factory = OPDS2FeedParserFactory()
        parser = parser_factory.create()

        # Act
        while True:
            page += 1

            params = {"page": page, "hitsPerPage": items_per_page}

            try:
                print("Started downloading page # {0}/{1}".format(page, pages))

                response = requests.get(
                    "https://ebookcentral.proquest.com/lib/nyulibrary-ebooks/BooksCatalog",
                    params=params,
                    proxies=proxies,
                )

                print("Finished downloading page # {0}/{1}".format(page, pages))

                json_response = response.json()
                json_manifest = json_response["opdsFeed"]

                print("Started parsing page # {0}/{1}".format(page, pages))

                result = parser.parse_json(json_manifest)

                print("Finished parsing page # {0}/{1}".format(page, pages))

                # Assert
                self.assertIsInstance(result, ManifestParserResult)
                self.assertEqual(0, len(result.errors))

                number_of_items = result.root.metadata.number_of_items
                pages = number_of_items // items_per_page
            except Exception:
                logging.exception(
                    "An unexpected exception occurred during parsing of the ProQuest feed"
                )
                raise

import csv
import logging
from unittest import TestCase, skip

from parameterized import parameterized
from requests.auth import HTTPBasicAuth

from webpub_manifest_parser.core import ManifestParserResult
from webpub_manifest_parser.core.analyzer import NodeFinder
from webpub_manifest_parser.odl import ODLFeedParserFactory
from webpub_manifest_parser.opds2.ast import OPDS2Publication
from webpub_manifest_parser.utils import first_or_default


class ODLFeedParserIntegrationTest(TestCase):
    @staticmethod
    def _print_errors(feed_name, feed_url, feed_parsing_result):
        """Print all the parsing errors in the console.

        :param feed_name: Feed's feed_name
        :type feed_name: str

        :param feed_url: Feed's URL
        :type feed_url: str

        :param feed_parsing_result: Parsing result
        :type feed_parsing_result: ManifestParserResult
        """
        node_finder = NodeFinder()
        fieldnames = ['feed_name', 'feed_url', 'publication_id', "publication_title", "error"]

        with open('error.csv', 'a') as output:
            writer = csv.DictWriter(output, fieldnames=fieldnames)

            writer.writeheader()

            if feed_parsing_result.errors:
                for index, error in enumerate(feed_parsing_result.errors):
                    publication = node_finder.find_parent_or_self(
                        feed_parsing_result.root, error.node, OPDS2Publication
                    )

                    if publication:
                        writer.writerow(
                            {
                                "feed_name": feed_name,
                                "feed_url": feed_url,
                                "publication_id": publication.metadata.identifier,
                                "publication_title": publication.metadata.title,
                                "error": error.error_message
                            }
                        )
                    else:
                        writer.writerow(
                            {
                                "feed_name": feed_name,
                                "feed_url": feed_url,
                                "publication_id": publication.metadata.identifier,
                                "publication_title": publication.metadata.title,
                                "error": error.error_message
                            }
                        )
                    # print("{0}. {1}".format(index + 1, error.error_message))

    @parameterized.expand(
        [
            (
                "De Marque / Feedbooks Market OPDS 2.0 + ODL feed",
                "https://market.feedbooks.com/api/libraries/harvest.json",
                "utf-8",
                HTTPBasicAuth("*****", "*****"),
            )
        ]
    )
    @skip("The test requires credentials to pull the feed")
    def test_dpla_feed(
        self, feed_name, feed_url, feed_encoding="utf-8", feed_auth=None
    ):
        """Ensure that the ODL 2.x parser correctly parses real production feeds.

        :param feed_name: Feed's name
        :type feed_name: str

        :param feed_url: Feed's URL
        :type feed_url: str

        :param feed_encoding: Feed's feed_encoding
        :type feed_encoding: str

        :param feed_auth: Feed's authentication information
        :type feed_auth: requests.auth.AuthBase
        """
        # Arrange

        # NOTE: Using logging.basicConfig doesn't work because there are no associated handlers,
        # so we have to set the root's level manually
        logging.root.level = logging.WARNING

        parser_factory = ODLFeedParserFactory()
        parser = parser_factory.create()

        # Act
        while True:
            try:
                result = parser.parse_url(feed_url, feed_encoding, auth=feed_auth)
            except Exception as exception:
                logging.exception(
                    "Unexpected exception occurred during parsing {0}".format(feed_name)
                )
                raise

            # Assert
            self.assertIsInstance(result, ManifestParserResult)

            self._print_errors(feed_name, feed_url, result)

            next_link = first_or_default(result.root.links.get_by_rel("next"))

            if not next_link:
                break

            feed_url = next_link.href

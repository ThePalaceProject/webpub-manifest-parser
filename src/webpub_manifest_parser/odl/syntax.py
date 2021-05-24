from webpub_manifest_parser.odl.ast import ODLFeed
from webpub_manifest_parser.opds2.syntax import OPDS2SyntaxAnalyzer


class ODLSyntaxAnalyzer(OPDS2SyntaxAnalyzer):
    """OPDS 2.0 syntax analyzer."""

    def _create_manifest(self):
        """Create a new OPDS 2.0 manifest.

        :return: OPDS 2.0 manifest
        :rtype: Manifestlike
        """
        return ODLFeed()

from webpub_manifest_parser.core import ManifestParser, ManifestParserFactory
from webpub_manifest_parser.opds2.registry import (
    OPDS2CollectionRolesRegistry,
    OPDS2LinkRelationsRegistry,
    OPDS2MediaTypesRegistry,
)
from webpub_manifest_parser.opds2.semantic import OPDS2SemanticAnalyzer
from webpub_manifest_parser.opds2.syntax import OPDS2SyntaxAnalyzer


class OPDS2FeedParserFactory(ManifestParserFactory):
    """Factory creating OPDS 2.0 parser."""

    def create(self):
        """Create a new OPDS 2.0 parser.

        :return: OPDS 2.0 parser
        :rtype: Parser
        """
        media_types_registry = OPDS2MediaTypesRegistry()
        link_relations_registry = OPDS2LinkRelationsRegistry()
        collection_roles_registry = OPDS2CollectionRolesRegistry()
        syntax_analyzer = OPDS2SyntaxAnalyzer()
        semantic_analyzer = OPDS2SemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )
        parser = ManifestParser(syntax_analyzer, semantic_analyzer)

        return parser

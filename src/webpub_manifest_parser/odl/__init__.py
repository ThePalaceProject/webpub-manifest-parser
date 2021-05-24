from webpub_manifest_parser.core import ManifestParser, ManifestParserFactory
from webpub_manifest_parser.odl.semantic import ODLSemanticAnalyzer
from webpub_manifest_parser.odl.syntax import ODLSyntaxAnalyzer
from webpub_manifest_parser.opds2.registry import (
    OPDS2CollectionRolesRegistry,
    OPDS2LinkRelationsRegistry,
    OPDS2MediaTypesRegistry,
)


class ODLFeedParserFactory(ManifestParserFactory):
    """Factory creating a new ODL parser."""

    def create(self):
        """Create a new ODL parser.

        :return: ODL parser
        :rtype: Parser
        """
        media_types_registry = OPDS2MediaTypesRegistry()
        link_relations_registry = OPDS2LinkRelationsRegistry()
        collection_roles_registry = OPDS2CollectionRolesRegistry()
        syntax_analyzer = ODLSyntaxAnalyzer()
        semantic_analyzer = ODLSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )
        parser = ManifestParser(syntax_analyzer, semantic_analyzer)

        return parser

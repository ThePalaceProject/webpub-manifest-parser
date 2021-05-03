from webpub_manifest_parser.core import ManifestParser, ManifestParserFactory
from webpub_manifest_parser.rwpm.registry import (
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
    RWPMMediaTypesRegistry,
)
from webpub_manifest_parser.rwpm.semantic import RWPMSemanticAnalyzer
from webpub_manifest_parser.rwpm.syntax import RWPMSyntaxAnalyzer


class RWPMManifestParserFactory(ManifestParserFactory):
    """Factory creating RWPM parsers."""

    def create(self):
        """Create a new RWPMManifestParser.

        :return: RWPM parser instance
        :rtype: Parser
        """
        media_types_registry = RWPMMediaTypesRegistry()
        link_relations_registry = RWPMLinkRelationsRegistry()
        collection_roles_registry = RWPMCollectionRolesRegistry()
        syntax_analyzer = RWPMSyntaxAnalyzer()
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )
        parser = ManifestParser(syntax_analyzer, semantic_analyzer)

        return parser

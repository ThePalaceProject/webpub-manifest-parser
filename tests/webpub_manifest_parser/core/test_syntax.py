import datetime
from unittest import TestCase

from dateutil.tz import tzutc
from parameterized import parameterized

from tests.webpub_manifest_parser.core.test_analyzer import AnalyzerTest
from webpub_manifest_parser.core.ast import (
    Manifestlike,
    Metadata,
    Node,
    PresentationMetadata,
)
from webpub_manifest_parser.core.syntax import (
    MissingPropertyError,
    SyntaxAnalyzer,
    SyntaxAnalyzerError,
)


class TestSyntaxAnalyzer(SyntaxAnalyzer):
    def _create_manifest(self):
        return Manifestlike()


class SyntaxAnalyzerTest(AnalyzerTest):
    @parameterized.expand(
        [
            # 1. Ensure that the syntax analyzer correctly restores
            #    from the error related to top missing `links` property and continues parsing `metadata` property.
            (
                "top_required_links_property_is_missing",
                {"metadata": {"modified": "2021-01-01T00:00:00Z"}},
                Manifestlike(
                    metadata=PresentationMetadata(
                        modified=datetime.datetime(2021, 1, 1, tzinfo=tzutc()),
                        languages=[],
                        authors=[],
                        translators=[],
                        editors=[],
                        artists=[],
                        illustrators=[],
                        letterers=[],
                        pencilers=[],
                        colorists=[],
                        inkers=[],
                        narrators=[],
                        contributors=[],
                        publishers=[],
                        imprints=[],
                        subjects=[],
                    )
                ),
                [
                    MissingPropertyError(Manifestlike(), Manifestlike.links),
                    MissingPropertyError(PresentationMetadata(), Metadata.title),
                ],
            ),
            # 2. Ensure that the syntax analyzer restores from the error related to incorrect `modified` property
            #    and continues parsing other nested properties (`subtitle`, etc.).
            (
                "incorrect_metadata_modified_property",
                {"metadata": {"subtitle": "Subtitle", "modified": "202X"}},
                Manifestlike(
                    metadata=PresentationMetadata(
                        subtitle="Subtitle",
                        modified=None,
                        languages=[],
                        authors=[],
                        translators=[],
                        editors=[],
                        artists=[],
                        illustrators=[],
                        letterers=[],
                        pencilers=[],
                        colorists=[],
                        inkers=[],
                        narrators=[],
                        contributors=[],
                        publishers=[],
                        imprints=[],
                        subjects=[],
                    )
                ),
                [
                    MissingPropertyError(Manifestlike(), Manifestlike.links),
                    MissingPropertyError(PresentationMetadata(), Metadata.title),
                    SyntaxAnalyzerError(
                        PresentationMetadata(),
                        Metadata.modified,
                        u"Value '202X' is not a correct date & time value: "
                        u"it does not comply with ISO 8601 date & time formatting rules",
                    ),
                ],
            ),
            # 3. Ensure that the syntax analyzer correctly parses required property `title`
            #    even though one of the nested properties (`modified`) is not correct.
            (
                "incorrect_metadata_modified_property",
                {
                    "metadata": {
                        "title": "Title",
                        "subtitle": "Subtitle",
                        "modified": "202X",
                    }
                },
                Manifestlike(
                    metadata=PresentationMetadata(
                        title="Title",
                        subtitle="Subtitle",
                        modified=None,
                        languages=[],
                        authors=[],
                        translators=[],
                        editors=[],
                        artists=[],
                        illustrators=[],
                        letterers=[],
                        pencilers=[],
                        colorists=[],
                        inkers=[],
                        narrators=[],
                        contributors=[],
                        publishers=[],
                        imprints=[],
                        subjects=[],
                    )
                ),
                [
                    MissingPropertyError(Manifestlike(), Manifestlike.links),
                    SyntaxAnalyzerError(
                        PresentationMetadata(),
                        Metadata.modified,
                        u"Value '202X' is not a correct date & time value: "
                        u"it does not comply with ISO 8601 date & time formatting rules",
                    ),
                ],
            ),
        ]
    )
    def test(self, _, raw_manifest, expected_manifest_ast, expected_errors):
        """Ensure that syntax analyzer correctly recovers from syntax errors.

        :param raw_manifest: Python dictionary containing an RWPM-like manifest
        :type raw_manifest: Dict

        :param expected_manifest_ast: AST object representing an RWPM-like manifest parsed from `raw_manifest`
        :type expected_manifest_ast: Node

        :param expected_errors: List of expected syntax errors
        :type expected_errors: List[webpub_manifest_parser.core.analyzer.BaseAnalyzerError]
        """
        # Arrange
        analyzer = TestSyntaxAnalyzer()
        manifest_ast = analyzer.analyze(raw_manifest)

        # Act
        self.assertEqual(expected_manifest_ast, manifest_ast)

        # Assert
        self.check_analyzer_errors(
            analyzer.context.errors, expected_errors, SyntaxAnalyzerError
        )

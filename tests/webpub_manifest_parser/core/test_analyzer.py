from unittest import TestCase

from webpub_manifest_parser.core.analyzer import BaseAnalyzerError


class AnalyzerTest(TestCase):
    def check_analyzer_errors(
        self, context_errors, expected_errors, error_class=BaseAnalyzerError
    ):
        self.assertEqual(len(expected_errors), len(context_errors))

        for expected_error in expected_errors:
            self.assertIsInstance(expected_error, error_class)

            for context_error in context_errors:
                self.assertIsInstance(context_error, error_class)

                if (
                    context_error.node.__class__ == expected_error.node.__class__
                    and (
                        (
                            context_error.node_property is None
                            and expected_error.node_property is None
                        )
                        or (
                            context_error.node_property is not None
                            and expected_error.node_property is not None
                            and context_error.node_property.__class__
                            == expected_error.node_property.__class__
                        )
                    )
                    and context_error.error_message == expected_error.error_message
                ):
                    break
            else:
                self.fail(
                    "Expected error for {0} node's property '{1}' with error message \"{2}\" wasn't raised".format(
                        expected_error.node.__class__,
                        expected_error.node_property.key
                        if expected_error.node_property
                        else "",
                        expected_error.error_message,
                    )
                )

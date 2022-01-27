import datetime
from abc import ABCMeta
from unittest import TestCase

import pytz
from parameterized import parameterized

from webpub_manifest_parser.core.ast import (
    ArrayOfContributorsProperty,
    ArrayOfSubjectsProperty,
    Contributor,
)
from webpub_manifest_parser.core.parsers import (
    AnyOfParser,
    ArrayParser,
    DateParser,
    DateTimeParser,
    NumberParser,
    StringParser,
    TypeParser,
    URIParser,
    ValueParser,
    ValueParserError,
    find_parser,
)


class ParserTest(metaclass=ABCMeta):
    PARSER_CLASS = ValueParser

    def _create_parser(self):
        return self.PARSER_CLASS()

    def test(self, _, value, expected_result, expected_error=None):
        """Ensure that the parser returns the expected result or raises the expected exception."""
        parser = self._create_parser()

        if expected_error:
            with self.assertRaises(expected_error.__class__) as error_context:
                parser.parse(value)

            self.assertEqual(
                error_context.exception.error_message, expected_error.error_message
            )
        else:
            result = parser.parse(value)

            self.assertEqual(expected_result, result)


class NumberParserTest(ParserTest, TestCase):
    PARSER_CLASS = NumberParser

    @parameterized.expand(
        [
            ("correct_number", "123", 123),
            (
                "incorrect_number",
                "abc",
                None,
                ValueParserError("abc", "could not convert string to float: 'abc'"),
            ),
        ]
    )
    def test(self, _, value, expected_result, expected_error_class=None):
        super().test(_, value, expected_result, expected_error_class)


class URIParserTest(ParserTest, TestCase):
    PARSER_CLASS = URIParser

    @parameterized.expand(
        [
            ("correct_uri", "http://example.com", "http://example.com"),
            (
                "incorrect_uri",
                "123",
                None,
                ValueParserError("123", "'123' is not a 'uri'"),
            ),
        ]
    )
    def test(self, _, value, expected_result, expected_error_class=None):
        super().test(_, value, expected_result, expected_error_class)


class DateParserTest(ParserTest, TestCase):
    PARSER_CLASS = DateParser

    @parameterized.expand(
        [
            (
                "yyyy",
                "2020",
                datetime.datetime(2020, 1, 1, 0, 0),
            ),
            (
                "yyyy",
                2020,
                None,
                ValueParserError("2020", "Value '2020' must be a string"),
            ),
            (
                "yyyy-mm",
                "2020-01",
                datetime.datetime(2020, 1, 1),
            ),
            ("yyyy-mm-dd", "2020-01-01", datetime.datetime(2020, 1, 1)),
            (
                "incorrect_date",
                "2020-01-0",
                None,
                ValueParserError(
                    "2020-01-0", "Value '2020-01-0' is not a correct date"
                ),
            ),
            (
                "yyyy-mm-ddThh:mm:ss",
                "2020-01-01T10:10:10",
                None,
                ValueParserError(
                    "2020-01-01T10:10:10",
                    "Value '2020-01-01T10:10:10' is not a correct date",
                ),
            ),
            (
                "yyyy-mm-ddThh:mm:ss",
                "2020-01-01 10:10:10",
                None,
                ValueParserError(
                    "2020-01-01 10:10:10",
                    "Value '2020-01-01 10:10:10' is not a correct date",
                ),
            ),
            (
                "yyyy-mm-ddThh:mm:ss",
                "2020-01-01 10:10:10-03:00",
                None,
                ValueParserError(
                    "2020-01-01 10:10:10-03:00",
                    "Value '2020-01-01 10:10:10-03:00' is not a correct date",
                ),
            ),
        ]
    )
    def test(self, _, value, expected_result, expected_error_class=None):
        super().test(_, value, expected_result, expected_error_class)


class DateTimeParserTest(ParserTest, TestCase):
    PARSER_CLASS = DateTimeParser

    @parameterized.expand(
        [
            (
                "yyyy",
                "2020",
                datetime.datetime(2020, 1, 1),
            ),
            (
                "yyyy",
                2020,
                None,
                ValueParserError("2020", "Value '2020' must be a string"),
            ),
            (
                "yyyy-mm",
                "2020-01",
                datetime.datetime(2020, 1, 1),
            ),
            ("yyyy-mm-dd", "2020-01-01", datetime.datetime(2020, 1, 1)),
            (
                "incorrect_date",
                "2020-01-0",
                None,
                ValueParserError(
                    "2020-01-0",
                    "Value '2020-01-0' is not a correct date & time value: it does not comply with ISO 8601 date & time formatting rules",
                ),
            ),
            (
                "yyyy-mm-ddThh:mm:ss",
                "2020-01-01T10:10:10",
                datetime.datetime(2020, 1, 1, 10, 10, 10),
            ),
            (
                "yyyy-mm-ddThh:mm:ss",
                "2020-01-01 10:10:10",
                datetime.datetime(2020, 1, 1, 10, 10, 10),
            ),
            (
                "yyyy-mm-ddThh:mm:ss",
                "2020-01-01 10:10:10-03:00",
                datetime.datetime(
                    2020,
                    1,
                    1,
                    10,
                    10,
                    10,
                    tzinfo=pytz.FixedOffset(
                        datetime.timedelta(hours=-3).total_seconds() / 60
                    ),
                ),
            ),
        ]
    )
    def test(self, _, value, expected_result, expected_error_class=None):
        super().test(_, value, expected_result, expected_error_class)


class FunctionsTest(TestCase):
    @parameterized.expand(
        [
            (
                "contributor_property",
                ArrayOfContributorsProperty.PARSER,
                TypeParser,
                [
                    (
                        ArrayParser(
                            AnyOfParser([StringParser(), TypeParser(Contributor)])
                        ),
                        TypeParser(Contributor),
                    ),
                    (None, TypeParser(Contributor)),
                ],
            ),
            (
                "subject_property",
                ArrayOfSubjectsProperty.PARSER,
                TypeParser,
                [
                    (
                        ArrayParser(
                            AnyOfParser([StringParser(), TypeParser(Contributor)])
                        ),
                        TypeParser(Contributor),
                    ),
                    (None, TypeParser(Contributor)),
                ],
            ),
        ]
    )
    def test_find_parser(self, _, parent_parser, child_parser_type, expected_results):
        # Act
        actual_results = find_parser(parent_parser, child_parser_type)

        # Assert
        self.assertEqual(len(expected_results), len(actual_results))

        for expected_result, actual_result in zip(expected_results, actual_results):
            expected_parent_parser, expected_child_parser = expected_result
            actual_parent_parser, actual_child_parser = expected_result

            if expected_parent_parser is None:
                self.assertIsNone(actual_parent_parser)
            else:
                self.assertEqual(
                    expected_parent_parser.__class__, actual_parent_parser.__class__
                )

            self.assertEqual(expected_child_parser, actual_child_parser)

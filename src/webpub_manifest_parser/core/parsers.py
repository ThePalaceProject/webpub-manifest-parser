import logging
import re
from abc import ABCMeta, abstractmethod
from pydoc import locate

import jsonschema  # noqa: I201
import six  # noqa: I201
from dateutil import parser as datetime_parser  # noqa: I201, I100
from jsonschema import FormatError  # noqa: I201, I100
from uritemplate import URITemplate  # noqa: I201

from webpub_manifest_parser.errors import BaseError
from webpub_manifest_parser.utils import encode, is_string


class ValueParserError(BaseError):
    """Base class for all errors raised by value parsers."""

    def __init__(self, value, message, inner_exception=None):
        """Initialize a new instance of ValueParsingError class.

        :param value: Value associated with this error
        :type value: Any

        :param message: String containing description of the error occurred
        :type message: basestring

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        super(ValueParserError, self).__init__(message, inner_exception)

        self._value = value

    @property
    def value(self):
        """Return the value associated with this error.

        :return: Value associated with this error
        :rtype: Any
        """
        return self._value


@six.add_metaclass(ABCMeta)
class ValueParser(object):
    """Base parser class."""

    @abstractmethod
    def parse(self, value):
        """Parse the value, raise ParsingError if the value is not correct, otherwise return the processed value.

        :param value: Value to validate
        :type value: Any

        :return: Processed value (for example, datetime object in the case of a value containing a date&time string)
        :rtype: Any

        :raise: ValidationError
        """
        raise NotImplementedError()


class AnyOfParser(ValueParser):
    """Parser making sure that at least one of the inner parsers succeed."""

    def __init__(self, inner_parsers):
        """Initialize a new instance of AnyOfParser class.

        :param inner_parsers: List of composed parsers
        :type inner_parsers: List[ValueParser]
        """
        self._inner_parsers = inner_parsers
        self._logger = logging.getLogger(__name__)

    @property
    def inner_parsers(self):
        """Return the inner parsers.

        :return: Inner parsers
        :rtype: List[ValueParser]
        """
        return self._inner_parsers

    def parse(self, value):
        """Make sure that at least one of the inner parsers succeed, otherwise raise the first validation error.

        :param value: Value
        :type value: Any

        :return: First valid value
        :rtype: Any

        :raise: ValidationError
        """
        first_validation_error = None

        for parser in self._inner_parsers:
            self._logger.debug(u"Running {0} parser".format(parser))

            try:
                result = parser.parse(value)

                self._logger.debug(
                    u"Parser {0} succeeded: {1}".format(parser, encode(result))
                )

                return result
            except ValueParserError as error:
                self._logger.debug(u"Parser {0} failed".format(encode(parser)))

                if first_validation_error is None:
                    first_validation_error = error

        self._logger.debug(u"All parsers failed")

        raise first_validation_error


@six.add_metaclass(ABCMeta)
class NumericParser(ValueParser):
    """Numeric parser."""

    def __init__(
        self, minimum=None, exclusive_minimum=None, maximum=None, exclusive_maximum=None
    ):
        """Initialize a new instance of NumericParser class.

        :param minimum: Minimum value
        :type minimum: Numeric

        :param exclusive_minimum: Exclusive minimum value
        :type exclusive_minimum: Numeric

        :param maximum: Maximum value
        :type maximum: Numeric

        :param exclusive_maximum: Exclusive maximum value
        :type exclusive_maximum: Numeric
        """
        self._minimum = minimum
        self._exclusive_minimum = exclusive_minimum
        self._maximum = maximum
        self._exclusive_maximum = exclusive_maximum

    @abstractmethod
    def _parse(self, value):
        """Parse a numeric string into a Python numeric object (int or float).

        :param value: Value
        :type value: Any

        :return: Parsed numeric value
        :rtype: Numeric

        :raise: ValidationError
        """
        raise NotImplementedError()

    def parse(self, value):
        """Parse a numeric value.

        :param value: Value
        :type value: Any

        :return: Parsed numeric value
        :rtype: Numeric

        :raise: ValidationError
        """
        value = self._parse(value)

        if self._minimum is not None and value < self._minimum:
            raise ValueParserError(
                value,
                u"Value {0} is less than the minimum ({1})".format(
                    value, self._minimum
                ),
            )
        if self._exclusive_minimum is not None and value <= self._exclusive_minimum:
            raise ValueParserError(
                value,
                u"Value {0} is less or equal than the exclusive minimum ({1})".format(
                    value, self._exclusive_minimum
                ),
            )
        if self._maximum is not None and value > self._maximum:
            raise ValueParserError(
                value,
                u"Value {0} is greater than the maximum ({1})".format(
                    value, self._maximum
                ),
            )
        if self._exclusive_maximum is not None and value >= self._exclusive_maximum:
            raise ValueParserError(
                value,
                u"Value {0} is greater or equal than the exclusive maximum ({1})".format(
                    value, self._exclusive_maximum
                ),
            )

        return value


class IntegerParser(NumericParser):
    """Integer parser."""

    def _parse(self, value):
        """Parse an integer value.

        :param value: Value
        :type value: Any

        :return: Parsed integer
        :rtype: int

        :raise: ValidationError
        """
        try:
            return int(value)
        except ValueError as error:
            raise ValueParserError(value, six.u(str(error)), error)


class NumberParser(NumericParser):
    """Number parser."""

    def _parse(self, value):
        """Parse a float number.

        :param value: Value
        :type value: Any

        :return: Parsed float number
        :rtype: int

        :raise: ValidationError
        """
        try:
            return float(value)
        except ValueError as error:
            raise ValueParserError(value, six.u(str(error)), error)


class BooleanParser(ValueParser):
    """Boolean parser."""

    def parse(self, value):
        """Parse a boolean value.

        :param value: Value
        :type value: Any

        :return: Parsed boolean value
        :rtype: int

        :raise: ValidationError
        """
        if isinstance(value, bool):
            return value

        if is_string(value):
            if value == "false":
                return False

            if value == "true":
                return True

        raise ValueParserError(
            value, u"Value '{0}' must be boolean".format(encode(value))
        )


class StringParser(ValueParser):
    """String parser."""

    def parse(self, value):
        """Parse a string value.

        :param value: Value
        :type value: Any

        :return: Parsed string value
        :rtype: str

        :raise: ValidationError
        """
        if not is_string(value):
            raise ValueParserError(
                value, u"Value '{0}' must be a string".format(encode(value))
            )

        return value


class StringPatternParser(StringParser):
    """String parser using a regular expression pattern."""

    def __init__(self, pattern):
        """Initialize a new instance of StringPatternParser class.

        :param pattern: Regular expression which string's value must conform to
        :type pattern: RegEx
        """
        if not is_string(pattern):
            raise ValueError("Argument 'pattern' must be a string")

        self._pattern = pattern
        self._regex = re.compile(pattern) if pattern is not None else None

    def parse(self, value):
        """Parse a string value using the specified regular expression.

        :param value: Value
        :type value: Any

        :return: Parsed string value
        :rtype: int

        :raise: ValidationError
        """
        value = super(StringPatternParser, self).parse(value)

        if not self._regex.match(value):
            raise ValueParserError(
                value,
                u"String value '{0}' does not match regular expression {1}".format(
                    encode(value), self._pattern
                ),
            )

        return value


class EnumParser(StringParser):
    """Enum parser."""

    def __init__(self, items):
        """Initialize a new instance of EnumParser class.

        :param items: Enumeration items
        :type items: List[str]
        """
        self._items = items

    def parse(self, value):
        """Make sure that the value is a part of the enumeration and return it back.

        :param value: Value
        :type value: Any

        :return: Parsed string value
        :rtype: int

        :raise: ValidationError
        """
        value = super(EnumParser, self).parse(value)

        if value not in self._items:
            raise ValueParserError(
                value,
                u"Value '{0}' is not among {1}".format(encode(value), self._items),
            )

        return value


@six.add_metaclass(ABCMeta)
class FormatChecker(StringParser):
    """Base class for all parsers using jsonschema FormatChecker."""

    def __init__(self, json_schema_format):
        """Initialize a new instance of FormatParser class.

        :param json_schema_format: One of the jsonschema allowed string formats (color, date, date-time, etc.)
        :type json_schema_format: str
        """
        self._json_schema_format = json_schema_format
        self._format_checker = jsonschema.FormatChecker([json_schema_format])

    def _validate(self, value):
        """Check the value's format.

        :param value: Value
        :type value: Any

        :raise: ValidationError
        """
        try:
            self._format_checker.check(value, self._json_schema_format)
        except FormatError as error:
            raise ValueParserError(value, six.u(str(error)), error)

    def _parse(self, value):
        """Parse the value into an appropriate Python type.

        :param value: Value
        :type value: Any

        :return: Parsed value
        :rtype: Any

        :raise: ValidationError
        """
        return value

    def parse(self, value):
        """Parse the value according to the specified format.

        :param value: Value
        :type value: Any

        :return: Parsed value
        :rtype: Any

        :raise: ValidationError
        """
        self._validate(value)
        result = self._parse(value)

        return result


class URIParser(FormatChecker):
    """URI parser."""

    def __init__(self):
        """Initialize a new instance of URIParser class."""
        super(URIParser, self).__init__("uri")

    def _parse(self, value):
        """Parse the URI into a Python dictionary containing URI's subcomponents.

        :param value: Value
        :type value: Any

        :return: URI
        :rtype: str
        """
        return value


class URITemplateParser(StringParser):
    """URI template parser."""

    def parse(self, value):
        """Parse the URI into a Python dictionary containing URI's subcomponents.

        :param value: Value
        :type value: Any

        :return: URI template
        :rtype: URITemplate
        """
        URITemplate(value)

        return value


class URIReferenceParser(FormatChecker):
    """URI-reference parser."""

    def __init__(self):
        """Initialize a new instance of URIReferenceParser class."""
        super(URIReferenceParser, self).__init__("uri-reference")

    def _parse(self, value):
        """Parse the URI-reference into a Python dictionary containing URI's subcomponents.

        :param value: Value
        :type value: Any

        :return: URI-reference
        :rtype: str
        """
        return value


class DateParser(StringParser):
    """Date parser."""

    def parse(self, value):
        """Parse a date & time string into datetime object.

        :param value: Value
        :type value: Any

        :return: Parsed date object
        :rtype: datetime.datetime
        """
        try:
            return datetime_parser.parse(value)
        except Exception as exception:
            raise ValueParserError(
                value,
                u"Value '{0}' is not a correct date".format(encode(value)),
                exception,
            )


class DateTimeParser(StringParser):
    """Date & time parser."""

    def parse(self, value):
        """Parse a date & time string into datetime object.

        :param value: Value
        :type value: Any

        :return: Parsed date & time object
        :rtype: datetime.datetime
        """
        try:
            return datetime_parser.parse(value)
        except Exception as exception:
            raise ValueParserError(
                value,
                u"Value '{0}' is not a correct date & time value: "
                u"it does not comply with ISO 8601 date & time formatting rules".format(
                    encode(value)
                ),
                exception,
            )


class ArrayParser(ValueParser):
    """Array parser."""

    def __init__(self, item_parser, unique_items=False):
        """Initialize a new instance of ArrayParser class.

        :param item_parser: Parser used for parsing array items
        :type item_parser: ValueParser

        :param unique_items: Boolean value indicating whether array must contain only unique items
        :type unique_items: bool
        """
        self._item_parser = item_parser
        self._unique_items = unique_items
        self._logger = logging.getLogger(__name__)

    @property
    def item_parser(self):
        """Return the parser used for parsing array items.

        :return: Parser used for parsing array items
        :rtype: ValueParser
        """
        return self._item_parser

    def parse(self, value):
        """Parse the value into a list of parsed values.

        :param value: Value
        :type value: Any

        :return: List consisting of parsed items
        :rtype: List

        :raise: ValidationError
        """
        if not isinstance(value, list):
            raise ValueParserError(
                value, u"Value '{0}' must be a list".format(encode(value))
            )

        result = []
        seen = set()

        for item in value:
            item = self._item_parser.parse(item)

            if self._unique_items and item in seen:
                raise ValueParserError(
                    value, u"Item '{0}' is not unique".format(encode(item))
                )

            result.append(item)
            seen.add(item)

        return list(result)


class ObjectParser(ValueParser):
    """Object parser."""

    def __init__(self, properties_parser, properties_pattern=None):
        """Initialize a new instance of ObjectParser class.

        :param properties_parser: Properties parser
        :type properties_parser: ValueParser

        :param properties_pattern: Properties regex pattern
        :type properties_pattern: Optional[str]
        """
        self._properties_parser = properties_parser
        self._properties_regex = (
            re.compile(properties_pattern) if properties_pattern is not None else None
        )

    def parse(self, value):
        """Parse a JSON object into a Python dictionary.

        :param value: Value
        :type value: Any

        :return: Python dictionary containing parsed items
        :rtype: Dict

        :raise: ValidationError
        """
        if not isinstance(value, dict):
            raise ValueParserError(value, u"Value must be a dictionary")

        result = {}

        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueParserError(
                    value, u"Key '{0}' must be a string".format(encode(key))
                )

            if self._properties_regex and not self._properties_regex.match(key):
                raise ValueParserError(
                    value,
                    u"Key '{0}' does not match the pattern '{1}'".format(
                        encode(key), self._properties_regex
                    ),
                )

            item = self._properties_parser.parse(item)

            result[key] = item

        return result


class LocalizableStringParser(ObjectParser):
    """Parser for localizable strings represented as a dictionary with keys equal to language codes."""

    LANGUAGE_PATTERN = "^((?P<grandfathered>(en-GB-oed|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|i-mingo|i-navajo|i-pwn|i-tao|i-tay|i-tsu|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE)|(art-lojban|cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min|zh-min-nan|zh-xiang))|((?P<language>([A-Za-z]{2,3}(-(?P<extlang>[A-Za-z]{3}(-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})(-(?P<script>[A-Za-z]{4}))?(-(?P<region>[A-Za-z]{2}|[0-9]{3}))?(-(?P<variant>[A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(-(?P<extension>[0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+))*(-(?P<privateUse>x(-[A-Za-z0-9]{1,8})+))?)|(?P<privateUse2>x(-[A-Za-z0-9]{1,8})+))$"  # noqa: E501, pylint: disable=C0301

    def __init__(self):
        """Initialize a new instance of LocalizableStringValidator class."""
        super(LocalizableStringParser, self).__init__(
            StringParser(), self.LANGUAGE_PATTERN
        )


class TypeParser(ValueParser):
    """Parser used for checking type information and as an indication of nested types."""

    def __init__(self, _type):
        """Initialize a new instance of TypeParser class.

        :param _type: Type
        :type _type: Union[Type, str]
        """
        self._type = _type

    @property
    def type(self):
        """Return the type.

        "return: Type
        :rtype: Type
        """
        if is_string(self._type):
            self._type = locate(self._type)

            if self._type is None:
                raise ValueError(u"Unknown type {0}".format(self._type))

        return self._type

    def parse(self, value):
        """Check that the value has the correct type.

        :param value: Value
        :type value: Any

        :return: Value
        :rtype: Any

        :raise: ValidationError
        """
        if not isinstance(value, self._type):
            raise ValueParserError(
                value,
                u"Value '{0}' must be an instance of '{1}'".format(
                    encode(value), self._type
                ),
            )

        return value


def find_parser(parent_parser, child_parser_type):
    """Find a child parser with a specified type in the parent parser.

    This function is used for finding nested types.

    :param parent_parser: Parent parser
    :type parent_parser: ValueParser

    :param child_parser_type: Child parser's type
    :type child_parser_type: Type

    :return: List of 2-tuples (parent parser, child parser)
    :rtype: List[Optional[ValueParser], ValueParser]
    """
    candidates = []

    def _find_parser(_parent_parser, _current_parser):
        if isinstance(_current_parser, child_parser_type):
            candidates.append((_parent_parser, _current_parser))
        elif isinstance(_current_parser, AnyOfParser):
            for inner_parser in _current_parser.inner_parsers:
                _find_parser(_parent_parser, inner_parser)
        elif isinstance(_current_parser, ArrayParser):
            _find_parser(_current_parser, _current_parser.item_parser)

    _find_parser(None, parent_parser)

    return candidates

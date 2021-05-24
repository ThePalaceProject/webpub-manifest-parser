import io
import json
import logging
from abc import ABCMeta, abstractmethod
from io import StringIO

import requests  # noqa: I201
import six  # noqa: I201

from webpub_manifest_parser.core.analyzer import AnalyzerContext


class ManifestParserResult(AnalyzerContext):
    """Class containing the result of the semantic analysis: root AST node and a list of found errors."""

    def __init__(self, root):
        """Initialize a new instance of DocumentParserResult class.

        :param root: Root AST node
        :type root: webpub_manifest_parser.core.ast.Node
        """
        super(ManifestParserResult, self).__init__()

        self._root = root

    @property
    def root(self):
        """Return the root AST node.

        :return: Root AST node
        :rtype: webpub_manifest_parser.core.ast.Manifestlike
        """
        return self._root


class ManifestParser(object):
    """Base class for RWPM-compatible parsers."""

    def __init__(self, syntax_analyzer, semantic_analyzer):
        """Initialize a new instance of ManifestParser class.

        :param syntax_analyzer: Syntax analyzer
        :type syntax_analyzer: syntax.SyntaxAnalyzer

        :param semantic_analyzer: Semantic analyser
        :type semantic_analyzer: semantic.SemanticAnalyzer
        """
        self._syntax_analyzer = syntax_analyzer
        self._semantic_analyzer = semantic_analyzer

        self._logger = logging.getLogger(__name__)

    def _parse(self, manifest_json):
        """Parse the JSON object containing an RWPM-compatible manifest.

        :param manifest_json: JSON object containing an RWPM-compatible manifest
        :type manifest_json: Dict

        :return: Parser result containing an AST object and a list of syntax and semantic errors
        :rtype: ManifestParserResult
        """
        manifest = self._syntax_analyzer.analyze(manifest_json)
        result = ManifestParserResult(manifest)

        manifest.accept(self._semantic_analyzer)

        result.errors.extend(self._syntax_analyzer.context.errors)
        result.errors.extend(self._semantic_analyzer.context.errors)

        return result

    def parse_file(self, input_file_path, encoding="utf-8"):
        """Parse the input file and return a validated AST object.

        :param input_file_path: Full path to the file containing RWPM-compatible document
        :type input_file_path: str

        :param encoding: Input file's encoding
        :type encoding: str

        :return: Parser result
        :rtype: ManifestParserResult
        """
        with io.open(input_file_path, "r", encoding=encoding) as input_file:
            manifest_json = self.get_manifest_json(input_file)

            return self._parse(manifest_json)

    def parse_stream(self, input_stream):
        """Parse the input file and return the result: root AST object and a list of errors.

        :param input_stream: Full path to the file containing RWPM-compatible document
        :type input_stream: six.StringIO

        :return: Parser result
        :rtype: ManifestParserResult
        """
        manifest_json = self.get_manifest_json(input_stream)

        return self._parse(manifest_json)

    def parse_url(
        self, url, encoding="utf-8", params=None, auth=None, proxies=None
    ):  # pylint: disable=too-many-arguments
        """Fetch the content pointed by the URL, parse it and return the result: root AST object and a list of errors.

        :param url: URL pointing to the RWPM-compatible document
        :type url: str

        :param encoding: Input file's encoding
        :type encoding: str

        :param params: Dictionary containing query parameters
        :type params: Dict

        :param auth: Authentication information
        :type auth: requests.auth.AuthBase

        :param proxies: Dictionary containing proxy information
        :type proxies: Dict

        :return: Parser result
        :rtype: ManifestParserResult
        """
        response = requests.get(url, params=params, auth=auth, proxies=proxies)
        input_stream = StringIO(six.text_type(response.content, encoding))
        manifest_json = self.get_manifest_json(input_stream)

        return self._parse(manifest_json)

    def parse_json(self, manifest_json):
        """Parse the JSON document with an RWPM-compatible manifest and return the result.

        :param manifest_json: JSON document with an RWPM-compatible manifest
        :type manifest_json: Dict

        :return: Parser result containing the root AST object and a list of errors
        :rtype: ManifestParserResult
        """
        return self._parse(manifest_json)

    @staticmethod
    def get_manifest_json(input_stream):
        """Parse the input stream into a JSON document containing an RWPM-compatible manifest.

        :param input_stream: Input stream containing JSON document with an RWPM-compatible manifest
        :type input_stream: Union[six.StringIO, six.BinaryIO]

        :return: JSON document containing an RWPM-compatible manifest
        :rtype: Dict
        """
        logging.debug("Started parsing input stream into a JSON document")

        input_stream_content = input_stream.read()
        input_stream_content = input_stream_content.strip()
        manifest_json = json.loads(input_stream_content)

        logging.debug("Finished parsing input stream into a JSON document")

        return manifest_json


@six.add_metaclass(ABCMeta)
class ManifestParserFactory(object):
    """Base class for factories creating parsers for particular RWPM-compatible standards (for example, OPDS 2.0)."""

    @abstractmethod
    def create(self):
        """Create a new Parser instance.

        :return: Parser instance
        :rtype: ManifestParser
        """
        raise NotImplementedError()

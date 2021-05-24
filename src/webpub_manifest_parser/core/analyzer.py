from abc import ABCMeta
from contextlib import contextmanager

import six

from webpub_manifest_parser.errors import BaseError


class BaseAnalyzerError(BaseError):
    """Exception raised in the case of any (syntax, semantic) errors thrown during parsing."""

    def __init__(self, node, node_property, message=None, inner_exception=None):
        """Initialize a new instance of BaseSemanticError class.

        :param node: AST node where the error was found
        :type node: webpub_manifest_parser.core.ast.Node

        :param node_property: AST node's property associated with the error
        :type node_property: Optional[webpub_manifest_parser.core.properties.Property]

        :param message: String containing description of the error occurred
        :type message: Optional[str]

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        super(BaseAnalyzerError, self).__init__(message, inner_exception)

        self._node = node
        self._node_property = node_property

    @property
    def node(self):
        """Return the AST node where the error was found.

        :return: Node where the error was found
        :rtype: webpub_manifest_parser.core.ast.Node
        """
        return self._node

    @property
    def node_property(self):
        """Return the AST node's property associated with the error.

        :return: AST node's property associated with the error
        :rtype: webpub_manifest_parser.core.properties.Property
        """
        return self._node_property


class AnalyzerContext(object):
    """Class containing the current analyzer's context."""

    def __init__(self):
        """Initialize a new instance of AnalyzerContext class."""
        self._errors = []

    @property
    def errors(self):
        """Return the list of errors.

        :return: List of errors
        :rtype: List[BaseAnalyzerError]
        """
        return self._errors

    def reset(self):
        """Reset the current context."""
        self._errors = []


@six.add_metaclass(ABCMeta)
class BaseAnalyzer(object):
    """Base class for all analyzers (syntax and semantic)."""

    def __init__(self):
        """Initialize a new instance of BaseAnalyzer class."""
        self._context = AnalyzerContext()

    @property
    def context(self):
        """Return the current analyzer's context.

        :return: Current analyzer's context
        :rtype: AnalyzerContext
        """
        return self._context

    @contextmanager
    def _record_errors(self):
        """Record semantic errors in the current context.

        NOTE: This is a very naive implementation of error recovery.
        """
        try:
            yield
        except BaseAnalyzerError as error:
            self.context.errors.append(error)

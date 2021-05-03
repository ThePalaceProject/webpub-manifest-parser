import six


class BaseError(Exception):
    """Base class for all errors."""

    def __init__(self, message=None, inner_exception=None):
        """Initialize a new instance of BaseError class.

        :param message: String containing description of the error occurred
        :type message: Optional[str]

        :param inner_exception: (Optional) Inner exception
        :type inner_exception: Optional[Exception]
        """
        if inner_exception and not message:
            message = inner_exception.error_message

        super(BaseError, self).__init__(message)

        self._inner_exception = inner_exception

    @property
    def inner_exception(self):
        """Return the inner exception.

        :return: Inner exception
        :rtype: Exception
        """
        return self._inner_exception

    @property
    def error_message(self):
        """Return the description of the error.

        :return: Description of the error
        :rtype: str
        """
        return six.text_type(str(self))

    def __eq__(self, other):
        """Compare two BaseError objects.

        :param other: BaseError object
        :type other: BaseError

        :return: Boolean value indicating whether two items are equal
        :rtype: bool
        """
        if not isinstance(other, BaseError):
            return False

        return str(self) == str(other)

    def __repr__(self):
        """Return error's string representation.

        :return: Error's string representation
        :rtype: str
        """
        return u"<BaseError(message={0}, inner_exception={1})>".format(
            self.error_message, self.inner_exception
        )

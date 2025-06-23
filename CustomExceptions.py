class RequestFailedException(Exception):
    """Raised when a request to a URL fails."""
    pass

class RegexPatternNotFoundException(Exception):
    """Exception raised when a regex pattern is not found."""
    pass

class SoupNotFoundException(Exception):
    """Exception raised when bs4 html pattern not found"""
    pass


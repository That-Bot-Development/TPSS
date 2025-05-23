class DurationParseError(Exception):
    """Thrown when the specified duration cannot be parsed from user input."""
    pass

class DurationOutOfBoundsError(Exception):
    """Thrown when the specified duration is out of bounds for the given context."""
    pass

class NotFoundError(Exception):
    """Thrown when the requested data cannot be found from the source."""
    pass
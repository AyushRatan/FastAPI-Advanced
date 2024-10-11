


class BooklyException(Exception):
    """This is the base class for all bookly errors """
    pass

class InvalidToken(BooklyException):
    """USer has provided an invalid or an expired token"""
    pass
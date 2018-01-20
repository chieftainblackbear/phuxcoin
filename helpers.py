"""
  helper functions
"""


def filterbyvalue(seq, value):  # TODO: not working yet
    """Filters by value.
    """
    for el in seq:
        if el.attribute == value:
            yield el

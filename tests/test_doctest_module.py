import doctest

import statblk


def test_embedded_doctests():
    result = doctest.testmod(statblk, optionflags=doctest.NORMALIZE_WHITESPACE)
    assert result.failed == 0, f"doctest failures: {result.failed}"

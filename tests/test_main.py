import re

from klavicle import __version__


def test_version():
    """Test version format."""
    assert re.match(r"^\d+\.\d+\.\d+$", __version__)

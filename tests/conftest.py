import pytest
from pathlib import Path

def pytest_addoption(parser):
    """ Add cmd line options to pytest
    """
    parser.addoption("--uno_server_url", action='store', default='http://s1:3000', help='Unoconv server url.')

    parser.addoption("--keep_files", action='store', default=True, help='Keep the directories and files created by testing.')

@pytest.fixture
def uno_server_url(request):
    """URL to a Unoconv Server.
    """
    return request.config.getoption("--uno_server_url")

@pytest.fixture
def keep_files(request):
    """Booealn cmd line option to keep files from testing around.
    """
    return request.config.getoption("--keep_files")

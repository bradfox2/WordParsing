import pytest

def pytest_addoption(parser):
    parser.addoption("--uno_server_url", action='store', default='http://s1:3000', help='Unoconv server url.')

@pytest.fixture
def uno_server_url(request):
    """URL to a Unoconv Server.
    """
    return request.config.getoption("--uno_server_url")
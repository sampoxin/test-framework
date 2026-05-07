import pytest

from api.client import ApiClient
from config.settings import BASE_URL,TIMEOUT


@pytest.fixture(scope="session")
def client():
    client = ApiClient(BASE_URL, TIMEOUT)
    yield client
    client.stats()


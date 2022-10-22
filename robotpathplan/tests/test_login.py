import pytest
from robotpathplan import app

@pytest.fixture
def client():
    return app.test_client()

def test_home(client):
    resp = client.get('/login')
    assert resp.status_code == 200
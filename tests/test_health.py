from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.json()
    assert data['status'] == 'ok'

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_and_lookup():
    response = client.post("/api/v1/urls", json={"original_url": "https://example.com"})
    assert response.status_code == 201
    data = response.json()
    assert data["short_code"]
    lookup = client.get(f"/api/v1/urls/{data['short_code']}")
    assert lookup.status_code == 200
    assert lookup.json()["original_url"] == "https://example.com/"

def test_custom_alias():
    response = client.post("/api/v1/urls", json={
        "original_url": "https://example.com/product",
        "custom_alias": "product-demo"
    })
    assert response.status_code == 201
    assert response.json()["short_code"] == "product-demo"

def test_duplicate_alias():
    alias = "duplicate-demo"
    first = client.post("/api/v1/urls", json={"original_url": "https://example.com", "custom_alias": alias})
    assert first.status_code == 201
    second = client.post("/api/v1/urls", json={"original_url": "https://example.org", "custom_alias": alias})
    assert second.status_code == 409

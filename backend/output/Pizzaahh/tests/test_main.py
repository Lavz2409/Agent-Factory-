import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

@pytest.fixture
def user_data():
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123"
    }

@pytest.fixture
def order_data():
    return {
        "items": [{"menuItemId": "123", "quantity": 2}],
        "userId": "user123"
    }

@pytest.fixture
def menu_item():
    return {
        "name": "Pizza",
        "price": 10.99,
        "description": "Delicious cheese pizza"
    }

def test_register_user(user_data):
    response = client.post("/api/users/register", json=user_data)
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_user(user_data):
    client.post("/api/users/register", json=user_data)  # Register first
    response = client.post("/api/users/login", json={"email": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200
    assert "token" in response.json()

def test_get_user_orders():
    response = client.get("/api/users/orders?userId=user123")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_menu_item(menu_item):
    response = client.post("/api/admin/menu", json=menu_item)
    assert response.status_code == 200
    assert response.json()["name"] == menu_item["name"]

def test_get_admin_orders():
    response = client.get("/api/admin/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_order_status():
    response = client.put("/api/admin/orders/123?status=completed")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_create_order(order_data):
    response = client.post("/api/orders", json=order_data)
    assert response.status_code == 200
    assert "confirmation" in response.json()
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def jwt_token():
    # Assuming a function to get a JWT token for testing
    response = client.post("/api/users/register", json={
        "username": "testuser",
        "password": "testpass",
        "email": "test@example.com"
    })
    return response.json().get("token")

def test_user_registration():
    response = client.post("/api/users/register", json={
        "username": "newuser",
        "password": "newpass",
        "email": "new@example.com"
    })
    assert response.status_code == 201
    assert "token" in response.json()

def test_user_login():
    response = client.post("/api/users/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    assert "token" in response.json()

def test_get_user_orders(jwt_token):
    response = client.get("/api/users/orders", headers={"Authorization": f"Bearer {jwt_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_post_order(jwt_token):
    response = client.post("/api/orders", headers={"Authorization": f"Bearer {jwt_token}"}, json={
        "orderDetails": {"item": "test item", "quantity": 1}
    })
    assert response.status_code == 201
    assert "confirmation" in response.json()

def test_get_admin_orders(jwt_token):
    response = client.get("/api/admin/orders", headers={"Authorization": f"Bearer {jwt_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_order_status(jwt_token):
    # Assuming an order ID is available for testing
    order_id = "some_order_id"
    response = client.put(f"/api/admin/orders/{order_id}", headers={"Authorization": f"Bearer {jwt_token}"}, json={
        "status": "shipped"
    })
    assert response.status_code == 200
    assert response.json().get("status") == "shipped"

def test_payment_checkout(jwt_token):
    response = client.post("/api/payment/checkout", headers={"Authorization": f"Bearer {jwt_token}"}, json={
        "paymentDetails": {"amount": 100, "method": "credit_card"}
    })
    assert response.status_code == 200
    assert "confirmation" in response.json()
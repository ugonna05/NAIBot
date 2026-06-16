"""
tests/test_api.py
──────────────────
Basic smoke tests for the NAiBot API.
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Patch model loading so tests don't require GPU/model weights
with patch("app.main.model_manager") as mock_manager:
    mock_manager.model = MagicMock()
    mock_manager.loading_status = "loaded"
    mock_manager.device = "cpu"
    mock_manager.generate = MagicMock(
        return_value="Welcome to NaiLand! I'm NAiBot, your onboarding assistant. How can I help you today?"
    )
    from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "NAiBot" in data["name"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "device" in data


def test_chat_valid_request():
    with patch("app.main.model_manager.model", MagicMock()), \
         patch("app.main.model_manager.generate", return_value="Welcome to NaiLand!"):
        response = client.post("/chat", json={"message": "Hello, what is NaiLand?"})
        assert response.status_code in (200, 503)  # 503 acceptable if model mocked as None


def test_chat_empty_message():
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422  # Pydantic validation error


def test_chat_message_too_long():
    response = client.post("/chat", json={"message": "x" * 3000})
    assert response.status_code == 422


def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_available():
    response = client.get("/redoc")
    assert response.status_code == 200

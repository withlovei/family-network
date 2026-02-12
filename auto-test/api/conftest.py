"""Pytest fixtures for API tests."""
import os

import httpx
import pytest

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")


@pytest.fixture
def base_url() -> str:
    return API_BASE_URL.rstrip("/")


@pytest.fixture
def client(base_url: str) -> httpx.Client:
    return httpx.Client(base_url=base_url, timeout=10.0)

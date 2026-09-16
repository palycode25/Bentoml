"""
Tests unitaires de l'API de prédiction d'admission.
Le service doit être démarré (docker run ou bentoml serve) avant de lancer ces tests.
"""
import time

import pytest
import requests

BASE_URL = "http://localhost:3000"

VALID_CREDENTIALS = {"username": "user123", "password": "password123"}
INVALID_CREDENTIALS = {"username": "wrong", "password": "wrong"}

VALID_INPUT = {
    "gre_score": 320,
    "toefl_score": 110,
    "university_rating": 4,
    "sop": 4.0,
    "lor": 4.5,
    "cgpa": 8.9,
    "research": 1,
}


@pytest.fixture(scope="module", autouse=True)
def wait_for_service():
    """Attend que le service soit prêt avant de lancer les tests."""
    for _ in range(30):
        try:
            requests.post(f"{BASE_URL}/login", json={"credentials": VALID_CREDENTIALS}, timeout=2)
            return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    pytest.fail("Le service n'a pas démarré à temps sur " + BASE_URL)


@pytest.fixture(scope="module")
def auth_token():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"credentials": VALID_CREDENTIALS},
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


# ---------- Tests de l'API de connexion (/login) ----------

def test_login_success():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"credentials": VALID_CREDENTIALS},
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_failure_wrong_credentials():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"credentials": INVALID_CREDENTIALS},
    )
    assert response.status_code == 401


# ---------- Tests de l'authentification JWT ----------

def test_predict_fails_without_token():
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"input_data": VALID_INPUT},
    )
    assert response.status_code == 401


def test_predict_fails_with_invalid_token():
    headers = {
        "Authorization": "Bearer invalid.token.value",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{BASE_URL}/predict",
        headers=headers,
        json={"input_data": VALID_INPUT},
    )
    assert response.status_code == 401


def test_predict_fails_with_malformed_header():
    headers = {
        "Authorization": "NotBearer sometoken",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{BASE_URL}/predict",
        headers=headers,
        json={"input_data": VALID_INPUT},
    )
    assert response.status_code == 401


def test_predict_succeeds_with_valid_token(auth_headers):
    response = requests.post(
        f"{BASE_URL}/predict",
        headers=auth_headers,
        json={"input_data": VALID_INPUT},
    )
    assert response.status_code == 200


# ---------- Tests de l'API de prédiction (/predict) ----------

def test_predict_returns_valid_prediction(auth_headers):
    response = requests.post(
        f"{BASE_URL}/predict",
        headers=auth_headers,
        json={"input_data": VALID_INPUT},
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], list)
    assert len(data["prediction"]) == 1
    assert isinstance(data["prediction"][0], float)
    assert 0.0 <= data["prediction"][0] <= 1.0


def test_predict_fails_with_invalid_input_data(auth_headers):
    invalid_input = {"gre_score": "not_a_number"}
    response = requests.post(
        f"{BASE_URL}/predict",
        headers=auth_headers,
        json={"input_data": invalid_input},
    )
    assert response.status_code in (400, 422)

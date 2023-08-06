import uuid

import requests

from rest_framework import status


def test_user_create_with_invalid_data_returns_400_and_error_message(
    api_url, admin_token
):
    data = {"username": "", "password": ""}
    r = requests.post(
        f"{api_url}/users/",
        json=data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in r.json()
    assert "Username is required" in r.json()["username"][0]


def test_user_create_with_duplicate_username_returns_400_and_error_message(
    api_url, admin_token
):
    data = {"username": "admin", "password": "admin"}
    r = requests.post(
        f"{api_url}/users/",
        json=data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username admin already exists" in r.json()["message"]


def test_user_create_happy_path_returns_201_and_user_id(api_url, admin_token):
    data = {"username": f"creator-{uuid.uuid4().hex[:6]}", "password": "creator"}
    r = requests.post(
        f"{api_url}/users/",
        json=data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["id"] is not None

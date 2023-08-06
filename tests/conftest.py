import uuid

import pytest
import requests

from common import config
import wait_for_postgres


@pytest.fixture(scope="session")
def api_url():
    return config.get_api_url()


@pytest.fixture(scope="session")
def admin_token(api_url):
    r = requests.post(
        f"{api_url}/token/", json={"username": "admin", "password": "admin"}
    )
    return r.json()["access"]


def _new_random_creator_token(api_url, admin_token) -> str:
    creator_username = f"creator-{uuid.uuid4().hex[:6]}"
    requests.post(
        f"{api_url}/users/",
        json={"username": creator_username, "password": "creator"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    r = requests.post(
        f"{api_url}/token/",
        json={"username": creator_username, "password": "creator"},
    )
    return r.json()["access"]


@pytest.fixture(scope="function")
def new_random_creator_token(api_url, admin_token) -> str:
    return _new_random_creator_token(api_url, admin_token)


@pytest.fixture(scope="session")
def new_random_creator_token_factory(api_url, admin_token):
    def factory():
        return _new_random_creator_token(api_url, admin_token)

    return factory


@pytest.fixture(autouse=True, scope="session")
def wait_for_postgres_to_come_up():
    wait_for_postgres.wait_for_postgres_to_come_up()

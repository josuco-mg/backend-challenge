import requests
import time

from rest_framework import status


def test_ecg_create_happy_path_returns_201_and_ecg_id(
    api_url, new_random_creator_token
):
    data = {
        "lead_results": [
            {
                "lead": "I",
                "signal": [1, -1, 1, -1],
            },
        ],
    }
    r = requests.post(
        f"{api_url}/ecgs/",
        json=data,
        headers={"Authorization": f"Bearer {new_random_creator_token}"},
    )
    assert r.status_code == status.HTTP_201_CREATED
    assert r.json()["id"] is not None


def test_ecg_create_with_invalid_data_returns_400_and_error_message(
    api_url, new_random_creator_token
):
    data = {"lead_results": []}
    r = requests.post(
        f"{api_url}/ecgs/",
        json=data,
        headers={"Authorization": f"Bearer {new_random_creator_token}"},
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "lead_results" in r.json()
    assert "No lead results" in r.json()["lead_results"][0]


def test_ecg_stats_happy_path_returns_200_and_ecg_stats(
    api_url, new_random_creator_token
):
    data = {
        "lead_results": [
            {
                "lead": "I",
                "signal": [1, -1, 1, -1],
            },
            {
                "lead": "II",
                "signal": [1, 1, 1, -1],
            },
        ],
    }
    r = requests.post(
        f"{api_url}/ecgs/",
        json=data,
        headers={"Authorization": f"Bearer {new_random_creator_token}"},
    )
    time.sleep(0.5)  # wait for the ECG to be processed in celery
    r = requests.get(
        f"{api_url}/ecgs/{r.json()['id']}/stats/",
        headers={"Authorization": f"Bearer {new_random_creator_token}"},
    )
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {
        "lead_results": [
            {
                "lead": "I",
                "zero_crossing_count": 3,
            },
            {
                "lead": "II",
                "zero_crossing_count": 1,
            },
        ],
    }


def test_ecg_stats_with_other_user_ecg_id_returns_404(
    api_url, new_random_creator_token_factory
):
    creator_token = new_random_creator_token_factory()
    other_creator_token = new_random_creator_token_factory()
    data = {
        "lead_results": [
            {
                "lead": "I",
                "signal": [1, -1, 1, -1],
            },
        ],
    }
    r = requests.post(
        f"{api_url}/ecgs/",
        json=data,
        headers={"Authorization": f"Bearer {creator_token}"},
    )
    r = requests.get(
        f"{api_url}/ecgs/{r.json()['id']}/stats/",
        headers={"Authorization": f"Bearer {other_creator_token}"},
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_ecg_stats_with_admin_user_returns_forbidden_response(
    api_url, admin_token, new_random_creator_token
):
    data = {
        "lead_results": [
            {
                "lead": "I",
                "signal": [1, -1, 1, -1],
            },
        ],
    }
    r = requests.post(
        f"{api_url}/ecgs/",
        json=data,
        headers={"Authorization": f"Bearer {new_random_creator_token}"},
    )
    r = requests.get(
        f"{api_url}/ecgs/{r.json()['id']}/stats/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == status.HTTP_403_FORBIDDEN

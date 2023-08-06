import pytest
import wait_for_postgres

@pytest.fixture(autouse=True, scope="session")
def wait_for_postgres_to_come_up():
    wait_for_postgres.wait_for_postgres_to_come_up()

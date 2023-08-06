import pytest
from account.adapters import repository
from account.services import services
from account.services import unit_of_work
from web.accounts import models as django_models


@pytest.mark.django_db(transaction=True)
def test_create_regular_user():
    assert not django_models.User.objects.exists()
    user_id = services.create_user(
        "regular", "password", False, unit_of_work.DjangoUserUnitOfWork()
    )
    assert django_models.User.objects.count() == 1
    django_user = django_models.User.objects.first()
    assert django_user.username == "regular"
    assert not django_user.is_admin
    assert user_id == django_user.id


@pytest.mark.django_db(transaction=True)
def test_create_admin_user():
    assert not django_models.User.objects.exists()
    user_id = services.create_user(
        "admin", "password", True, unit_of_work.DjangoUserUnitOfWork()
    )
    assert django_models.User.objects.count() == 1
    django_user = django_models.User.objects.first()
    assert django_user.username == "admin"
    assert django_user.is_admin
    assert user_id == django_user.id


@pytest.mark.django_db(transaction=True)
def test_cannot_create_user_if_username_already_exists():
    django_models.User.objects.create_user(
        username="existing", password="password", is_admin=False
    )
    with pytest.raises(services.UsernameAlreadyExists):
        services.create_user(
            "existing", "password", False, unit_of_work.DjangoUserUnitOfWork()
        )


@pytest.mark.django_db
def test_get_user_by_username():
    django_user = django_models.User.objects.create_user(
        username="existing", password="password", is_admin=False
    )
    user = services.get_user_by_username(
        "existing", repository.DjangoUserRepository()
    )
    assert user.id == django_user.id
    assert user.username == "existing"
    assert user.password is None
    assert user.is_admin == False

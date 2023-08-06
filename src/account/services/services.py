from account.adapters import repository
from account.domain import model
from account.services import unit_of_work


class UsernameAlreadyExists(Exception):
    pass


def create_user(
    username: str,
    password: str,
    is_admin: bool,
    uow: unit_of_work.AbstractUserUnitOfWork,
) -> int:
    with uow:
        if uow.users.exists_by_username(username):
            raise UsernameAlreadyExists(f"Username {username} already exists")
        user = uow.users.create(
            model.User(username=username, password=password, is_admin=is_admin)
        )
        uow.commit()
    return user.id


def get_user_by_username(
    username: str,
    users: repository.AbstractUserRepository = repository.DjangoUserRepository(),
) -> model.User:
    return users.get_by_username(username=username)

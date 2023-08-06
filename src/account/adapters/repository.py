import abc

from account.domain import model as domain_model
from web.accounts import models as django_models


class AbstractUserRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, user: domain_model.User) -> domain_model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_username(self, username: str) -> domain_model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def exists_by_username(self, username: str) -> bool:
        raise NotImplementedError


class DjangoUserRepository(AbstractUserRepository):
    def create(self, user: domain_model.User) -> domain_model.User:
        return django_models.User.objects.create_user(
            username=user.username,
            password=user.password,
            is_admin=user.is_admin,
        ).to_domain()

    def get_by_username(self, username: str) -> domain_model.User:
        return django_models.User.objects.get(username=username).to_domain()

    def exists_by_username(self, username: str) -> bool:
        return django_models.User.objects.filter(username=username).exists()

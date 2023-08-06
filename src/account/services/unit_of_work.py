from __future__ import annotations
import abc

from django.db import transaction

from account.adapters import repository


class AbstractUserUnitOfWork(abc.ABC):
    users: repository.AbstractUserRepository

    def __enter__(self) -> AbstractUserUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class DjangoUserUnitOfWork(AbstractUserUnitOfWork):
    def __enter__(self):
        self.users = repository.DjangoUserRepository()
        transaction.set_autocommit(False)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        transaction.set_autocommit(True)

    def commit(self):
        transaction.commit()

    def rollback(self):
        transaction.rollback()

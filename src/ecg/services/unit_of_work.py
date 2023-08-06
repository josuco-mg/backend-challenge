from __future__ import annotations
import abc

from django.db import transaction

from ecg.adapters import repository


class AbstractECGUnitOfWork(abc.ABC):
    ecgs: repository.AbstractECGRepository

    def __enter__(self) -> AbstractECGUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class DjangoECGUnitOfWork(AbstractECGUnitOfWork):
    def __enter__(self):
        self.ecgs = repository.DjangoECGRepository()
        transaction.set_autocommit(False)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        transaction.set_autocommit(True)

    def commit(self):
        transaction.commit()

    def rollback(self):
        transaction.rollback()

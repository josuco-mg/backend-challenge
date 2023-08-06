from typing import Any, Dict, List, Optional

from account.domain import model as account_model
from ecg.adapters import repository
from ecg.domain import model as ecg_model
from ecg.services import unit_of_work


class InvalidCreator(Exception):
    pass


def create_ecg(
    creator: account_model.User,
    lead_results: List[Dict[Any, Any]],
    uow: unit_of_work.AbstractECGUnitOfWork,
) -> int:
    if creator.is_admin:
        raise InvalidCreator("Admins cannot create ECGs")

    with uow:
        ecg = uow.ecgs.create(
            ecg_model.ECG(creator=creator, lead_results=lead_results)
        )
        uow.commit()
    return ecg.id


def get_ecg_by_id(
    id: int, ecgs: repository.AbstractECGRepository
) -> Optional[ecg_model.ECG]:
    return ecgs.get_by_id(id=id)


def process_ecg(ecg: ecg_model.ECG, uow: unit_of_work.AbstractECGUnitOfWork):
    with uow:
        uow.ecgs.process(ecg=ecg)
        uow.commit()

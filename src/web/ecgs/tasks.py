from celery import shared_task

from ecg.adapters import repository
from ecg.services import services as ecg_services
from ecg.services import unit_of_work


@shared_task
def task_process_ecg(ecg_id: int):
    ecg = ecg_services.get_ecg_by_id(id=ecg_id, ecgs=repository.DjangoECGRepository())
    ecg_services.process_ecg(ecg=ecg, uow=unit_of_work.DjangoECGUnitOfWork())

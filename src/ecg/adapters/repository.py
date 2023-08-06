import abc
from typing import Optional

from ecg.domain import model as domain_model
from web.ecgs import models as django_models


class AbstractECGRepository(abc.ABC):
    @abc.abstractmethod
    def create(self, ecg: domain_model.ECG) -> domain_model.ECG:
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, id: int) -> domain_model.ECG:
        raise NotImplementedError

    @abc.abstractmethod
    def process(self, ecg: domain_model.ECG):
        raise NotImplementedError


class DjangoECGRepository(AbstractECGRepository):
    def create(self, ecg: domain_model.ECG) -> domain_model.ECG:
        django_ecg = django_models.ECG.objects.create(creator_id=ecg.creator.id)
        django_models.ECGLeadResult.objects.bulk_create(
            django_models.ECGLeadResult(
                ecg_id=django_ecg.id,
                lead=lead_result.lead,
                signal=lead_result.signal,
                num_samples=lead_result.num_samples,
            )
            for lead_result in ecg.lead_results
        )
        return self.get_by_id(django_ecg.id)

    def get_by_id(self, id: int) -> Optional[domain_model.ECG]:
        try:
            return (
                django_models.ECG.objects.filter(id=id)
                .select_related("creator")
                .prefetch_related("ecgleadresult_set")
                .get()
                .to_domain()
            )
        except django_models.ECG.DoesNotExist:
            return

    def process(self, ecg: domain_model.ECG):
        ecg.process()
        django_models.ECGLeadResult.objects.bulk_update(
            [
                django_models.ECGLeadResult(
                    id=lead_result.id,
                    zero_crossing_count=lead_result.zero_crossing_count,
                )
                for lead_result in ecg.lead_results
            ],
            fields=["zero_crossing_count"],
        )

from django.db import models
from django.contrib.postgres.fields import ArrayField

from ecg.domain import model as domain_model


class ECG(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey("accounts.User", on_delete=models.CASCADE)

    def to_domain(self) -> domain_model.ECG:
        return domain_model.ECG(
            id=self.id,
            created=self.created,
            creator=self.creator.to_domain(),
            lead_results=[
                lead_result.to_domain()
                for lead_result in self.ecgleadresult_set.all()
            ],
        )


class ECGLeadResult(models.Model):
    ecg = models.ForeignKey(ECG, on_delete=models.CASCADE)
    lead = models.CharField(choices=[(e.value, e.name) for e in domain_model.ECGLead])
    signal = ArrayField(models.IntegerField())
    num_samples = models.IntegerField(blank=True, null=True)
    zero_crossing_count = models.IntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["ecg", "lead"], name="unique_ecg_lead"),
        ]

    def to_domain(self) -> domain_model.ECGLeadResult:
        return domain_model.ECGLeadResult(
            id=self.id,
            lead=self.lead,
            signal=self.signal,
            num_samples=self.num_samples,
            zero_crossing_count=self.zero_crossing_count,
        )

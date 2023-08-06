import pytest
import pydantic
from ecg.domain import model as ecg_model
from ecg.adapters import repository
from ecg.services import services
from ecg.services import unit_of_work
from web.accounts import models as django_account_models
from web.ecgs import models as django_ecg_models


@pytest.mark.django_db(transaction=True)
def test_cannot_create_ecg_with_an_admin_user():
    user = django_account_models.User.objects.create_user(
        "username", "password", True
    ).to_domain()
    lead_results = [{"lead": "I", "signal": [1, -1, 1]}]
    with pytest.raises(services.InvalidCreator):
        services.create_ecg(user, lead_results, unit_of_work.DjangoECGUnitOfWork())
    assert not django_ecg_models.ECG.objects.exists()
    assert not django_ecg_models.ECGLeadResult.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_cannot_create_ecg_with_invalid_lead_results_data():
    user = django_account_models.User.objects.create_user(
        "username", "password", False
    ).to_domain()
    lead_results = [
        {"lead": "I", "signal": [1, -1, 1]},
        {"lead": "I", "signal": [1, -1, 1]},
    ]
    with pytest.raises(pydantic.ValidationError):
        services.create_ecg(user, lead_results, unit_of_work.DjangoECGUnitOfWork())
    assert not django_ecg_models.ECG.objects.exists()
    assert not django_ecg_models.ECGLeadResult.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_cannot_create_ecg_with_empty_lead_results_data():
    user = django_account_models.User.objects.create_user(
        "username", "password", False
    ).to_domain()
    lead_results = []
    with pytest.raises(pydantic.ValidationError):
        services.create_ecg(user, lead_results, unit_of_work.DjangoECGUnitOfWork())
    assert not django_ecg_models.ECG.objects.exists()
    assert not django_ecg_models.ECGLeadResult.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_create_ecg_ok():
    user = django_account_models.User.objects.create_user(
        "username", "password", False
    ).to_domain()
    lead_results = [
        {"lead": "I", "signal": [1, -1, 1]},
        {"lead": "II", "signal": [-1, 1, -1]},
    ]
    ecg_id = services.create_ecg(
        user, lead_results, unit_of_work.DjangoECGUnitOfWork()
    )
    assert django_ecg_models.ECG.objects.count() == 1
    assert django_ecg_models.ECGLeadResult.objects.count() == 2
    django_ecg = django_ecg_models.ECG.objects.get(id=ecg_id)
    assert django_ecg.creator_id == user.id
    assert django_ecg.ecgleadresult_set.filter(
        lead=ecg_model.ECGLead.I, signal=[1, -1, 1]
    ).exists()
    assert django_ecg.ecgleadresult_set.filter(
        lead=ecg_model.ECGLead.II, signal=[-1, 1, -1]
    ).exists()


@pytest.mark.django_db(transaction=True)
def test_process_ecg_ok():
    user = django_account_models.User.objects.create_user(
        "username", "password", False
    )
    django_ecg = django_ecg_models.ECG.objects.create(creator_id=user.id)
    django_ecg_lead_result_I = django_ecg_models.ECGLeadResult.objects.create(
        ecg_id=django_ecg.id,
        lead=ecg_model.ECGLead.I,
        signal=[1, -1, 1, -1],
    )
    django_ecg_lead_result_II = django_ecg_models.ECGLeadResult.objects.create(
        ecg_id=django_ecg.id,
        lead=ecg_model.ECGLead.II,
        signal=[1, 1, 1, -1],
    )
    ecg = django_ecg.to_domain()
    services.process_ecg(ecg, unit_of_work.DjangoECGUnitOfWork())
    django_ecg_lead_result_I.refresh_from_db()
    django_ecg_lead_result_II.refresh_from_db()
    assert django_ecg_lead_result_I.zero_crossing_count == 3
    assert django_ecg_lead_result_II.zero_crossing_count == 1


@pytest.mark.django_db
def test_get_ecg_by_id():
    django_user = django_account_models.User.objects.create_user(
        "username", "password", False
    )
    django_ecg = django_ecg_models.ECG.objects.create(creator_id=django_user.id)
    django_ecg_models.ECGLeadResult.objects.create(
        ecg_id=django_ecg.id,
        lead=ecg_model.ECGLead.I,
        signal=[1, -1, 1, -1],
    )
    assert django_ecg.to_domain() == services.get_ecg_by_id(
        django_ecg.id, repository.DjangoECGRepository()
    )


@pytest.mark.django_db
def test_get_ecg_by_id_not_found():
    assert services.get_ecg_by_id(1, repository.DjangoECGRepository()) is None

import random

from account.domain import model as account_model
from ecg.domain import model as ecg_model


def test_ecg_lead_result_calculate_zero_crossing_count():
    test_cases = [
        (0, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),
        (0, [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]),
        (1, [2, 2, 2, 2, 2, 2, 2, 2, 2, -2]),
        (1, [-3, 3, 3, 3, 3, 3, 3, 3, 3, 3]),
        (2, [-4, 4, 4, 4, 4, 4, 4, 4, 4, -4]),
        (9, [1, -2, 3, -4, 5, -6, 7, -8, 9, -9]),
    ]
    for expected_zero_crossing_count, signal in test_cases:
        ecg_lead_result = ecg_model.ECGLeadResult(
            lead=random.choice(list(ecg_model.ECGLead)),
            signal=signal,
        )
        ecg_lead_result.calculate_zero_crossing_count()
        assert ecg_lead_result.zero_crossing_count == expected_zero_crossing_count


def test_ecg_process():
    creator = account_model.User(username="test")
    ecg_lead_result_I = ecg_model.ECGLeadResult(
        lead=ecg_model.ECGLead.I,
        signal=[-1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    )
    ecg_lead_result_II = ecg_model.ECGLeadResult(
        lead=ecg_model.ECGLead.II,
        signal=[-1, 1, -1, 1, -1, 1, -1, 1, -1, 1],
    )
    ecg = ecg_model.ECG(
        creator=creator,
        lead_results=[ecg_lead_result_I, ecg_lead_result_II],
    )
    assert not ecg.is_processed()
    ecg.process()
    assert ecg.is_processed()
    assert ecg.lead_results[0].zero_crossing_count == 1
    assert ecg.lead_results[1].zero_crossing_count == 9


def test_ecg_stats_model_dump():
    creator = account_model.User(username="test")
    ecg_lead_result_I = ecg_model.ECGLeadResult(
        lead=ecg_model.ECGLead.I,
        signal=[-1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        zero_crossing_count=1,
    )
    ecg_lead_result_II = ecg_model.ECGLeadResult(
        lead=ecg_model.ECGLead.II,
        signal=[-1, 1, -1, 1, -1, 1, -1, 1, -1, 1],
        zero_crossing_count=9,
    )
    ecg = ecg_model.ECG(
        creator=creator,
        lead_results=[ecg_lead_result_I, ecg_lead_result_II],
    )
    assert ecg.stats_model_dump() == {
        "lead_results": [
            {"lead": "I", "zero_crossing_count": 1},
            {"lead": "II", "zero_crossing_count": 9},
        ],
    }

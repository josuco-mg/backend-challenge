from datetime import datetime
from enum import Enum
from typing import Optional

import numpy as np
from pydantic import BaseModel
from pydantic import field_validator

from account.domain import model as account_model


class ECGLead(str, Enum):
    I = "I"
    II = "II"
    III = "III"
    aVR = "aVR"
    aVL = "aVL"
    aVF = "aVF"
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V5 = "V5"
    V6 = "V6"


class ECG(BaseModel):
    id: Optional[int] = None
    creator: account_model.User
    created: Optional[datetime] = None
    lead_results: list["ECGLeadResult"]

    def is_processed(self) -> bool:
        return all(
            lead_result.zero_crossing_count is not None
            for lead_result in self.lead_results
        )

    def process(self):
        for lead_result in self.lead_results:
            lead_result.calculate_zero_crossing_count()

    def stats_model_dump(self) -> dict:
        return self.model_dump(
            include={"lead_results": {"__all__": {"lead", "zero_crossing_count"}}}
        )

    @field_validator("lead_results")
    @classmethod
    def validate_lead_results(
        cls, value: list["ECGLeadResult"]
    ) -> list["ECGLeadResult"]:
        if not value:
            raise ValueError("No lead results")
        if len(set(result.lead for result in value)) != len(value):
            raise ValueError("Duplicate lead results")
        return value


class ECGLeadResult(BaseModel):
    id: Optional[int] = None
    lead: ECGLead
    signal: list[int]
    num_samples: Optional[int] = None
    zero_crossing_count: Optional[int] = None

    def calculate_zero_crossing_count(self):
        self.zero_crossing_count = np.count_nonzero(np.diff(np.sign(self.signal)))

from pydantic import BaseModel
from datetime import date

class CallCenterResponse(BaseModel):
    result: bool
    status: str
    comment: str

class ManagerStatusResult(BaseModel):
    name: str
    shortnumber: int
    status: str
    ok: bool

class ActivationResponse(BaseModel):
    date: date
    results: list[ManagerStatusResult]
    not_in_schedule: list[str]

class ScheduleResponse(BaseModel):
    year: int
    month: int
    schedule: dict[str, list[str]]
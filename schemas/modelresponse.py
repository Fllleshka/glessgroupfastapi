from pydantic import BaseModel

class CallCenterResponse(BaseModel):
    result: bool
    status: str
    comment: str
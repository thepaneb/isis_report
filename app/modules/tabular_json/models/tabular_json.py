from pydantic import BaseModel
from robyn.types import JSONResponse


class MetaInfo(BaseModel):
    title: str
    sub_title: str | None = None
    company: str | None = None
    mode: str = "exact"


class ReportPayload(BaseModel):
    meta: MetaInfo
    layout: dict | None = None
    data: list


class ErrorResponse(JSONResponse):
    error: str

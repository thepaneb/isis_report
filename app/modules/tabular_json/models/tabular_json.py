"""Tabular JSON API request/response models."""
from pydantic import BaseModel
from robyn.types import JSONResponse


class MetaInfo(BaseModel):
    """Metadata information for the report."""
    title: str
    sub_title: str | None = None
    company: str | None = None
    mode: str = "exact"


class ReportPayload(BaseModel):
    """Report payload with metadata, optional layout, and data."""
    meta: MetaInfo
    layout: dict | None = None
    data: list


class ErrorResponse(JSONResponse):
    """Error response model."""
    error: str

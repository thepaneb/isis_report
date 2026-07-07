"""Tabular .toon API response models."""
from robyn.types import JSONResponse


class ErrorResponse(JSONResponse):
    """Error response model."""
    error: str

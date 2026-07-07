"""Status module API response models."""
from robyn.types import JSONResponse


class StatusResponse(JSONResponse):
    """Response model for healthy status."""
    status: str
    uptime: float | None = None


class StatusErrorResponse(JSONResponse):
    """Response model for unhealthy status."""
    status: str

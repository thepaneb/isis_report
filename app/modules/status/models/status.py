"""
Status response model.
"""

from typing import Optional

from robyn.types import JSONResponse


class StatusResponse(JSONResponse):
    """
    Response model for application status.
    """
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    status: str
    uptime: Optional[float] = None

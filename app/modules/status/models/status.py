from robyn.types import JSONResponse


class StatusResponse(JSONResponse):
    status: str
    uptime: float | None = None


class StatusErrorResponse(JSONResponse):
    status: str

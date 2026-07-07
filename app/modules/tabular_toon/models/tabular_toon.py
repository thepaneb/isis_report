from robyn.types import JSONResponse


class ErrorResponse(JSONResponse):
    error: str
